import inspect
from datetime import datetime

class logger:
    def __init__(self):
        pass

    def info(self, msg):
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        now = datetime.now().strftime('%H:%M:%S')
        print("\033[32m")
        print(f"{now} {msg}\n[{filename}:{lineno}] ")
        print("\033[0m")

    def error(self, msg):
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        now = datetime.now().strftime('%H:%M:%S')
        print("\033[31m")
        print(f"{now} {msg}\n[{filename}:{lineno}] ")
        print("\033[0m")

    def warning(self, msg):
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        now = datetime.now().strftime('%H:%M:%S')
        print("\033[33m")
        print(f"{now} {msg}\n[{filename}:{lineno}] ")
        print("\033[0m")