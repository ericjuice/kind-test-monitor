/*
This file is the entry point of the agent

Author: Juice

Date: 2023/12/29
*/
package main

import (
	etc "juice_agent/internal/app/ebpf_tcp_collector"
	fg "juice_agent/internal/app/flame_graph_collector"
	"log"
	"net/http"
)

func main() {
	var c etc.Collector
	var f fg.Collector
	c.Start()
	f.Start()
	http.HandleFunc("/metrics", c.HandleMetrics)
	http.HandleFunc("/flameg", f.HandleFlameGraph)
	// http.HandleFunc("/savef", f.SaveFlameStackToDB)

	log.Println("Started")
	log.Println("Listening on port 30002...")
	log.Fatal(http.ListenAndServe(":30002", nil))

}
