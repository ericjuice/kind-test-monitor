#!/bin/bash

set -e

# 定义颜色的 ANSI 转义码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 恢复默认颜色


# 创建k8s
echo -e "${GREEN}启动kind集群${NC}"
echo -e "${GREEN}正在拉取kind节点镜像${NC}"
docker pull kindest/node:v1.21.14 || { echo -e "${RED}拉取kind节点镜像失败！${NC}"; exit 1; }
kind create cluster --config ./kindtest/config.yaml || { echo -e "${RED}创建kind集群失败！${NC}"; exit 1; }
echo -e "${GREEN}kind集群创建完成！${NC}"

# 部署应用
echo -e "${GREEN}正在安装prometheus和grafana${NC}"
kubectl get ns juice || kubectl create ns juice || { echo -e "${RED}创建juice命名空间失败！${NC}"; exit 1; }
kubectl apply -f ./k8s-prometheus-grafana/node-exporter.yaml || { echo -e "${RED}安装node-exporter失败！${NC}"; exit 1; }
kubectl apply -f ./k8s-prometheus-grafana/prometheus/rbac-setup.yaml || { echo -e "${RED}安装prometheus/rbac失败！${NC}"; exit 1; }
kubectl apply -f ./k8s-prometheus-grafana/prometheus/configmap.yaml || { echo -e "${RED}安装prometheus/configmap失败！${NC}"; exit 1; }
kubectl apply -f ./k8s-prometheus-grafana/prometheus/prometheus.yaml || { echo -e "${RED}安装prometheus/prometheus失败！${NC}"; exit 1; }
kubectl apply -f ./k8s-prometheus-grafana/grafana/grafana.yaml || { echo -e "${RED}grafana安装失败！${NC}"; exit 1; }

echo -e "${GREEN}prometheus和grafana安装完成！${NC}"


# MongoDB
# mongoDB compose
docker compose -f ./server/mongodb-compose.yaml up -d || { echo -e "${RED}启动mongoDB失败！${NC}"; exit 1; }
# 获取mongoDB ip
mongo_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' juice-mongodb) || { echo -e "${RED}获取mongo ip失败！${NC}"; exit 1; }
# 设置mongoDB svc-endpoint IP
sed -i "s/\(.*ip:.*# OuterIP\)/      - ip: $mongo_ip # OuterIP/" ./server/mongo-ep-svc.yaml || { echo -e "${RED}设置mongo svc-endpoint ip失败！${NC}"; exit 1; }
# 设置mongoDB svc-endpoint
kubectl apply -f ./server/mongo-ep-svc.yaml || { echo -e "${RED}设置mongo svc-endpoint失败！${NC}"; exit 1; }

# 暴露到外面
echo -e "${GREEN}正在设置端口转发${NC}"
# 获取容器和主机的 IP 地址
kind_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-worker) || { echo -e "${RED}获取kind ip失败！${NC}"; exit 1; }
host_ip=$(hostname -I | awk '{print $1}')

# 设置nginx端口转发
# 修改Nginx文件         default 192.168.0.100; # NodePortIP
sed -i "s/\(.*default.*# NodePortIP\)/        default $kind_ip; # NodePortIP/" ./nginx/conf/nginx.conf || { echo -e "${RED}修改nginx conf失败！${NC}"; exit 1; }
# 启动Nginx
docker compose -f ./nginx/nginx-compose.yaml up -d || { echo -e "${RED}启动nginx失败！${NC}"; exit 1; }
echo -e "${GREEN}Nginx端口转发设置完成！${NC}"


# 启动agent
kubectl apply -f ./agent/daemon.yaml || { echo -e "${RED}启动agent失败！${NC}"; exit 1; }

# ok
echo -e "${GREEN}安装完成！你的prometheus数据源地址为${RED}$kind_ip${NC}"
echo -e "${YELLOW}系统内部访问地址如下${NC}"
echo -e "${GREEN}Grafana: http://$kind_ip:30004$ 默认密码:admin:admin${NC}"
echo -e "${GREEN}Prometheus: http://$kind_ip:30003${NC}"
echo -e "${GREEN}MongoExpress: http://$kind_ip:8081$ 默认密码:root:root${NC}"
echo -e "${GREEN}Nginx: http://$kind_ip:80${NC}"
echo -e "${YELLOW}系统外部访问地址如下${NC}"
echo -e "${GREEN}Grafana: http://$host_ip:30004$ 默认密码:admin:admin{NC}"
echo -e "${GREEN}Prometheus: http://$host_ip:30003${NC}"
echo -e "${GREEN}MongoExpress: http://$host_ip:8081$ 默认密码:root:root{NC}"
echo -e "${GREEN}Nginx: http://$host_ip:80${NC}"