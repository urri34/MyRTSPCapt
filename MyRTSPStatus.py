import psutil
from os import getpid, path
import argparse
from sys import _getframe, exc_info, path
from pathlib import Path
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from sqlite3 import connect, Error, Binary
from traceback import format_exception
from os import path, getpid
from time import time
import pickle

MyRTSPCaptFile='MyRTSPCapt.py'
TimeLimit=20

LogFile=path.join(path.dirname(path.realpath(__file__)), path.splitext(path.basename(__file__))[0]+'.log')
LogLevel=DEBUG #.DEBUG .INFO .WARNING .ERROR .CRITICAL
SQLiteFile=path.join(path.dirname(path.realpath(__file__)), path.splitext(path.basename(__file__))[0]+'.db')
PID=str(getpid())

def SQLitePrepare():
    DefName=_getframe( ).f_code.co_name
    global SQLMainCon
    logger.debug(PID+':'+DefName+'(): Connecting to SqLite ...')
    SQLQueryCreateMain='CREATE TABLE IF NOT EXISTS main (idunic INTEGER PRIMARY KEY, time INTEGER, name TEXT, pid INTEGER, cmdline BLOB);'
    if path.exists(SQLiteFile):
        logger.debug(PID+':'+DefName+'(): SQliteFile exist as '+SQLiteFile)
    else:
        logger.warning(PID+':'+DefName+'(): SQliteFile not present as '+SQLiteFile)
    SQLMainCon=connect(SQLiteFile)
    SQLMainCon.execute("PRAGMA busy_timeout=3000")
    SQLMainCon.cursor().execute(SQLQueryCreateMain)
 
def SQLiteQuery(SQLQuery, Verbose=1):
    DefName=_getframe( ).f_code.co_name
    if Verbose==1:
        logger.debug(PID+':'+DefName+'(): SQLQuery='+SQLQuery)
    Cursor=SQLMainCon.cursor()
    try:
        Cursor.execute(SQLQuery)
    except Error as er:
        logger.warning(PID+':'+DefName+'(): SQLite error: %s' % (' '.join(er.args)))
        logger.warning(PID+':'+DefName+'(): Exception class is: ', er.__class__)
        logger.warning(PID+':'+DefName+'(): SQLite traceback: ')
        exc_type, exc_value, exc_tb = exc_info()
        logger.warning(PID+':'+DefName+'(): '+str(format_exception(exc_type, exc_value, exc_tb)))
    except:
        logger.warning(PID+':'+DefName+'(): Something went wrong with SQLQuery!')
        return 0
    try:
        SQLMainCon.commit()
        return Cursor
    except:
        logger.critical(DefName+'(): Something went wrong with commit!')
        return 0

def ReadProcsToDB():
    DefName=_getframe( ).f_code.co_name
    global Rebuild
    logger.debug(PID+':'+DefName+'(): Reading process and storing them in DB.')
    SQLQuery='DELETE FROM main;'
    SQLiteQuery(SQLQuery)
    for proc in psutil.process_iter():
        if 'python' in str(proc.name()):
            logger.debug(PID+':'+DefName+'(): Storing '+str([time(), proc.name(), proc.pid, proc.cmdline()]))
            SQLMainCon.cursor().execute("INSERT INTO main (time, name, pid, cmdline) VALUES (?, ?, ?, ?)", (time(), proc.name(), proc.pid, Binary(pickle.dumps(proc.cmdline()))))
    logger.debug(PID+':'+DefName+'(): Done!')
    Rebuild=True

