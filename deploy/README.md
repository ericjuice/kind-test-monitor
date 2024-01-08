## 自动部署

### 使用说明
1. 执行 `./deploy.sh` 命令

必需修改项目:
- MongoDB-ep.yaml中的IP

可选修改项目:
- agent/daemon.yaml, 目前是默认总览. 若要精确到每个节点, 则需分别配置svc. 然后修改promethuse的configmap
- 其他

### 访问地址和端口映射说明
- Local-project:
    - Addr: 127.0.0.1:5678
- Grafana:
    - Addr: \<NodePort\>:30004
    - Svc(NodePort): 30004
    - Port: 3000
- Prometheus:
    - Addr: \<NodePort\>:30003
    - Svc(NodePort): 30003
    - Port: 9090
- Agent-collector:
    - Addr: \<NodePort\>:30002
    - Svc(NodePort): 30002
    - Port: 30002
- MongoDB-express:
    - Addr: 127.0.0.1:8081
    - Port: 8081
    - ContainerPort: 8081
- MongoDB:
    - Addr: 127.0.0.1:27017
    - Port: 27017
    - ContainerPort: 27017
- MongoDB-svc:
    - Svc(ClusterIP): mongodb-external:27017



### 流程解释
整个部署过程流程如下
- 安装kind(同时安装docker)
- kind启动集群
- 集群部署promethuse
- 集群部署grafana
- Docker部署MongoDB
- 查看MongoDB的IP
- **手动修改MongoDB-ep.yaml中的IP**
- 部署Agent
- Docker启动本地Server
- 打开前端页面使用
- (可选)部署nginx测试应用