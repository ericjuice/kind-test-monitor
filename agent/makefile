.PHONY: build

h:	
	@echo "Usage: make [target]"
	@echo "Target: h, run, r, test_on, test_off, test_m, build, clean, c, count"
	@echo "Function: "
	@echo "    h(default): help"
	@echo "    run/r: run go agent"
	@echo "    test-on: test on-cpu"
	@echo "    test-off: test off-cpu"
	@echo "    test-m: test prom-metrics"
	@echo "    build: build go agent into executable file"
	@echo "    clean/c: clean build files"
	@echo "    count: count go files"


count:
	find . -type f \( -name "*.go" -o -name "*.yaml" \) -exec wc -l {} +

r: run 
run:
	go run ./cmd/main.go 

test-on:
	curl localhost:30002/flameg?time=3\&freq=99\&type=on

test-off:
	curl localhost:30002/flameg?time=3\&freq=99\&type=off

test-m:
	curl localhost:30002/metrics | grep juice

build:
	go build -o build/agent.o ./cmd/main.go

c: clean
clean:
	rm ./build/*