printf "UPDATING MULTICAST AUDIO RECORDER..."

# save current config.json in a temp dir
if [[ -f "/home/ccninfo/multicast-audio-recorder/config.json" ]]; then
    printf "\nsaving current config.json\n"
    cp /home/ccninfo/multicast-audio-recorder/config.json /home/ccninfo/config.json 
else
    printf "\n/!\\ NO config.json FILE WAS FOUND, PLEASE COPY ONE MANUALLY IN /home/ccninfo/multicast-audio-recorder/\n"
fi

# pull the latest commit
cd /home/ccninfo/multicast-audio-recorder
git reset --hard origin/main
chmod +x /home/ccninfo/multicast-audio-recorder/start.sh
chmod +x /home/ccninfo/multicast-audio-recorder/start_dev.sh
chmod +x /home/ccninfo/multicast-audio-recorder/recorder_update.sh
chmod +x /home/ccninfo/multicast-audio-recorder/recorder_install.sh

# check that all packages are properly installed
sudo apt-get update && sudo apt-get install -y git ffmpeg python3-venv python3-pip
pip3 install Flask python-dateutil

# copy latest version of the .service file
cp /home/ccninfo/multicast-audio-recorder/audio-recorder.service /etc/systemd/system/audio-recorder.service
sudo systemctl daemon-reload

# create the data dir where local recordings will be stored
if [[ ! -d "/home/ccninfo/multicast-audio-recorder/data" ]]; then
    mkdir /home/ccninfo/multicast-audio-recorder/data
fi

# restore the config.json
printf "\nrestoring config.json\n"
mv /home/ccninfo/config.json /home/ccninfo/multicast-audio-recorder/config.json

# restart the service and show the status
sudo systemctl restart audio-recorder.service
sudo systemctl status audio-recorder.service

printf "\nAUDIO RECORDER UPDATE FINISHED\n"


