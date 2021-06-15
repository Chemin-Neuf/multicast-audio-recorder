printf "INSTALLING MULTICAST AUDIO RECORDER..."
printf "\nINSTALL GIT and other tools\n"
sudo apt-get update && sudo apt-get install -y git ffmpeg python3-venv python3-pip
pip3 install Flask python-dateutil

# give rights on tcpdump to ccninfo
groupadd pcap
usermod -a -G pcap ccninfo
chgrp pcap /usr/sbin/tcpdump
setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
ln -s /usr/sbin/tcpdump /usr/bin/tcpdump


if [[ -d "/home/ccninfo" ]]
then
    printf "\nCLONE THE GIT REPO in /home/ccninfo/multicast-audio-recorder\n"
    cd /home/ccninfo/
    git clone https://github.com/Chemin-Neuf/multicast-audio-recorder.git

    printf "\nCOPY THE SERVICE FILE IN /etc/systemd/system/\n"
    if [[ -d "/home/ccninfo/multicast-audio-recorder" ]]
    then
        cd /home/ccninfo/multicast-audio-recorder
        mkdir /home/ccninfo/multicast-audio-recorder/data
        python3 -m venv venv
        source venv/bin/activate
        pip3 install Flask python-dateutil
        python -m flask --version
        chmod +x /home/ccninfo/multicast-audio-recorder/start.sh
        chmod +x /home/ccninfo/multicast-audio-recorder/start_dev.sh
        chmod +x /home/ccninfo/multicast-audio-recorder/recorder_update.sh
        chmod +x /home/ccninfo/multicast-audio-recorder/recorder_install.sh

        # setup the service
        cp /home/ccninfo/multicast-audio-recorder/audio-recorder.service /etc/systemd/system/audio-recorder.service
        sudo chmod u+x /etc/systemd/system/audio-recorder.service
        sudo systemctl enable audio-recorder.service
        sudo systemctl restart audio-recorder.service
        sudo systemctl status audio-recorder.service

        printf "\nAUDIO RECORDER INSTALL SUCCESSFUL\n This does not work yet, please create a config.json file and restart the service (or run the install script again)"
    else
        printf "\nABORT : GIT CLONE MAY HAVE FAILED"
    fi
else
    printf "ABORT : CANNOT FIND DIRECTORY /home/ccninfo"
fi
