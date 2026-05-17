<img width="1536" height="1024" alt="ChatGPT Image May 12, 2026, 09_59_35 AM" src="https://github.com/user-attachments/assets/ef821ef7-33d4-45e1-9f44-951a869028fe" />

# MacDaddy - by WastelandSYS



<img width="1050" height="680" alt="macdaddy (1)" src="https://github.com/user-attachments/assets/09217c89-2d8a-48ec-8d59-1119b3b468ed" />






---------------------

![Screenshot_2024-07-30_16-10-08](https://github.com/user-attachments/assets/36cdc8cf-a628-46d6-9743-b2fb99843b02)
![Screenshot_2024-07-30_16-10-46](https://github.com/user-attachments/assets/786658e3-86a5-4a60-b12e-574750a5a50f)




Overview

MacDaddy is a Python tool designed to help you manage and manipulate MAC addresses on your network interfaces. It provides a range of functionalities including viewing, changing, and resetting MAC addresses, backing up and restoring MAC addresses, and even automating MAC address changes. 

-------------------------------
KEY FEATURES

* Show available network interfaces and their MAC addresses
* Display MAC address information for a specific interface
* Change MAC address of a specific interface
* Change MAC addresses of all interfaces
* Reset MAC address of a specific interface to its original state
* Reset MAC addresses of all interfaces to their original states
* Backup current MAC addresses to a text file
* Restore MAC addresses from a backup file
* Change MAC address to a custom value
* Check the status of a network interface (up/down)
* Automatically change MAC addresses at regular intervals
* Change the state of a network interface (up/down)

--------------------------------
 
INSTALLATION & USAGE

Git clone installation:

1. 'git clone https://github.com/WastelandSYS/macdaddy.git'
2. 'cd macdaddy'
3. 'chmod +x install.sh macdaddy.py'
4. 'sudo ./install.sh'
5. Exit and open a new terminal to use 'macdaddy' shortcut 

-------------------------------

DEPENDANCIES

For this tool to work you will need to have python3, macchanger, and iproute2 installed. The install.sh should automatically install them for you.
If not then use:

* sudo apt-get install -y python3
* sudo apt-get install -y macchanger
* sudo apt-get install -y iproute2

-------------------------------

This tool has been tested on my RPI 4b running a kali linux arm.
Enjoy and use responsibly
