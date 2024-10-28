# MyRTSPCapt

Contains the python scripts I use Save to a file a RTSP stream or a webcam stream.

## MyRTSPCapt.py:
### Idea behind:

I want my RTSP streams comming from my local cameras to be saved to a file. As the RTSP sources are in my LAN any computer in the LAN can be the one who store that RTSPs. As almost everything in my life it needs to be integrated with Home Assistant. In this case I want the media center to be the one that saves the streams and it's a windows machine, so everything is designed to work for windows.

[Hass.Agent](https://github.com/hass-agent/HASS.Agent) is the key to do that.

I'm able to see my RTSP in home Assistant, so I want a button that allows me to save that RTSP to a file. In order to do that I should create a Command in Hass:

(json placed in %LocalAppData%\HASS.Agent\Client\config and named commands.json as example where the garden camera is 192.168.1.2, you can find the full example in this repository [command.json](https://github.com/urri34/MyRTSPCapt/blob/main/commands_cmd.json))
```
  {
    "Id": "*",
    "Name": "WinTV_Capt1ShotGardenStart",
    "EntityName": "WinTV_Capt1ShotGardenStart",
    "Type": "CustomCommand",
    "EntityType": "button",
    "Command": "cd c:\\PythonProjects\\MyRTSPCapt && venv\\Scripts\\activate.bat && python MyRTSPCapt.py -u user -p password -o 1shot -l 300 -i 192.168.1.2",
    "KeyCode": 0,
    "RunAsLowIntegrity": false,
    "Keys": []
  }
```
In this case the script is placed in c:\PythonProjects\MyRTSPCapt and python runs with dependences solved in a venv environment [notes about venv](https://docs.python.org/3/library/venv.html). A button called WinTV_Capt1ShotGardenStart will appear in HA and if you click it it will start recording the RTSP that cames from 192.168.1.2 and stop after 300 seconds.
```
  {
    "Id": "*",
    "Name": "WinTV_CaptGardenStop",
    "EntityName": "WinTV_CaptGardenStop",
    "Type": "CustomCommand",
    "EntityType": "button",
    "Command": "cd c:\\PythonProjects\\MyRTSPCapt && venv\\Scripts\\activate.bat && python MyRTSPCapt.py -o stop -l 300 -i 192.168.1.2",
    "KeyCode": 0,
    "RunAsLowIntegrity": false,
    "Keys": []
  }
```
In this case a button called WinTV_CaptGardenStop will appear in HA and if you click it it will stop recording the RTSP that cames from 192.168.1.2, but not another one, just this one.
```
  {
    "Id": "*",
    "Name": "WinTV_CaptFEGardenStart",
    "EntityName": "WinTV_CaptFEGardenStart",
    "Type": "CustomCommand",
    "EntityType": "button",
    "Command": "cd c:\\PythonProjects\\MyRTSPCapt && venv\\Scripts\\activate.bat && python MyRTSPCapt.py -u user -p password -o forever -l 300 -i 192.168.1.2",
    "KeyCode": 0,
    "RunAsLowIntegrity": false,
    "Keys": []
  }
```
What if first I push the WinTV_Capt1ShotGardenStart button and then the WinTV_CaptFEGardenStart? The process associated to WinTV_CaptFEGardenStart will write down that the stream coming from 192.168.1.2 needs to be saved forever and just will die. After 300 seconds of being pushed, the process called by WinTV_Capt1ShotGardenStart, will know its time to die but will read that the stream coming from 192.168.1.2 need to be saved forever and will not die. All this information flow between processes is done thru a SQLite database generated just for this purpose.

If you dont feel comfortable using cmd for running your scripts and prefer powershell, you can also find a version of commands.json to do so [command.json](https://github.com/urri34/MyRTSPCapt/blob/main/commands_powershell.json)).

### Basic configuracion options:

- WindowVisible=False

Do you want the window with the content of the RTSP to be seen during the capture? That easy.

- WindowWidth=640

If you want the window to be seen how witdh do you want it to be?

### Execution parameters:

If you want to capture a RTSP stream to a file you should use:

--ip/-i <ip> (The ip addres of the RTSP source, tipycaly the camera)

--username/-u <username> (It's a good option to have the RTSP protected with username and password)

--password/-p <password>( It's a good option to have the RTSP protected with username and password)

If you want to store a WebCam stream to a file you should use:

--webcam/-w <webcamid> (In case you want to capture a webcam stream, use the webcamid to do that)=

In both cases you will need also to specify:

--order/-o [1shot/forever/stop] (how much do you wantto capture? just one shot? forever? or tell it to stop if it was capturing that source?)

--lenght/-l <secs> (how long do you want it to save if its 1shot or how long it take toevery file if its a forever)

## MyRTSPStatus.py:
### Idea behind:
I want to know in HA if the desired streams is really being saved or not.

[Hass.Agent](https://github.com/hass-agent/HASS.Agent) is the key to do that ... again :)

(json placed in %LocalAppData%\HASS.Agent\Client\config and named sensors.json as example, you can find the full example in this repository [command.json](https://github.com/urri34/MyRTSPCapt/blob/main/sensors.json))
```
  {
    "Type": "PowershellSensor",
    "Id": "*",
    "Name": "WinTV_8888",
    "UpdateInterval": 30,
    "Query": "cd c:\\PythonProjects\\MyRTSPCapt;venv\\Scripts\\activate.ps1;python.exe MyRTSPStatus.py -i 192.168.1.2",
    "Scope": null,
    "WindowName": "",
    "Category": "",
    "Counter": "",
    "Instance": "",
    "EntityName": "WinTV_CaptGardenStatus",
    "IgnoreAvailability": false,
    "ApplyRounding": false,
    "Round": null,
    "AdvancedSettings": null
  }
```
With this code we will have a sensor in HA that will simply said true or false about the stream 192.168.1.2 being saved.

### Basic configuracion options:

- MyRTSPCaptFile='MyRTSPCapt.py'

The name of the file that we expect to be storing the RTSP stream

- TimeLimit=20

We get a process list every TimeLimit (it's somehow hard to take it from python)

### Execution parameters:

Just the ip of the RTSP you want to know its status:

--ip/-i <ip> (The ip addres of the RTSP source, tipycaly the camera)

## Home Assistant integration:

### What I want:

An easy command center where to see the cam and decide when to save and which machine use to save.

![My HA Controls](https://github.com/urri34/MyRTSPCapt/blob/main/CaptureGarden.jpg)

In my case I have a switch previosly to the POE that allows me to start and stop the camera and it's the one places in the right.

[You can find the full example code here](https://github.com/urri34/MyRTSPCapt/blob/main/HomeAssistantCard.yaml)
