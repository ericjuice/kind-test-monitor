#!/bin/bash

set -e

# 定义颜色的 ANSI 转义码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${GREEN}正在部署nginx${NC}"
kubectl apply -f ./nginx/nginx-dep.yaml || { echo -e "${RED}部署nginx失败！${NC}"; exit 1; }
echo -e "${GREEN}nginx部署完成！${NC}"