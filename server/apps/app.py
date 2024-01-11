from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import os
from apps.logger import logger
from apps.kube import KubeOperator


class Routers():
    def __init__(self):
        # define flask app config
        self.app = Flask(__name__)
        self.app_socketio = SocketIO(self.app)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.app.template_folder = os.getcwd() + '/templates'
        self.app.static_folder = os.getcwd() + '/static'

        # define app route
        self.app.route("/")(self.handle_index)
        self.app.route("/exec_cmd_by_post",
                       methods=['POST'])(self.handle_exec_cmd_by_post)

        # define socketio event
        self.app_socketio.on_event('connect', self.test_connect)
        self.app_socketio.on_event('reconnect', self.test_reconnect)
        self.app_socketio.on_event(
            'exec_test_command', self.handle_exec_test_cmd)
        self.app_socketio.on_event(
            'exec_gen_flame', self.handle_gen_flame_graph)

        # self helper
        self.__host_operator = HostOperator()
        self.__logger = logger()
        self.__logger.info('Routers inited.')

    def handle_index(self):
        # index page
        note = 'Greetings!'
        return render_template('index.html', note_info=note)

    def test_connect(self):
        self.__logger.info('Connect ok')
        emit('connection_response', 1)


    def test_reconnect(self):
        self.__logger.warning('reconnecting')
        emit('connection_response', 1)

    def handle_exec_cmd_by_post(self):
        # execute command through post
        command = request.form['command']
        if command == '':
            return
        return self.__host_operator.exec_cmd_on_host(command)

    def handle_exec_test_cmd(self, data: dict):
        # 1. read args and handlie it to host operator.
        # 2. when it is ready, return msg
        # TODO
        try:
            threads = data['thread']
            qps = data['qps']
            time = data['time']
            addr = data['addr']
        except Exception as e:
            self.__logger.error(e)
            emit('err_msg', {'data': 'Invalid args'})
        self.__logger.info(
            f'Handle exec test command: threads={threads}&qps={qps}&time={time}&addr={addr}')
        emit('test_ok', {'data': '正在执行...'})
        pass

    def handle_gen_flame_graph(self, data: dict):
        # generate flame graph
        # 1. read command args and handle it to HostOperator.exec_gen_flame()
        # 3. return the message that host operator is working (websocket)
        # 4. when the flame graph is ready, return msg(websocket)
        # TODO
        try:
            type = data['type']
            time = data['time']
            hz = data['hz']
            args = [type, time, hz]
        except Exception as e:
            self.__logger.error(e)
            emit('err_msg', {'data': 'Invalid args'})

        self.__logger.info(
            f'Handle gen flame graph: type={args[0]}&time={args[1]}&hz={args[2]}')
        emit('flame_ok', {'data': '正在执行...'})
        pass

    def run(self):
        self.app_socketio.run(self.app, host='0.0.0.0', port=5678)


class HostOperator():
    def __init__(self):
        self.__logger = logger()
        self.__kube_operator = KubeOperator()

    def exec_gen_flame(self, type, port, time, freq):
        # Handle flame graph
        # 1. notify kube operator to generate flame(through pods)
        # 2. when ready. call self.fetch_data_and_gen_flame_from_db()
        # 4. return the message that job has done
        # TODO
        pass

    def exec_test_cmd_on_host(self, threads, qps, time, addr) -> str:
        # fortio load -c <threads> -qps <qps> -t <time> http://<ip>:<port>/
        # 1. exec test command
        # 2. return the message that job is working
        # 3. when done, return the message(websocket) that job is done
        try:
            cmd = f'tools/fortio load -c {threads} -qps {qps} -t {time}s {addr}'
            self.__logger.info('exec command: ' + cmd)
            result = subprocess.check_output(
                cmd, shell=True)
            cmd_result = result.decode("utf-8")
            self.__logger.info('exec result: ' + cmd_result)
        except subprocess.CalledProcessError as e:
            cmd_result = "Test command execution failed: " + str(e)
            self.__logger.error(cmd_result)

        return cmd_result

    def fetch_data_and_gen_flame_from_db(self):
        # fetch data from mongo db and gen flame. save to static dir
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
