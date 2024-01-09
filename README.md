## 毕业设计
毕业设计: 一站式K8S容器网络测试和监控系统

### 使用说明
安装步骤如下
- 进入deploy目录
- 执行脚本`setup-env.sh`
- 执行脚本`setup-k8s.sh`
- Grafana可视化: 根据提示进入Grafana. 根据提示添加data source地址. 之后创建模板并选择指标即可
- 进入server目录
- 手动启动本地Server`python3 main.py`
- (可选)部署nginx测试应用:进入deploy目录
- (可选)执行脚本`setup-nginx-deploy.sh`

### 脚本功能介绍
`setup-env.sh`安装kind等环境
`setup-k8s.sh`部署集群/promethuse/grafana/MongoDB/Agent, 并使用nginx转发端口到外部
`setup-nginx-deploy.sh`部署nginx集群测试应用