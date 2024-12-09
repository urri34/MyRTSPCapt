#!python.exe
# -*- coding: utf-8 -*-
from pyusbcameraindex import enumerate_usb_video_devices_windows
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from os import path, getpid, kill
from pathlib import Path
from signal import SIGTERM
from sqlite3 import connect, Error
from sys import _getframe, exc_info
from threading import Thread
from time import time, strftime, localtime
from traceback import format_exception
import argparse
import cv2
import psutil

WindowVisible=True
WindowWidth=640

LogFile=path.join(path.dirname(path.realpath(__file__)), path.splitext(path.basename(__file__))[0]+'.log')
LogLevel=DEBUG #.DEBUG .INFO .WARNING .ERROR .CRITICAL
SQLiteFile=path.join(path.dirname(path.realpath(__file__)), path.splitext(path.basename(__file__))[0]+'.db')
PID=str(getpid())

class RTSPVideoWriterObject(object):

    def __init__(self, Src, VideoFileNameHeader):
        DefName=_getframe( ).f_code.co_name
        # Create a VideoCapture object
        self.Capture = cv2.VideoCapture(Src)
        logger.debug(PID+':'+DefName+'(): RTSP src='+str(Src))

        # Default resolutions of the frame are obtained (system dependent)
        self.FrameWidh = int(self.Capture.get(3))
        self.FrameHeight = int(self.Capture.get(4))
        self.Fps = self.Capture.get(cv2.CAP_PROP_FPS)
        logger.debug(PID+':'+DefName+'(): RTSP width='+str(self.FrameWidh))
        logger.debug(PID+':'+DefName+'(): RTSP height='+str(self.FrameHeight))
        logger.debug(PID+':'+DefName+'(): RTSP fps='+str(self.Fps))

        if WindowVisible:
            logger.debug(PID+':'+DefName+'(): Window visible=True')
            self.WindowWidth=WindowWidth
            logger.debug(PID+':'+DefName+'(): Window width='+str(self.WindowWidth))
            if self.FrameWidh != 0:
                self.WindowHeight=int(self.FrameHeight*WindowWidth/self.FrameWidh)
            else:
                self.WindowHeight=0
            logger.debug(PID+':'+DefName+'(): Window height='+str(self.WindowHeight))
        else:
            logger.debug(PID+':'+DefName+'(): Window visible=False')
        
        # Set up codec and output video settings
        self.VideoFileNameHeader=VideoFileNameHeader
        self.FileName=self.VideoFileNameHeader+'-'+str(Now())+'.avi'
        logger.debug(PID+':'+DefName+'(): Video filename='+str(self.FileName))
        self.OutPutVideoFile = cv2.VideoWriter(self.FileName, cv2.VideoWriter_fourcc(*'mp4v'), self.Fps, (self.FrameWidh, self.FrameHeight))
        self.ActualVideoStartTime=time()

        # Start the thread to read frames from the video stream
        self.Thread = Thread(target=self.Update, args=())
        self.Thread.daemon = True
        self.Thread.start()

    def RotateVideoFile(self):
        DefName=_getframe( ).f_code.co_name
        logger.debug(PID+':'+DefName+'(): Closing old video file '+str(self.FileName)+' ...')
        self.OutPutVideoFile.release()
        if IncomingVars['Order'] == '1shot' and ShouldIStop():
            logger.debug(PID+':'+DefName+'(): And closing the program')
            self.SayGoodBye()
        else:
            self.FileName=self.VideoFileNameHeader+'-'+str(Now())+'.avi'
            logger.debug(PID+':'+DefName+'(): Opening new video file '+str(self.FileName)+' ...')
            self.OutPutVideoFile = cv2.VideoWriter(self.FileName, cv2.VideoWriter_fourcc(*'mp4v'), self.Fps, (self.FrameWidh, self.FrameHeight))

    def Showframe(self):
        DefName=_getframe( ).f_code.co_name
        if self.status:
            cv2.imshow('RTSP', cv2.resize(self.frame, (self.WindowWidth, self.WindowHeight)))
        key = cv2.waitKey(1)
        if key != -1:
            logger.debug(PID+':'+DefName+'(): key='+str(key))
            if key == ord('q') or key == ord('Q'):
                logger.debug(PID+':'+DefName+'(): Calling exit due to key press')
                self.SayGoodBye()
        if cv2.getWindowProperty('RTSP', cv2.WND_PROP_VISIBLE) <1:
            logger.debug(PID+':'+DefName+'(): Calling exit due to cross clicked')
            self.SayGoodBye()

    def SaveFrame(self):
        self.OutPutVideoFile.write(self.frame)

    def SayGoodBye(self):
        DefName=_getframe( ).f_code.co_name
        logger.debug(PID+':'+DefName+'(): Cutting incoming stream')
        self.Capture.release()
        logger.debug(PID+':'+DefName+'(): Sttoping video capture')
        self.OutPutVideoFile.release()
        if WindowVisible:
            logger.debug(PID+':'+DefName+'(): Closing window')
            cv2.destroyAllWindows()
        UpdateAllDonesToTrue()
        SQLMainCon.close()
        exit(0)

    def Update(self):
        while True:
            if self.Capture.isOpened():
                try:
                    (self.status, self.frame) = self.Capture.read()
                except:
                    pass

