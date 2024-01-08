## 毕业设计
毕业设计: K8S容器网络测试和监控系统

### 使用说明
安装步骤如下
- 执行脚本`setup-env.sh`
- 执行脚本`setup-k8s.sh`
- 根据回显, 查看MongoDB的IP, 然后**手动修改MongoDB-ep.yaml中的IP**
- 执行脚本`setup-app.sh`
- (可选)部署nginx测试应用

### 脚本功能介绍
`setup-env.sh`安装kind(同时安装docker)
`setup-k8s.sh`部署集群/promethuse/grafana/MongoDB
`setup-app.sh`部署Agent/启动本地Server