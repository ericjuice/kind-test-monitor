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
        self.app.route("/")(self.index)
        self.app.route("/hello")(self.hello)
        self.app.route("/exec_cmd_by_post",
                       methods=['POST'])(self.exec_cmd_by_post)
        self.app.template_folder = os.getcwd() + '/templates'
        self.app.static_folder = os.getcwd() + '/static'
        self.__host_operator = HostOperator()
        self.__logger = logger()
        self.__logger.info('Routers inited.')

    # index page
    def index(self):
        note = 'Greetings!'
        return render_template('index.html', note_info=note)

    # to test program's status
    def hello(self):
        return "Hello world.\n"

    # execute command through post
    def exec_cmd_by_post(self):
        command = request.form['command']
        if command == '':
            return

        return self.__host_operator.exec_cmd_on_host(command)

    def echo_info(self):
        pass

    def run(self):
        self.app.run(host='0.0.0.0', port=5678)


class HostOperator():
    def __init__(self):
        self.__logger = logger()
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