def AmITheOnlyOne():
    DefName=_getframe( ).f_code.co_name
    logger.debug(PID+':'+DefName+'(): Am I the only one?')

    Me=path.basename(__file__)
    logger.debug(PID+':'+DefName+'(): me='+Me)
    for proc in psutil.process_iter():
        if 'python' in str(proc.name()):
            logger.debug(PID+':'+DefName+'(): Python detected=["'+str(proc.name())+'"] ["'+str(proc.pid)+'"] '+str(proc.cmdline()))
            if str(proc.name()) == 'pythonw.exe' or str(proc.name()) == 'python.exe':
                logger.debug(PID+':'+DefName+'(): Its a starter (pythonw.exe or python.exe)')
            else:
                if Me in proc.cmdline() or '.\\'+Me in proc.cmdline():
                    logger.debug(PID+':'+DefName+'(): This python process is executing a script called like Me:'+Me)
                    if str(PID) == str(proc.pid):
                        logger.debug(PID+':'+DefName+'(): It has my PID('+str(PID)+'), so its me, nothing to do -> Following up')
                    else:
                        logger.debug(PID+':'+DefName+'(): Its not my PID('+str(PID)+'), lets see if saving the same thing')
                        if not 'WebCam' in IncomingVars:
                            logger.debug(PID+':'+DefName+'(): Im not saving a Webcam, Im saving ip='+IncomingVars['Ip'])
                            if IncomingVars['Ip'] in proc.cmdline():
                                logger.debug(PID+':'+DefName+'(): There is really another me in execution against same Ip, no stop as order, time updated, so exiting.')
                                exit(0)
                            else:
                                logger.debug(PID+':'+DefName+'(): There is no one against same Ip -> Following up')
                        else:
                            logger.debug(PID+':'+DefName+'(): Im a Webcam='+IncomingVars['WebCam'])
                            WFlagDetected=False
                            WFlagValue=''
                            for Value in proc.cmdline():
                                if WFlagDetected==True:
                                    WFlagValue=Value
                                    WFlagDetected=False
                                if Value == '-w' or Value == '--webcam':
                                    WFlagDetected=True
                            if WFlagValue == str(IncomingVars['WebCam']):
                                logger.debug(PID+':'+DefName+'(): There is really another me in execution against same WebCam, no stop as order, time updated, so exiting.')
                                exit(0)
                            else:
                                logger.debug(PID+':'+DefName+'(): There is no one against same WebCam -> Following up')

def GetWebCamsList():
    WebCams=[]
    WebCams.append([None,"Choose webcam"])
    Devices = enumerate_usb_video_devices_windows()
    for Device in Devices:
        WebCams.append([Device.index, Device.name])
    return WebCams

