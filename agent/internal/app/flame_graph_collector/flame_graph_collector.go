package flame_graph_collector

import (
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"

	fu "juice_agent/internal/app/file_uploader"
)

type Collector struct {
	savePath       string // path to save stack file
	offCpuFileName string
	onCpuFileName  string
	hostname       string
	isBusy         bool
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

	c.savePath = "./tmp/"
	c.offCpuFileName = "off_cpu.stack"
	c.onCpuFileName = "on_cpu.stack"
	c.isBusy = false
}

func (c *Collector) Start() {
	c.init()
}

func (c *Collector) SaveFlameStackToDB(w http.ResponseWriter, r *http.Request) {
	var f fu.FileUploader
	res := f.InsertFile2DB(c.savePath+c.onCpuFileName, "mongodb://mongodb-external:27017", "root", "root", "juice", "flame-stack", c.hostname)
	var ret string
	if res == 1 {
		ret = "success\n"
		log.Printf("insert %s to db success", c.savePath+c.onCpuFileName)
	} else {
		ret = "fail\n"
		log.Printf("insert %s to db fail", c.savePath+c.onCpuFileName)
	}
	w.Write([]byte(ret))
}

// get flamegraph and save to db
func (c *Collector) HandleFlameGraph(w http.ResponseWriter, r *http.Request) {
	log.Printf("handleFlameGraph, url: %s", r.RequestURI)

	// to avoid multiple requests concurrent
	if c.isBusy {
		log.Printf("Busy, url: %s", r.RequestURI)
		http.Error(w, "Busy", http.StatusBadRequest)
		return
	}

	c.isBusy = true
	defer func() {
		c.isBusy = false
	}()

	if r.URL.Path != "/flameg" {
		http.NotFound(w, r)
	}

	query := r.URL.Query()
	timeParam := query.Get("time")
	freqParam := query.Get("freq")
	onOffCpuType := query.Get("type")

	// limit
	time, err := strconv.Atoi(timeParam)
	if err != nil || time < 0 || time > 100 {
		http.Error(w, "Invalid time parameter", http.StatusBadRequest)
		return
	}

	freq, err := strconv.Atoi(freqParam)
	if err != nil || freq < 50 || freq > 200 {
		http.Error(w, "Invalid freq parameter", http.StatusBadRequest)
		return
	}

	if onOffCpuType != "on" && onOffCpuType != "off" {
		http.Error(w, "Invalid type parameter", http.StatusBadRequest)
		return
	}

	// select type
	var cmd *exec.Cmd
	var myFilePath string
	if onOffCpuType == "on" {
		cmd = exec.Command("python3", "./src/oncputime.py", "-af", timeParam, "-F", freqParam)
		myFilePath = c.savePath + c.onCpuFileName
	}
	if onOffCpuType == "off" {
		cmd = exec.Command("python3", "./src/offcputime.py", "-f", timeParam)
		myFilePath = c.savePath + c.offCpuFileName
	}

	// redirect stdout
	originalStdout := cmd.Stdout
	dirs := filepath.Dir(myFilePath)
	err = os.MkdirAll(dirs, os.ModePerm)
	if err != nil {
		log.Println("MkdirAll error: ", err)
		panic(err)
	}
	file, err := os.OpenFile(myFilePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		log.Println("OpenFile error: ", err)
		http.Error(w, err.Error()+".Open file error .Please try again", http.StatusInternalServerError)
		return
	}
	defer file.Close()
	cmd.Stdout = file

	err = cmd.Run()
	if err != nil {
		log.Println("Run error: ", err)
		http.Error(w, err.Error()+".Run error .Please try again", http.StatusInternalServerError)
		return
	}

	// recover Stdout
	cmd.Stdout = originalStdout
	cmd.Stderr = os.Stderr

	res := "cmd: " + cmd.String() + " executed successfully\n"
	log.Println(res)

	c.SaveFlameStackToDB(w, r)
}
