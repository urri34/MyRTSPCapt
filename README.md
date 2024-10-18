# MyWebInLANDetect
Contains the python scripts I use to detect my GeekMagic SmallTV-Ultra. It wakes up with DHCP and I never know where is it. It can be used to find any kind of webserver , in any kind of ip range and can detect any kind of string in the web server serving page.

## MyWebInLANDetect.py:
### Idea behind:


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
--lenght/-l <secs>
