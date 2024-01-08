package ebpf_tcp_collector

import (
	"bufio"
	"log"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type Collector struct {
	hostname                 string           // hostname to identify nodes
	tcpRetransmitGauge       prometheus.Gauge // current number of tcp retransmits
	tcpAveConnlatGauge       prometheus.Gauge // latest 5s average tcp connlat (ms)
	tcpRretransmitOutputChan chan string      // chan to collect tcp retransmits
	tcpConnlatOutputChan     chan string      // chan to collect tcp connlat
}

func (c *Collector) init() {
	nodeName := os.Getenv("JUICE_NODE_NAME")
	// it is better the node name, on default it is pod's hostname
	if nodeName != "" {
		c.hostname = nodeName
	} else {
		c.hostname, _ = os.Hostname()
		c.hostname = "pod_" + c.hostname
	}
	reg := regexp.MustCompile(`[^a-zA-Z0-9_]`)
	// prometheus metric name should not contain special characters
	c.hostname = reg.ReplaceAllString(c.hostname, "_")

	c.tcpRetransmitGauge = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "juice_" + c.hostname + "_collector_tcp_retransmits_count",
		Help: "The current number of tcp retransmits",
	})
	c.tcpAveConnlatGauge = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "juice_" + c.hostname + "_collector_tcp_connlat_5s_ave",
		Help: "The latest 5s average tcp connlat (ms)",
	})
	c.tcpRretransmitOutputChan = make(chan string, 100)
	c.tcpConnlatOutputChan = make(chan string, 100)
}

// transform handler to prom http handler
func (c *Collector) HandleMetrics(w http.ResponseWriter, r *http.Request) {
	log.Printf("handleMetrics, url: %s", r.RequestURI)
	promHandler := promhttp.Handler()
	promHandler.ServeHTTP(w, r)
}

// execute ebpf and collect metrics
func (c *Collector) recordMetrics() {
	c.tcpRetransmitGauge.Set(0)
	go c.exeTcpRetransmit()

	var tcpCount int
	var tcpTotalTime float64
	tcpCount = 0
	tcpTotalTime = 0
	c.tcpAveConnlatGauge.Set(0)
	go c.exeTcpConnlat(&tcpCount, &tcpTotalTime)

	// clear metrics per 60m, to avoid gauge overflow
	go func() {
		for {
			time.Sleep(60 * 60 * time.Second)
			c.tcpRetransmitGauge.Set(0)
		}
	}()

	go func() {
		for {
			time.Sleep(5 * time.Second)
			if tcpCount == 0 || tcpTotalTime == 0 {
				continue
			} else {
				c.tcpAveConnlatGauge.Set(tcpTotalTime / float64(tcpCount))
			}
			// log.Printf("tcpAveConnlatGauge: %f", tcpTotalTime/float64(tcpCount))
			// log.Printf("tcpCount: %d", tcpCount)
			// log.Printf("tcpTotalTime: %f", tcpTotalTime)
			tcpCount = 0
			tcpTotalTime = 0
		}
	}()

}

func (c *Collector) exeTcpConnlat(tcpCount *int, tcpTotalTime *float64) {
	log.Printf("start collect tcp connlat\n")
	cmd := exec.Command("python3", "./src/tcpconnlat.py")
	log.Print(cmd.String())

	// stdout pipe
	stdoutPipe, err := cmd.StdoutPipe()
	if err != nil {
		log.Fatal(err)
	}

	_ = cmd.Start()

	// get stdout from pipe
	scanner := bufio.NewScanner(stdoutPipe)

	go func() {
		for scanner.Scan() {
			log := scanner.Text()
			// put log into channel
			c.tcpConnlatOutputChan <- log
		}
	}()

	// count tcp connlat
	for line := range c.tcpConnlatOutputChan {
		words := strings.Fields(line)
		lastWord := words[len(words)-1]
		res, err := strconv.ParseFloat(lastWord, 64)
		if err != nil {
			log.Printf("ParseFloat error: %v", err)
		} else {
			*tcpTotalTime += res
			*tcpCount += 1
		}
	}

	_ = cmd.Wait()
}

func (c *Collector) exeTcpRetransmit() {
	log.Printf("start collect tcp retransmits\n")
	cmd := exec.Command("python3", "./src/tcpretran.py")
	log.Print(cmd.String())

	// stdout pipe
	stdoutPipe, _ := cmd.StdoutPipe()

	_ = cmd.Start()

	// get stdout from pipe
	scanner := bufio.NewScanner(stdoutPipe)

	go func() {
		for scanner.Scan() {
			log := scanner.Text()
			// put log into channel
			c.tcpRretransmitOutputChan <- log
		}
	}()

	// count tcp retransmits
	// if need log , use `for log := range outputQueue {}`
	for range c.tcpRretransmitOutputChan {
		c.tcpRetransmitGauge.Add(1)
	}

	_ = cmd.Wait()
}

func (c *Collector) Start() {
	c.init()
	c.recordMetrics()
}
