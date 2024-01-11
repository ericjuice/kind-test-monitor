from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import os
import json
import re
import pymongo
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

        # variables to control the job status
        self.__test_busy = False
        self.__exec_busy = False
        self.__flame_busy = False

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
        if self.__exec_busy:
            return '后台忙碌中...'
        self.__exec_busy = True
        command = request.form['command']
        if command == '':
            return
        res = self.__host_operator.exec_cmd_on_host(command)
        self.__exec_busy = False
        return res

    def handle_exec_test_cmd(self, data: dict):
        # 1. read args and handlie it to host operator.
        # 2. when it is ready, return msg
        if self.__test_busy:
            emit('err_msg', {'data': '后台忙碌中...'})
            return
        self.__test_busy = True
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
        res = self.__host_operator.exec_test_cmd_on_host(
            threads, qps, time, addr)
        self.__test_busy = False
        self.__logger.info('Exec test command ok')
        emit('test_ok', {'data': res})
        pass

    def handle_gen_flame_graph(self, data: dict):
        # generate flame graph
        # 1. read command args and handle it to HostOperator.exec_gen_flame()
        # 2. return the message that host operator is working (websocket)
        # 3. when the flame graph is ready, return nodes names(websocket)
        if self.__flame_busy:
            emit('err_msg', {'data': '后台忙碌中...'})
            return
        self.__flame_busy = True

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
        # 0 presents unfinished
        emit('flame_ok', {'data': '正在执行...', 'ctr': 0})
        res = self.__host_operator.exec_gen_flame(type, 30002, time, hz)
        if res == []:
            emit('flame_ok', {'data': '无数据', 'ctr': 0})
            return
        json_res = json.dumps(res)
        # 1 presents finished
        self.__flame_busy = False
        emit('flame_ok', {'data': json_res, 'ctr': 1})

    def run(self):
        self.app_socketio.run(self.app, host='0.0.0.0', port=5678)


class HostOperator():
    def __init__(self):
        self.__logger = logger()
        self.__kube_operator = KubeOperator()

    def exec_gen_flame(self, type, port, time, hz) -> list:
        # Handle flame graph
        # 1. notify kube operator to generate flame(through pods)
        # 2. when ready. call self.fetch_data_and_gen_flame_from_db()
        # 3. return the message that job has done
        self.__kube_operator.exec_flame_genarate(type, port, time, hz)
        return self.fetch_data_and_gen_flame_from_db()

    def exec_test_cmd_on_host(self, threads, qps, time, addr) -> str:
        # fortio load -c <threads> -qps <qps> -t <time> http://<ip>:<port>/
        # 1. exec test command
        # 2. when done, return the message that job is done
        try:
            cmd = f'tools/fortio load -c {threads} -qps {qps} -t {time}s {addr}'
            self.__logger.info('exec command: ' + cmd)
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cmd_result = result.stdout.decode("utf-8")

            # extract last 17 lines info from cmd_result
            lines = cmd_result.splitlines()
            if len(lines) <= 17:
                pass
            else:
                cmd_result = lines[-17:]
                cmd_result = '\n'.join(cmd_result)

            self.__logger.info('exec result(extracted): ' + cmd_result)
        except subprocess.CalledProcessError as e:
            cmd_result = "Test command execution failed: " + str(e)
            self.__logger.error(cmd_result)

        return cmd_result

    def fetch_data_and_gen_flame_from_db(self) -> list:
        # fetch data from mongo db and gen flame. save to static dir
        names = self.__kube_operator.return_node_names()
        # name dont have special characters
        new_names = []
        for name in names:
            reg = re.compile(r'[^a-zA-Z0-9_]')
            name = reg.sub('_', name)
            new_names.append(name)
        names = new_names
        client = pymongo.MongoClient("mongodb://root:root@localhost:27017")
        db = client["juice"]
        collection = db["flame-stack"]
    
        for name in names:
            # find the latest data for each node, save to stack file
            try:

                query = {"hostName": name}
                result = collection.find(query).sort("_id", pymongo.DESCENDING).limit(1)
                if collection.count_documents(query) > 0:
                    content = result[0]["content"]
                    file_path = f"./static/{name}.stack"
                    with open(file_path, "w") as file:
                        file.write(content.decode('utf-8'))
                        self.__logger.info(f"Flame graph saved to {file_path}")
                else:
                    self.__logger.warning(f"No data found for node {name}")
            except Exception as e:
                self.__logger.error(e)

        for name in names:
            # convert the stack file to flame image
            stack_path = f"./static/{name}.stack"
            image_path = f"./static/{name}.svg"
            if os.path.exists(stack_path):
                try:
                    self.__logger.info(f"Converting {stack_path} to {image_path}")
                    result = subprocess.run(
                        f"tools/flamegraph.pl --color=java < {stack_path} > {image_path}",shell=True
                    )
                except subprocess.CalledProcessError as e:
                    self.__logger.error(e)
            else:
                self.__logger.error(f"No stack file found for node {name}")
        self.__logger.info('Fetch data and gen flame ok')

        return names

    def exec_cmd_on_host(self, command) -> str:
        try:
            self.__logger.info('exec command: ' + command)
            result = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cmd_result = result.stdout.decode("utf-8")
            self.__logger.info('exec result: ' + cmd_result)
        except subprocess.CalledProcessError as e:
            self.__logger.error(e)

        return cmd_result
