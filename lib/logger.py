

class LogLevel:
    debug=0
    info=1
    warn=2
    error=3
    fatal=4
    nolog=5

class Logger:
    loglevel=LogLevel.info
    @staticmethod
    def info(context:str):
        global loglevel
        print('\033[0m'+context) if loglevel<=LogLevel.info else None
    @staticmethod
    def debug(context:str):
        global loglevel
        print('\033[0;34m'+context+'\033[0m') if loglevel<=LogLevel.debug else None
    @staticmethod
    def warn(context:str):
        global loglevel
        print('\033[0;1;33m'+context+'\033[0m') if loglevel<=LogLevel.warn else None
    @staticmethod
    def error(context:str):
        global loglevel
        print('\033[0;1;31m'+context+'\033[0m') if loglevel<=LogLevel.error else None
    @staticmethod
    def fatal(context:str):
        global loglevel
        print('\033[0;1;41;37m'+context+'\033[0m') if loglevel<=LogLevel.fatal else None