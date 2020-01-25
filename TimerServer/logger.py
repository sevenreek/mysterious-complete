from CONFIGURATION import CFG_LOGS_DIR, CFG_LOGS_DATE_FORMAT, CFG_LOGS_DAYS_ARCHIVE_SIZE, CFG_LOGS_TIME_FORMAT
import os, sys
import datetime
class Logger():
    instance = None
    def __init__(self, logsDir, archiveSizeDays):
        self.scriptDirectory = os.path.dirname(os.path.realpath(__file__))
        print(self.scriptDirectory)
        self.logsDirectory = self.scriptDirectory + '/' + logsDir
        print(self.logsDirectory)
        if not os.path.exists(self.logsDirectory):
            try:
                os.makedirs(self.logsDirectory)
            except PermissionError as e:
                print(str(e))
        self.cleanLogsDirectory(self.logsDirectory, archiveSizeDays)
    def cleanLogsDirectory(self, dir, olderThanDays, dateFrom = datetime.date.today()):
        files = os.listdir(dir)
        print(files)
        for file in files:
            try:
                date = datetime.datetime.strptime(file, CFG_LOGS_DATE_FORMAT).date()
                if((dateFrom - date).days > olderThanDays):
                    os.remove(dir + '/' + file)
                    self.log('Removing log file ' + file + '.')
            except Exception as e:
                self.log("Arrived at an unexpected file in /logs or file could not be removed.")
                self.log(e)
    def log(self, msg):
        try:
            with open(self.logsDirectory + '/' + datetime.date.today().strftime(CFG_LOGS_DATE_FORMAT),"a+") as f:
                f.write(datetime.datetime.now().strftime(CFG_LOGS_TIME_FORMAT) + str(msg) + '\n')
        except PermissionError as e:
            print(str(e))
    @staticmethod
    def glog(msg): # global log
        if(Logger.instance is not None):
            Logger.instance.log(msg)
    def makeGlobal(self):
        Logger.instance = self
if __name__ == "__main__":
    l = Logger(CFG_LOGS_DIR, CFG_LOGS_DAYS_ARCHIVE_SIZE)
    l.log("Running logger test.")
    l.makeGlobal()
    Logger.glog("Running global logger test.")