def InitArgParse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [--ip/-i <ip> --username/-u <username> --password/-p <password>]/[--webcam/-w <webcamid>] --order/-o [1shot/forever/stop] --lenght/-l <secs>",
        description="Captures RTSP streams to MP4"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument('-w', '--webcam', nargs='*')
    parser.add_argument('-i', '--ip', nargs='*')
    parser.add_argument('-u', '--username', nargs='*')
    parser.add_argument('-p', '--password', nargs='*')
    parser.add_argument('-o', '--order', choices=['1shot', 'forever', 'stop'], nargs='*')
    parser.add_argument('-l', '--lenght', nargs='*')
    return parser

def InsertPeticio():
    DefName=_getframe( ).f_code.co_name
    SQLQuery='INSERT INTO main (rtspsrc, pid, start, stop, done) VALUES ('
    if not 'WebCam' in IncomingVars:
        SQLQuery+='"'+IncomingVars['Ip']+'", '
    else:
        SQLQuery+='"WebCam'+str(IncomingVars['WebCam'])+'", '
    SQLQuery+=str(PID)+', '
    SQLQuery+=str(time())+', '
    if IncomingVars['Order']=='1shot':
        Stop=time()+IncomingVars['VideoRotateSeconds']
        logger.debug(PID+':'+DefName+'(): 1shot, setting stop='+str(strftime('%Y/%m/%d %H:%M:%S', localtime(Stop))))
    else:
        Stop=time()+365*24*60*60
        logger.debug(PID+':'+DefName+'(): forever, setting stop='+str(strftime('%Y/%m/%d %H:%M:%S', localtime(Stop))))
    SQLQuery+=str(Stop)+', 0);'
    SQLiteQuery(SQLQuery)

def Now():
    from datetime import datetime
    return str(datetime.now().strftime("%Y%m%d%H%M%S"))

def SetIncomingVars():
    DefName=_getframe( ).f_code.co_name
    IncomingVars={}
    parser = InitArgParse()
    args = parser.parse_args()

    if not (args.order):
        logger.critical(PID+':'+DefName+'(): No order, add -o or --order')
        exit(1)
    else:
        if str(args.order[0]) not in ['1shot', 'forever', 'stop']:
            logger.critical(PID+':'+DefName+'(): Order must be set to 1shot or forever or stop')
            exit(1)
        IncomingVars['Order']=str(args.order[0])
        logger.debug(PID+':'+DefName+'(): order='+IncomingVars['Order'])

    if (args.webcam):
        IncomingVars['WebCam']=args.webcam[0]
        if not IncomingVars['WebCam'].isdigit():
            logger.critical(PID+':'+DefName+'(): WebCam Id should be a number')
            exit(1)
        IncomingVars['WebCam']=int(IncomingVars['WebCam'])
        logger.debug(PID+':'+DefName+'(): WebCamId='+str(IncomingVars['WebCam']))
        WebCams=GetWebCamsList()
        WebCamDetected=False
        for WebCam in WebCams:
            if WebCam[0] == IncomingVars['WebCam']:
                WebCamDetected=True
                logger.debug(PID+':'+DefName+'(): WebCamName="'+str(WebCam[1])+'"')
        if WebCamDetected == False:
            logger.critical(PID+':'+DefName+'(): Unable to find WebCam with id='+str(IncomingVars['WebCam']))
            exit(1)            
        else:
            IncomingVars['RTSPStreamLink'] = IncomingVars['WebCam']
    else:
        if not (args.ip):
            logger.critical(PID+':'+DefName+'(): No ip, add -i or --ip')
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

        if IncomingVars['Order'] != 'stop':
            if not (args.username):
                logger.critical(PID+':'+DefName+'(): No username, add -u or --username')
                exit(1)
            else:
                IncomingVars['UserName']=str(args.username[0])
                logger.debug(PID+':'+DefName+'(): username='+IncomingVars['UserName'])

            if not (args.password):
                logger.critical(PID+':'+DefName+'(): No password, add -p or --password')
                exit(1)
            else:
                IncomingVars['Password']=str(args.password[0])
                logger.debug(PID+':'+DefName+'(): password='+IncomingVars['Password'])
            RTSPStreamLink = 'rtsp://'+str(IncomingVars['UserName'])+':'+str(IncomingVars['Password'])+'@'+str(IncomingVars['Ip'])+':554/stream1'
            logger.info(PID+':'+DefName+'(): RTSPStreamLink='+str(RTSPStreamLink))
            IncomingVars['RTSPStreamLink'] = RTSPStreamLink

    if IncomingVars['Order'] != 'stop':
        if not (args.lenght):
            logger.critical(PID+':'+DefName+'(): No lenght, add -l or --lenght')
            exit(1)
        else:
            if not str(args.lenght[0]).isdigit():
                logger.critical(PID+':'+DefName+'(): Lenght must be set to a number "'+str(Value)+'"')
                exit(1)
            IncomingVars['VideoRotateSeconds']=int(args.lenght[0])
            logger.debug(PID+':'+DefName+'(): lenght='+str(IncomingVars['VideoRotateSeconds']))        

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

