# Kasimir's Musicbox

Kasmirs Player is a jukebox project for Raspberrypi beginners, who always wanted to program a hardware interface besides the software. 

Front            |  Back | (Rainbow) Inside
:-------------------------:|:-------------------------: | :-------------------------: 
![front](https://github.com/matana/kasimir-player/blob/main/docs/110C61D7-EDF1-424E-B1D0-1914034A8859_1_105_c.jpeg)  | ![back](https://github.com/matana/kasimir-player/blob/main/docs/E95F60C3-83EF-4FC7-81CE-0B23D4A58033_1_105_c.jpeg) | ![inside](https://github.com/matana/kasimir-player/blob/main/docs/8DE36A21-5BB5-4559-824A-C8C022ADC503_1_105_c.jpeg)

## Legend
- [Requirements](#requirements)
- [Installing RPi OS](#installing-rpi-os)
  - [Setup WiFi and SSH on Raspberry Pi](#setup-wifi-and-ssh-on-raspberry-pi)
  - [Connecting to RPi via SSH](#connecting-to-rpi-via-ssh)
  - [Enabling SPI on Raspberry Pi](#enabling-spi-on-raspberry-pi)
- [Installing pip](#installing-pip)
- [Installing Mopidy](#installing-mopidy)
  - [Setup Spotify Configuration in Mopidy](#setup-spotify-configuration-in-mopidy)
- [Setup Services as Deamons](#setup-services-as-deamons)
- [RFID Card Reader (RC522)](#rfid-card-reader-rc522)
  - [Read / Write Data Blocks from / to RFID Card](#read--write-data-blocks-from--to-rfid-card)
- [Add a Spotify Playlist ID to the RFID Card](#add-a-spotify-playlist-id-to-the-rfid-card)
- [Rotary Encoder (KY-040) aka Volume Control](#rotary-encoder-ky-040-aka-volume-control)
- [Turn on / off RPi](#turn-on--off-rpi)
- [Refernces](#refernces)


### Requirements
Hardware
- Raspberry Pi 4
- Rc522 RFID Reader
- Rotary Encoder Push button KY-040

Software
- [Mopidy](https://mopidy.com/)
- Spotify 
- Pip and some Python libs (see [requirments.txt](https://github.com/matana/kasimir-player/blob/main/requirements.txt))

### Installing RPi OS

Install Raspberry Pi OS using Raspberry Pi Imager which can be downloaded [here](https://www.raspberrypi.com/software/). We want to install the headless version of the RPi os (Raspberry Pi OS Lite) for performance reasons, since we don't need a monitor for the application. Besides the lower memory requirement, an additional advantage is the faster startup of the machine. Details of how to install the RPi os can be found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system).


### Setup WiFi and SSH on Raspberry Pi

Create files [wpa_supplicant.conf](https://www.daemon-systems.org/man/wpa_supplicant.conf.5.html) and ssh in Boot-Partition (Raspbian Stretch) via terminal.

```bash
$ cd /Volumes/boot
$ touch ssh 
$ touch wpa_supplicant.conf
```

The configuration can be copied from below and only needs to be supplemented with the name of the wifi network and the wifi password.

```bash
$ nano wpa_supplicant.conf

# paste this config into wpa_supplicant.conf and replace WIFI_* placeholders 
country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
       ssid="WIFI_NAME"
       psk="WIFI_PASSWORD"
       key_mgmt=WPA-PSK
}
```

To unmount the device you can use the cmd tool `diskutil`. On Mac OS use `diskutil unmountDisk /dev/disk2` in terminal.

### Connecting to RPi via SSH
Use the `ssh` command under unix/linux systems with *user@host* (the default is pi@raspberrypi) to connect to yout RPi. The default `ssh` password is *raspberry*. After first successful login, please
change user, host and password (at minimum) and store it safely into you the password manager you trust.

> NOTE: You won't be able to connect to your RPi ending up in a `ssh: connect to host raspberrypi port 22: Operation timed out`. The reason is quite simple: Your RPi has neither a (public) static IP adress, nor a DNS record poiting to the machine. Therfore you have to adjust additional secuity settings in your wifi router/network to permit other wifi devices to communicate with each other. (see configuration for [FRITZ!Box](https://en.avm.de/service/knowledge-base/dok/FRITZ-Box-7490/549_Shared-files-and-printers-on-a-computer-are-not-visible-in-home-network/))

```bash
$ ssh pi@raspberrypi 
...
pi@raspberrypi:~ $ sudo passwd pi # change password after login
```
Find [here](https://www.raspberrypi.com/documentation/computers/using_linux.html#linux-users) the how-to on managing users. You could also change the default hostname `raspberry` with `$ sudo raspi-config > 1 System Options > S4 Hostname` and then restart the system `$ sudo shutdown -r now` or `$ sudo reboot`.  

While you are on your RPi machine, think about doing a system update ;)
```bash
$ sudo apt update -y && sudo apt upgrade -y
```

You can also add a public key (id_rsa.pub) to the file .ssh/authorized_keys. This also gives you the possibility to log in via `ssh -i ~/.ssh/id_rsa user@host`. To generate a public/private rsa key pair on you local machine use `ssh-keygen`. Use `touch ~/.ssh/authorized_keys` to create the file for authorized keys on RPi (server) and add either manually the id_rsa.pub key into (copy/paste) *.ssh/authorized_keys* or via command `ssh-copy-id`. 

## Installing pip

If you have Rapberry Pi OS Lite (Debian Bullseye) installed the current Python version is 3.9.2 (see: https://packages.debian.org/bullseye/python3).

```bash
$ sudo apt-get install python3-dev python3-pip -y
$ pip3 install --upgrade pip
```
## Installing git
```bash
$ sudo apt-get install git -y
$ git clone https://github.com/matana/kasimir-player.git
``` 

## Enabling SPI on Raspberry Pi

`$ sudo pip3 install spidev # (already installed)`

The interface can be activated via the GUI. To invoke the GUI enter the following command.

```bash
$ sudo raspi-config # enable spi interface
```
![img_spi1](https://github.com/matana/kasimir-player/blob/main/docs/img_spi1.png)
![img_spi2](https://github.com/matana/kasimir-player/blob/main/docs/img_spi2.png)
![img_spi3](https://github.com/matana/kasimir-player/blob/main/docs/img_spi3.png)

Finally reboot the RPi. 
```bash
$ sudo reboot
```

Alternatively, SPI can be enabled via a modification to a system file. The following configuration must be made for this.

```bash
$ sudo nano /boot/config.txt
```

Add the following line at the bottom or if it's commented uncomment the corosponding line and save the changes on exit with `CTRL-X`, then `Y`, and finally `RETURN`.

```bash
dtparam=spi=on
```

Reboot the machine using the following comannd.
```bash
$ sudo reboot
```

Check that the SPI is enabled with `lsmod` (see man page [here](https://man7.org/linux/man-pages/man8/lsmod.8.html)).
```
$ lsmod | grep spi_
```

![img_lsmod](https://github.com/matana/kasimir-player/blob/main/docs/img_lsmod.png)

## Installing Mopidy and Spotify extension

[Here](https://docs.mopidy.com/en/latest/installation/) you can find the Mopidy installation instructions for various operating systems.
```bash
$ wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add - \
&& sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list \
&& sudo apt update \
&& sudo apt install mopidy -y
```
Installing also Mopidy extension for playing music from Spotify (see: https://github.com/mopidy/mopidy-spotify#installation).
```bash
$ sudo apt install libspotify-dev
$ sudo python3 -m pip install Mopidy-Spotify
```

### Setup Spotify Configuration in Mopidy 
You can get the API credentials to your Spotify account and find as well  the installation instructions [here](https://mopidy.com/ext/spotify/). A Spotify Premium subscription is required. 

```bash
$ touch ~/.config/mopidy/mopidy.conf \
&& nano ~/.config/mopidy/mopidy.conf

[spotify]
enabled = true
username = USER_NAME
password = USER_PASSWORD
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
allow_playlists = true
```

To communicate with the Mopidy server we use [MPD](https://docs.mopidy.com/en/latest/clients/#mpd-clients) (Music Player Daemon) and this in turn is accessed by `mpc` ([a command line client for MPD](https://www.musicpd.org/clients/). Version 0.19 and upwards seems to work nicely with Mopidy.). 

```bash
$ #sudo apt-get install mpd mpc alsa-utils -y #not working! 
$ sudo python3 -m pip install Mopidy-MPD
```
## Setup Services as Deamons

Upload the service configuration file to the RPi...

```bash
scp -i ~/.ssh/id_rsa mopidyd.service pi@raspberrypi:/home/pi
scp -i ~/.ssh/id_rsa kasimir.service pi@raspberrypi:/home/pi
```
... and move them into *systemd* services folder `/etc/systemd/system/`.

```bash
sudo mv mopidyd.service /etc/systemd/system/
sudo mv kasimir.service /etc/systemd/system/
```
Finally enable the services. 

```bash
sudo systemctl enable mopidyd.service
sudo systemctl start mopidyd.service
sudo systemctl enable kasimir.service
sudo systemctl start kasimir.service
```

You can use `systemctl` commands interact with the services. [Here](https://man7.org/linux/man-pages/man1/systemctl.1.html#COMMANDS) you'll find an overview of all *systemctl* comands. The command `sudo systemctl status kasimir.service` for example can be used to query the status of the service.

![img_systemctl](https://github.com/matana/kasimir-player/blob/main/docs/img_systemctl.png)

With `journalctl -u kasimir.service -r` can be used to read the logs in reversed time order. The most recent log entrie will be on top. [Here](https://man7.org/linux/man-pages/man1/journalctl.1.html#COMMANDS) you'll find an overview of all *journalctl* comands.

![img_journalctl](https://github.com/matana/kasimir-player/blob/main/docs/img_journalctl.png)


## RFID Card Reader (RC522)

![588FD058-5235-4D36-ADF8-C0F35E8CD252_1_105_c.jpeg](https://github.com/matana/kasimir-player/blob/main/docs/588FD058-5235-4D36-ADF8-C0F35E8CD252_1_105_c.jpeg)

To read and write RFID cards I used the project [pi-rc522](https://github.com/ondryaso/pi-rc522). It is relatively complicated to get into the world of bitshifts and low level programming. Nevertheless it is worth to have a look at it. 

The command `pinout` will show the 40 pins in the terminal on your RPi. Have also a look [here](https://pinout.xyz/#). With  Pthon module RPi.GPIO you can control Raspberry Pi GPIO channels.

![img_pinout](https://github.com/matana/kasimir-player/blob/main/docs/img_pinout.png)

Connecting the RC522 module to the RPi's SPI (Serial Peripheral Interface).

| RC522 pin name | Physical RPi pin | RPi Broadcom pin name | 
|----------------|------------------|-----------------------| 
| SDA            | 24               | GPIO8, CE0            | 
| SCK            | 23               | GPIO11, SCKL          | 
| MOSI           | 19               | GPIO10, MOSI          | 
| MISO           | 21               | GPIO9, MISO           | 
| IRQ            | 18               | GPIO24                | 
| GND            | 6, 9, 20, 25     | Ground                | 
| RST            | 22               | GPIO25                | 
| 3.3V           | 1,17             | 3V3                   |



### Read / Write Data Blocks from / to RFID Card

The module `src/read_write_rfid.py` can be used to write or read RFID cards. The memory is currently limited to three blocks of a sector (48 characters), but can be extended easily if needed. Details about the memory organization can be found [here](https://www.nxp.com/docs/en/data-sheet/MF1S50YYX_V1.pdf#%5B%7B%22num%22%3A243%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C150.062%2C327.517%2Cnull%5D). 

## Add a Spotify Playlist ID to the RFID Card

To add Spotify playlist IDs to the RFID cards execute the following script: `./src/read_write_rfid.py -w`. The flag `-w` routes to the standard input. 

Currently the pattern you will have to store on the RFID card looks like this: 
```
playlist:<spotify_playlist_id>
``` 
The reason is that `mpc` and therefore Mopidy consumes this kind of [Spotify URI pattern](https://github.com/mopidy/mopidy-spotify/issues/214)
```
spotify:playlist:<spotify_playlist_id>
``` 

The link to the playlist can be obtained via the Spotify app. Go to the desired playlist and copy the link via the context menu *... > Share > Copy link to playlist*. The link looks something like this: https://open.spotify.com/playlist/5G1mm8Utb185nf8CXL3kIF

You will need to extract the ID form URL path `https://.../playlist/<spotify_playlist_id>`. As soon as the complete string is available in the input, press enter. Now you will be asked to hold the card to the RFID interface and wait until the data transfer is completed. As soon as you see the message `Done :)` you can remove the card. If an error occurs, repeat the procedure. In the future the Spotify URL should be stored completely. 

## Rotary Encoder (KY-040) aka Volume Control

![6AE92102-9976-4774-B130-71444C3446FF_1_105_c.jpeg)](https://github.com/matana/kasimir-player/blob/main/docs/6AE92102-9976-4774-B130-71444C3446FF_1_105_c.jpeg)

The volume is controlled via a rotary knob. The implementation for this can be found in module `src/rotary_encoder.py`. Turning the knob clockwise increases the volume. Turning the knob counterclockwise decreases the volume. The volume range is between 0 and 100. The minimum volume is 10 and the maximum 90. The volume is currently increased/decreased in steps of 3. The setting can be changed in the module `src/player.Volume`. Default volumne on start up is 10. 

Another feature of the rotary knob is that it can also be pressed. This event is also processed by the module and a corresponding callback is returned to the player. The button press is interpreted as a play/pause function. 

Connecting the KY-040 module to the RPi's. 

| RC522 pin name | Physical RPi pin | RPi Broadcom pin name | 
|----------------|------------------|-----------------------| 
| CLK            | 29               | GPIO5                 | 
| DT             | 31               | GPIO6                 | 
| SW             | 33               | GPIO13 (PWM1)         | 
| +              | 17               | 3V3                   | 
| GND            | 39               | Ground                | 


## Turn on / off RPi

If the Raspberry Pi is completely shut down, you can see that only the red LED is permanently on. As long as the green LED is still blinking, you should keep your hands off the plug.

```bash
# shutdown variations
sudo shutdown
sudo shutdown -h 0
sudo shutdown -h now
sudo poweroff

# reboot variations
sudo shutdown -r 0
sudo shutdown -r now
sudo reboot
``` 

## Refernces
- Raspberry Pi Imager - https://www.raspberrypi.com/software/  
- GPIO and the 40-pin Header - https://www.raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header
- Setup WiFi on Raspberry Pi -  https://pi-buch.info/wlan-schon-vor-der-installation-konfigurieren/
- Mopidy - https://mopidy.com/
- Mopidy-Spotify - https://github.com/mopidy/mopidy-spotify#dependencies
- How to Install Pip on Debian 10 - https://linuxize.com/post/how-to-install-pip-on-debian-10/
- Advanced Linux Sound Architecture (ALSA) - https://wiki.archlinux.org/title/Advanced_Linux_Sound_Architecture
- Mopidy NPM - https://www.npmjs.com/package/mopidy
- How to Use SSH Public Key Authentication - https://serverpilot.io/docs/how-to-use-ssh-public-key-authentication/
- The Linux man-pages project - https://www.kernel.org/doc/man-pages/
- systemd Services - https://wiki.debian.org/systemd/Services
