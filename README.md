# ipcam2 - weather cam

This is our ip-cam script in Python3, picamera2-library based on libcamera software. Tested with Raspberry Pi Zero 2 W and Camera Module3.               

### Presets                                                                        

The scripts are located in a "scripts" folder in the Pi's home directory under "/home/~/scripts". To install paramiko and pythonmagick please do        
sudo apt install python3-paramiko                                              
sudo apt install python3-pythonmagick                                          
                                                                                
### Notes                                                                          

This is our first build in this configuration. Reason for version number "2" that there is a previous model in our development with different hardware.  

### Blink codes                                                                    

3x short - boot finished, starting recording                                   
2x long  - recording finished, sftp upload starts                              
4x short - sftp upload finished, now shutting down    
1x long  - sftp upload error    
