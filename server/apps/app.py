from flask import Flask
from flask import render_template
from flask import request
import subprocess
import os
from apps.logger import logger
from apps.kube import KubeOperator


class Routers():
    def __init__(self):
        self.app = Flask(__name__)
        self.app.route("/")(self.handle_index)
        self.app.route("/hello")(self.handle_hello)
        self.app.route("/exec_cmd_by_post",
                       methods=['POST'])(self.handle_exec_cmd_by_post)
        self.app.template_folder = os.getcwd() + '/templates'
        self.app.static_folder = os.getcwd() + '/static'
        self.__host_operator = HostOperator()
        self.__logger = logger()
        self.__logger.info('Routers inited.')

    def handle_index(self):
        # index page
        note = 'Greetings!'
        return render_template('index.html', note_info=note)

    def handle_hello(self):
        # to test program's status
        return "Hello world.\n"

    def handle_exec_cmd_by_post(self):
        # execute command through post
        command = request.form['command']
        if command == '':
            return

        return self.__host_operator.exec_cmd_on_host(command)

    def handle_gen_flame_graph(self):
        # generate flame graph
        # 1. read command arguments through post
        # 2. handle it to host operator to gen flame graph
        # 3. return the message that host operator is working
        # TODO
        pass

    def run(self):
        self.app.run(host='0.0.0.0', port=5678)


class HostOperator():
    def __init__(self):
        self.__logger = logger()
        self.__kube_operator = KubeOperator()

    def gen_flame(self, type, port, time, freq):
        # Handle flame graph
        # 1. notify kube operator to generate flame(through pods)
        # 2. read datas from mongodb
        # 3. generate flame graph through perl
        # 4. return flame graph to front end(websocket), meanwhile return the message that job has done
        # TODO
        pass

    def exec_cmd_on_host(self, command) -> str:
        try:
            self.__logger.info('exec command: ' + command)
            result = subprocess.check_output(command, shell=True)
            cmd_result = result.decode("utf-8")
            self.__logger.info('exec result: ' + cmd_result)
        except subprocess.CalledProcessError as e:
            self.__logger.error(e)

        return cmd_result

    def exec_test_cmd_on_host(self, threads, qps, time, is_https: bool, ip, port) -> str:
        # fortio load -c <threads> -qps <qps> -t <time> http://<ip>:<port>/
        # 1. exec test command
        # 2. return the message that job is working
        # 3. when done, return the message(websocket) that job is done
        http_type = 'https' if is_https else 'http'
        try:
            cmd = f'tools/fortio load -c {threads} -qps {qps} -t {time}s {http_type}://{ip}:{port}/'
            self.__logger.info('exec command: ' + cmd)
            result = subprocess.check_output(
                cmd, shell=True)
            cmd_result = result.decode("utf-8")
            self.__logger.info('exec result: ' + cmd_result)
        except subprocess.CalledProcessError as e:
            cmd_result = "Test command execution failed: " + str(e)
            self.__logger.error(cmd_result)

        return cmd_result