def AmIBeingSaved():
    DefName=_getframe( ).f_code.co_name
    logger.debug(PID+':'+DefName+'(): Am I being saved?')
    SQLQuery='SELECT time FROM main ORDER BY time DESC LIMIT 1;'
    Cursor=SQLiteQuery(SQLQuery)
    LenListCursorFromFile=len(list(Cursor))
    if LenListCursorFromFile == 0:
        logger.debug(PID+':'+DefName+'(): No entrys in main, need to read processes')
        ReadProcsToDB()
    else:
        Cursor=SQLiteQuery(SQLQuery, 0)
        if Cursor.fetchone()[0]+TimeLimit < time():
            logger.debug(PID+':'+DefName+'(): Old entrys in main, need to read processes')
            ReadProcsToDB()
    logger.debug(PID+':'+DefName+'(): Main populated')
    SQLQuery='SELECT name,cmdline FROM main;'
    Cursor=SQLiteQuery(SQLQuery)
    LenListCursorFromFile=len(list(Cursor))
    if LenListCursorFromFile == 0:
        logger.warning(PID+':'+DefName+'(): No python process running in this machine!')
        return False
    else:
        Cursor=SQLiteQuery(SQLQuery, 0)
        for Row in Cursor:
            Name=str(Row[0])
            CMDLine=pickle.loads(Row[1])
            logger.debug(PID+':'+DefName+'(): Processing '+str([Name, CMDLine]))
            if Name == 'pythonw.exe' or Name == 'python.exe':
                logger.debug(PID+':'+DefName+'(): Its a starter')
            else:
                if MyRTSPCaptFile in CMDLine or '.\\'+MyRTSPCaptFile in CMDLine:
                    logger.debug(PID+':'+DefName+'(): Python executing '+MyRTSPCaptFile)
                    if not 'WebCam' in IncomingVars:
                        if IncomingVars['Ip'] in CMDLine:
                            logger.debug(PID+':'+DefName+'(): Someone is saving this Ip')
                            return True
                    else:
                        WFlagDetected=False
                        WFlagValue=''
                        for Value in CMDLine:
                            if WFlagDetected==True:
                                WFlagValue=Value
                                WFlagDetected=False
                            if Value == '-w':
                                WFlagDetected=True
                        if WFlagValue == str(IncomingVars['WebCam']):
                            logger.debug(PID+':'+DefName+'(): Someone is saving this WebCam')
                            return True
                else:
                    logger.debug(PID+':'+DefName+'(): Python not executing '+MyRTSPCaptFile)
    logger.debug(PID+':'+DefName+'(): No one is executing '+MyRTSPCaptFile)
    return False                      

def InitArgParse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s --ip <ip> / --webcam <webcamid>",
        description="Captures RTSP/WebCam streams to MP4"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument('-w', '--webcam', nargs='*')
    parser.add_argument('-i', '--ip', nargs='*')
    return parser

def SetIncomingVars():
    DefName=_getframe( ).f_code.co_name
    IncomingVars={'WebCam':'','Ip':''}
    parser = InitArgParse()
    args = parser.parse_args()
    if (args.webcam):
        IncomingVars['WebCam']=args.webcam[0]
        if not IncomingVars['WebCam'].isdigit():
            logger.critical(PID+':'+DefName+'(): WebCam Id should be a number')
            exit(1)
        IncomingVars['WebCam']=int(IncomingVars['WebCam'])
        logger.debug(PID+':'+DefName+'(): WebCamId='+str(IncomingVars['WebCam']))
    else:
        if not (args.ip):
            logger.critical(PID+':'+DefName+'(): No ip, add -i or --ip. No webcam, add -w or --webcam.')
            exit(1)
        else:
            if str(args.ip[0]).count('.') != 3:
                logger.critical(PID+':'+DefName+'(): Not a valid ip format 1.1.1.1')
                exit(1)
            for Value in args.ip[0].split('.'):
                if not Value.isdigit():
                    logger.critical(PID+':'+DefName+'(): Not a number inside ip "'+str(Value)+'"')
                    exit(1)
            IncomingVars['Ip']=str(args.ip[0])
            logger.debug(PID+':'+DefName+'(): Ip='+IncomingVars['Ip'])   
    return IncomingVars

def SetMyLogger():
    from  logging import getLogger, Formatter
    from logging.handlers import RotatingFileHandler

    logger = getLogger()
    logger.setLevel(LogLevel)
    LogFormat = ('[%(asctime)s] %(levelname)-4s %(message)s')
    formatter = Formatter(LogFormat)

    file_handler = RotatingFileHandler(LogFile, mode="a", encoding="utf-8", maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(LogLevel)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def main():
    DefName=_getframe( ).f_code.co_name
    global logger, SQLMainCon, IncomingVars, Rebuild
    logger = SetMyLogger()
    logger.debug(PID+':'+DefName+'(): Logging active for me: '+str(Path(__file__).stem))
    IncomingVars=SetIncomingVars()
    SQLitePrepare()
    Rebuild=False
    AmIBeingSavedStatus=str(AmIBeingSaved())
    print(AmIBeingSavedStatus)
    if Rebuild:
        Rebuild=' (rebuild)'
    else:
        Rebuild=''
    logger.info('PID('+PID+'): '+DefName+'(): '+str(Path(__file__).stem)+'.py -i="'+IncomingVars['Ip']+'" -w="'+str(IncomingVars['WebCam'])+'"'+Rebuild+' -> '+AmIBeingSavedStatus)

if __name__ == '__main__':
    main()