def ShouldIStop():
    DefName=_getframe( ).f_code.co_name
    UpdateNeededDonesToTrue()
    SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="'+IncomingVars['Ip']+'" AND stop>'+str(time())+' AND done=0;'
    Cursor=SQLiteQuery(SQLQuery)
    LenListCursorFromFile=len(list(Cursor))
    if LenListCursorFromFile == 0:
        logger.debug(PID+':'+DefName+'(): No entrys in future, we should stop')
        return True
    else:
        Cursor=SQLiteQuery(SQLQuery, 0)
        for Row in Cursor:
            Start=strftime('%Y/%m/%d %H:%M:%S', localtime(Row[3]))
            Stop=strftime('%Y/%m/%d %H:%M:%S', localtime(Row[4]))
            logger.debug(PID+':'+DefName+'(): Idunic='+str(Row[0])+', RTSPSrc='+str(Row[1])+', Pid='+str(Row[2])+', Start='+Start+', Stop='+Stop+', Done='+str(Row[5]))
        logger.debug(PID+':'+DefName+'(): Entrys in future, we should not stop')
        return False

def SQLitePrepare():
    DefName=_getframe( ).f_code.co_name
    global SQLMainCon
    logger.debug(PID+':'+DefName+'(): Connecting to SqLite ...')
    SQLQueryCreateMain='CREATE TABLE IF NOT EXISTS main (idunic integer PRIMARY KEY, rtspsrc text, pid integer, start REAL, stop REAL, done INTEGER);'
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

def UpdateAllDonesToTrue():
    DefName=_getframe( ).f_code.co_name
    Stop=time()
    if not 'WebCam' in IncomingVars:
        SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="'+IncomingVars['Ip']+'" AND done=0;'
    else:
        SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="WebCam'+str(IncomingVars['WebCam'])+'" AND done=0;'
    Cursor=SQLiteQuery(SQLQuery)
    LenListCursorFromFile=len(list(Cursor))
    if LenListCursorFromFile == 0:
        logger.warning(PID+':'+DefName+'(): No dones need to be updated to true! Not even myself?')
        return 0
    else:
        Cursor=SQLiteQuery(SQLQuery, 0)
        for Row in Cursor:
            Start=strftime('%Y/%m/%d %H:%M:%S', localtime(Row[3]))
            Stop=strftime('%Y/%m/%d %H:%M:%S', localtime(Row[4]))
            logger.debug(PID+':'+DefName+'(): Idunic='+str(Row[0])+', RTSPSrc='+str(Row[1])+', Pid='+str(Row[2])+', Start='+Start+', Stop='+Stop+', Done='+str(Row[5]))
            SQLQuery='UPDATE main SET done=1 WHERE idunic='+str(Row[0])+';'
            SQLiteQuery(SQLQuery)

