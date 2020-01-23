CFG_LOGS_DIR = 'logs'
CFG_LOGS_DATE_FORMAT = '%Y-%m-%d'
CFG_LOGS_TIME_FORMAT = '[%H:%M:%S] '
CFG_LOGS_DAYS_ARCHIVE_SIZE = 7
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
            os.makedirs(self.logsDirectory)
        self.cleanLogsDirectory(self.logsDirectory, archiveSizeDays)
    def cleanLogsDirectory(self, dir, olderThanDays, dateFrom = datetime.date.today()):
        files = os.listdir(dir)
        print(files)
        for file in files:
            try:
                date = datetime.datetime.strptime(file, CFG_LOGS_DATE_FORMAT).date()
                if((dateFrom - date).days > olderThanDays):
                    os.remove(dir + '/' + file)
                    self.log('Removing log file from' + file + '.')
            except:
                self.log("Arrived at an unexpected file in /logs or file could not be removed.")
    def log(self, msg):
        with open(self.logsDirectory + '/' + datetime.date.today().strftime(CFG_LOGS_DATE_FORMAT),"a+") as f:
            f.write(datetime.datetime.now().strftime(CFG_LOGS_TIME_FORMAT) + str(msg) + '\n')
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