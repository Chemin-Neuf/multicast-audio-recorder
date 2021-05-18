# Update
if [[ -d "/home/ccninfo/multicast-audio-recorder" ]]
then
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
    git pull origin main
    chmod +x /home/ccninfo/multicast-audio-recorder/start.sh

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


# Install
else
    printf "INSTALLING MULTICAST AUDIO RECORDER..."
    printf "\nINSTALL GIT and other tools\n"
    sudo apt-get update && sudo apt-get install -y git ffmpeg python3-venv
    pip3 install Flask python-dateutil

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
fi