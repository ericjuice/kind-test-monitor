package mytest

import (
	"bufio"
	"fmt"
	"os/exec"
	"strconv"
	"strings"
	"testing"
)

var sc = make(chan string, 10)

func Test_string(t *testing.T) {
	str := "529966 node         4  127.0.0.1        127.0.0.1        45243 0.07"
	words := strings.Fields(str)
	lastWord := words[len(words)-1]
	res, err := strconv.ParseFloat(lastWord, 64)
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println(res)
	}

}

func Test_exec(t *testing.T) {
	cmd := exec.Command("../src/tcpconnlat-bpfcc")

	// stdout pipe
	stdoutPipe, _ := cmd.StdoutPipe()

	_ = cmd.Start()

	// get stdout from pipe
	scanner := bufio.NewScanner(stdoutPipe)

	go func() {
		for scanner.Scan() {
			log := scanner.Text()
			// put log into channel
			sc <- log
		}
	}()

	// count tcp retransmits
	// if need log , use `for log := range outputQueue {}`
	for i := range sc {
		fmt.Print(i)
	}

	_ = cmd.Wait()
}
