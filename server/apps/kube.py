from kubernetes import client, config
import subprocess
import threading
from apps.logger import logger


class KubeOperator:
    # Kubernetes command operator
    def __init__(self):
        config.load_kube_config()
        self.__api_handler = client.CoreV1Api()
        self.__pod_ips = []
        self.__node_names = []
        self.__master_node_name = ''
        self.__logger = logger()
        self.get_master_name()
        self.get_pods_ip_and_nodes_name('juice', 'app=juice-collector')

    def return_node_names(self) -> list:
        return self.__node_names

    def get_pods_ip_and_nodes_name(self, namespace, label_selector):
        self.__pod_ips = []
        self.__node_names = []
        try:
            pod_list = self.__api_handler.list_namespaced_pod(
                namespace=namespace, label_selector=label_selector)
        except Exception as e:
            self.__logger.error(e)

        for pod in pod_list.items:
            node_name = pod.spec.node_name
            self.__node_names.append(node_name)
            pod_ip = pod.status.pod_ip
            self.__pod_ips.append(pod_ip)
        self.__logger.info('Get pods ip and nodes name ok')
        # for pod_ip in self.__pod_ips:
        #     self.__logger.info('Pod ip: ' + pod_ip)

        # for node_name in self.__node_names:
        #     self.__logger.info('Node name: ' + node_name)

    def get_master_name(self):
        nodes = self.__api_handler.list_node().items
        for node in nodes:
            if 'node-role.kubernetes.io/control-plane' in node.metadata.labels:
                self.__master_node_name = node.metadata.name
                break

        if self.__master_node_name == '':
            self.__logger.error('Can not get master node name.')
        else:
            self.__logger.info('Master node name: ' + self.__master_node_name)

    def exec_flame_genarate(self, type, port, time, freq) -> bool:
        # exec flame genarating , the pods will save it to mongodb
        # get master node name, and get into it, and exec command to get flame
        # eg: docker exec <master_node_name> curl localhost:30002/flameg?time=3\&freq=99\&type=on
        if self.__node_names == []:
            self.__logger.error('No pods found.')
            return False
        if type != 'on' and type != 'off':
            self.__logger.error('Invalid type: ' + type)
            return False

        # subfunction to exec
        def execute_command(command):
            try:
                self.__logger.info('exec command: ' + command)
                result = subprocess.check_output(command, shell=True)
                cmd_result = result.decode("utf-8")
                self.__logger.info('exec result: ' + cmd_result)
            except subprocess.CalledProcessError as e:
                cmd_result = "Command execution failed: " + str(e)
                self.__logger.error(cmd_result)

        threads = []
        for i in range(len(self.__pod_ips)):
            command = f'docker exec {self.__master_node_name} curl {self.__pod_ips[i]}:{port}/flameg?time={time}\&freq={freq}\&type={type}'
            thread = threading.Thread(target=execute_command, args=(command,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            self.__logger.info('Joining thread: ' + thread.name)
            thread.join()

        return True
