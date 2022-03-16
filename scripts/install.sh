#!/bin/sh

set +e

# make mopidy source repository available in apt

sudo mkdir -p /usr/local/share/keyrings

sudo wget -q -O /usr/local/share/keyrings/mopidy-archive-keyring.gpg \
  https://apt.mopidy.com/mopidy.gpg

sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

echo "make mopidy source repository available in apt ... DONE"

sudo apt update
sudo apt upgrade -y

echo "update and upgrade ... DONE"

# install all apt dependencies 
sudo apt install \
python3-dev \
python3-pip \
git \
mpc \
mopidy \
alsa-utils \
libspotify-dev \
-y

echo "install all apt dependencies ... DONE"

# upgrade pip
sudo pip3 install --upgrade pip

echo "upgrade pip ... DONE"

# install python libs
pip3 install  \
Mopidy-Spotify \
Mopidy-MPD \
spidev \
RPi.GPIO \
playsound 

echo "install python libs ... DONE"

sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt

pip3 list --format=freeze > ~/requirements.txt

echo "freeze pip dependencies ... DONE"

git clone https://github.com/matana/kasimir-player.git

echo "clone kasimir player git repository ... DONE"

mkdir -p ~/.config/mopidy
touch ~/.config/mopidy/mopidy.conf


read -p "Enter spotify username: " spotify_username
read -p "Enter spotify password: " spotify_password
read -p "Enter spotify client_id: " spotify_client_id
read -p "Enter spotify client_secret: " spotify_client_secret

cat > ~/.config/mopidy/mopidy.conf <<EOF
[spotify]
enabled = true
username = ${spotify_username}
password = ${spotify_password}
client_id = ${spotify_client_id}
client_secret = ${spotify_client_secret}
allow_playlists = true

EOF

echo "setup mopidy conf file ... DONE"

sudo touch /etc/systemd/system/mopidyd.service
sudo chmod 777 /etc/systemd/system/mopidyd.service

sudo cat > /etc/systemd/system/mopidyd.service <<EOF
[Unit]
Description=Mopidy Service
Requires=network-online.target
After=network-online.target

[Service]
Type=simple
User=${USER}
Group=${USER}
ExecStart=/usr/bin/mopidy --config ~/.config/mopidy/mopidy.conf
SyslogIdentifier=mopidyService
StandardOutput=syslog
StandardError=syslog
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

EOF

sudo chmod 644 /etc/systemd/system/mopidyd.service
sudo chown $USER:$USER /etc/systemd/system/mopidyd.service

echo "setup mopidyd.service ... DONE"

sudo touch /etc/systemd/system/kasimir.service
sudo chmod 777 /etc/systemd/system/kasimir.service

sudo cat > /etc/systemd/system/kasimir.service <<EOF
[Unit]
Description=Kasimir's Music Player
After=network-online.target mopidyd.service 

[Service]
Type=simple
User=${USER}
Group=${USER}
WorkingDirectory=/home/${USER}
ExecStart=/home/${USER}/kasimir-player/src/player.py
SyslogIdentifier=kasimirPlayer
StandardOutput=syslog
StandardError=syslog
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

EOF

sudo chown $USER:$USER /etc/systemd/system/kasimir.service
sudo chmod 644 /etc/systemd/system/kasimir.service

echo "setup kasimir.service ... DONE"

sudo systemctl enable mopidyd.service
sudo systemctl enable kasimir.service

sudo systemctl start mopidyd.service
sudo systemctl start kasimir.service

echo "services mopidyd.service, kasimir.service enabled and started ... DONE"

sudo reboot