def UpdateNeededDonesToTrue():
    DefName=_getframe( ).f_code.co_name
    Stop=time()
    if not 'WebCam' in IncomingVars:
        #SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="'+IncomingVars['Ip']+'" AND stop<'+str(Stop)+' AND done=0;'
        SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="'+IncomingVars['Ip']+'" AND pid NOT IN ("'+str(PID)+'") AND done=0;'
    else:
        #SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="WebCam'+str(IncomingVars['WebCam'])+'" AND stop<'+str(Stop)+' AND done=0;'
        SQLQuery='SELECT idunic,rtspsrc,pid,start,stop,done FROM main WHERE rtspsrc="WebCam'+str(IncomingVars['WebCam'])+'" AND pid NOT IN ("'+str(PID)+'") AND done=0;'
    Cursor=SQLiteQuery(SQLQuery)
    LenListCursorFromFile=len(list(Cursor))
    if LenListCursorFromFile == 0:
        logger.debug(PID+':'+DefName+'(): No dones need to be updated to true')
        return 0
    else:
        Cursor=SQLiteQuery(SQLQuery, 0)
        for Row in Cursor:
            Start=strftime('%Y/%m/%d %H:%M:%S', localtime(Row[3]))
            Stop=strftime('%Y/%m/%d %H:%M:%S', localtime(Row[4]))
            logger.debug(PID+':'+DefName+'(): Idunic='+str(Row[0])+', RTSPSrc='+str(Row[1])+', Pid='+str(Row[2])+', Start='+Start+', Stop='+Stop+', Done='+str(Row[5]))
            SQLQuery='UPDATE main SET done=1 WHERE idunic='+str(Row[0])+';'
            SQLiteQuery(SQLQuery)

def main():
    DefName=_getframe( ).f_code.co_name
    global logger, SQLMainCon, IncomingVars
    logger = SetMyLogger()
    logger.debug(PID+':'+DefName+'(): Logging active for me: '+str(Path(__file__).stem))
    SQLitePrepare()
    IncomingVars=SetIncomingVars()

    if IncomingVars['Order'] == 'stop':
        if not 'WebCam' in IncomingVars:
            SQLQuery='SELECT pid FROM main WHERE rtspsrc="'+IncomingVars['Ip']+'" AND done=0;'
        else:
            SQLQuery='SELECT pid FROM main WHERE rtspsrc="WebCam'+str(IncomingVars['WebCam'])+'" AND done=0;'
        Cursor=SQLiteQuery(SQLQuery)
        LenListCursorFromFile=len(list(Cursor))
        if LenListCursorFromFile == 0:
            logger.debug(PID+':'+DefName+'(): No entry to stop about this target')
        else:
            Cursor=SQLiteQuery(SQLQuery, 0)
            for Row in Cursor:
                kill(Row[0], SIGTERM)
        pass
    else:
        InsertPeticio()
        AmITheOnlyOne()
        UpdateNeededDonesToTrue()
        if not 'WebCam' in IncomingVars:
            VideoFileNameHeader='Stream'+IncomingVars['Ip'].split('.')[3]
        else:
            VideoFileNameHeader='Stream'+str(IncomingVars['WebCam'])
        logger.debug(PID+':'+DefName+'(): Opening RTSP ...')
        VideoStreamWidget = RTSPVideoWriterObject(IncomingVars['RTSPStreamLink'], VideoFileNameHeader)
        VideoStreamWidget.ActualVideoStartTime=time()
        logger.debug(PID+':'+DefName+'(): Starting time '+str(strftime('%Y/%m/%d %H:%M:%S', localtime(VideoStreamWidget.ActualVideoStartTime))))
        logger.debug(PID+':'+DefName+'(): VideoRotateSeconds '+str(IncomingVars['VideoRotateSeconds']))
        while True:
            if time()-VideoStreamWidget.ActualVideoStartTime > IncomingVars['VideoRotateSeconds']:
                VideoStreamWidget.RotateVideoFile()
                VideoStreamWidget.ActualVideoStartTime = time()
                logger.debug(PID+':'+DefName+'(): Starting time '+str(strftime('%Y/%m/%d %H:%M:%S', localtime(VideoStreamWidget.ActualVideoStartTime))))
            try:
                if WindowVisible:
                    VideoStreamWidget.Showframe()
                VideoStreamWidget.SaveFrame()
            except AttributeError:
                pass

if __name__ == '__main__':
    main()
