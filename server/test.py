import unittest
from apps.kube import KubeOperator
from apps.app import HostOperator
from apps.logger import logger
import warnings



class TestKubeOperator(unittest.TestCase):
    # eg: python3 -m unittest test.TestKubeOperator.test_get_pods_ip_and_nodes_name
    def test_get_pods_ip_and_nodes_name(self):
        # to avoid the stupid warning
        warnings.filterwarnings("ignore", category=ResourceWarning)
        k = KubeOperator()
        k.get_pods_ip_and_nodes_name('juice', 'app=juice-collector',)

    # eg: python3 -m unittest test.TestKubeOperator.test_get_master_name
    def test_get_master_name(self):
        # to avoid the stupid warning
        warnings.filterwarnings("ignore", category=ResourceWarning)
        k = KubeOperator()
        k.get_master_name()

    # eg: python3 -m unittest test.TestKubeOperator.test_exec_flame_genarate
    def test_exec_flame_genarate(self):
        # to avoid the stupid warning
        warnings.filterwarnings("ignore", category=ResourceWarning)
        k = KubeOperator()
        k.get_pods_ip_and_nodes_name('juice', 'app=juice-collector',)
        k.get_master_name()
        k.exec_flame_genarate('on', 30002, 3, 99)

class TestHostOperator(unittest.TestCase):
    # eg: python3 -m unittest test.TestHostOperator.test_exec_cmd_on_host
    def test_exec_cmd_on_host(self):
        h = HostOperator()
        h.exec_cmd_on_host('ls')

    # eg: python3 -m unittest test.TestHostOperator.test_exec_test_cmd_on_host
    def test_exec_test_cmd_on_host(self):
        h = HostOperator()
        h.exec_test_cmd_on_host(10, 10, 3, True, 'juis.top', 443)

class TestLogger(unittest.TestCase):
    # eg: python3 -m unittest test.TestLogger.test_logger
    def test_logger(self):
        l = logger()
        l.info('test info')
        l.error('test error')
        l.warning('test warning')


if __name__ == '__main__':
    print("Please use single test")

    # deprecated kube exec pod
    # def execute_command_on_pod(self, pod_name, namespace, command):
    #     try:
    #         # request
    #         exec_command = [
    #             '/bin/sh',
    #             '-c',
    #             command
    #         ]
    #         # exec and get res
    #         resp = stream(self.__api_handler.connect_get_namespaced_pod_exec, pod_name, namespace,
    #                       command=exec_command,
    #                       stderr=True, stdin=False,
    #                       stdout=True, tty=False)
            
    #         # output
    #         print(f"Pod: {pod_name}")
    #         print(resp)

    #     except Exception as e:
    #         print(f"Error: {e}")