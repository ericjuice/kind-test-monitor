#!/bin/bash

set -e

# 定义颜色的 ANSI 转义码
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # 恢复默认颜色

echo -e "${GREEN}正在下载并安装必备 apt 工具${NC}"
apt update
apt upgrade -y
apt install -y wget curl vim python3-pip python3
echo -e "${GREEN}apt 工具安装完成！${NC}"

# 检查 Docker 是否已经安装
if ! command -v docker &> /dev/null; then
    echo -e "${GREEN}Docker 未安装，开始安装 Docker...${NC}"

    # 安装 Docker
    curl -fsSL https://get.docker.com > get-docker.sh
    sudo sh get-docker.sh -s docker --mirror Aliyun

    # 添加当前用户到 docker 用户组
    sudo usermod -aG docker $USER

    echo -e "${GREEN}Docker 安装完成！请重新登录以使用户组更改生效。${NC}"
else
    echo -e "${GREEN}Docker 已安装。${NC}"
fi

# 下载并安装 kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${GREEN}正在下载并安装 kubectl...${NC}"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" || { echo -e "${RED}下载 kubectl 失败！${NC}"; exit 1; }
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl || { echo -e "${RED}安装 kubectl 失败！${NC}"; exit 1; }
    rm ./kubectl
    echo -e "${GREEN}kubectl 安装完成！${NC}"
else
    echo -e "${GREEN}kubectl 已安装。${NC}"
fi

# 下载并安装 kind
if ! command -v kind &> /dev/null; then
    echo -e "${GREEN}正在下载并安装 kind...${NC}"
    wget https://github.com/kubernetes-sigs/kind/releases/download/v0.19.0/kind-linux-amd64 || { echo -e "${RED}下载 kind 失败！${NC}"; exit 1; }
    chmod +x kind-linux-amd64 || { echo -e "${RED}修改 kind 权限失败！${NC}"; exit 1; }
    sudo mv kind-linux-amd64 /usr/local/bin/kind || { echo -e "${RED}安装 kind 失败！${NC}"; exit 1; }
    echo -e "${GREEN}kind 安装完成！${NC}"
else
    echo -e "${GREEN}kind 已安装。${NC}"
fi

echo -e "${GREEN}脚本执行完毕！${NC}"