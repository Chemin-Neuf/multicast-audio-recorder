


## Setup

First test that the multicast is listenable from your server : `tcpdump -c 10 multicast` should return a few lines

### Install frfmpeg

`sudo apt-get install ffmpeg`

### Install Flask webserver

see https://linuxize.com/post/how-to-install-flask-on-ubuntu-18-04/ :
- `sudo apt install python3-venv`
- cd in this repo root directory
- `python3 -m venv venv` creates a new python3 virtual env in a folder called venv
- `source venv/bin/activate` activates the python3 virtual env
- `pip3 install Flask python-dateutil` install Flask webserver and dateutil for dates manipulation
- `python -m flask --version` check Flask installation

### Prerequisites

- `mkdir data` at the root of this repo. this is where local recordings will be stored

### Start the web server

- `source venv/bin/activate` activate python virtual env
- `export FLASK_APP=app.py` sets up the web app entry point
- `export FLASK_ENV=development` or "production" for production app
- `flask run --host=0.0.0.0` runs the web server (the 0.0.0.0 is to make the web server available to anyone)

or run `start.sh` (you can make it executable by running `chmod +x start.sh`)


### Register start.sh as a service

To register the web app as a service an linux, 
- modify **audio-recorder.service** as needed (with the proper absolute path to the start.sh script)
- copy the **audio-recorder.service** file in `/etc/systemd/system/`
- make it executable with `sudo chmod u+x /etc/systemd/system/audio-recorder.service`
- `sudo systemctl enable audio-recorder.service`
- `sudo systemctl start audio-recorder.service`
- `sudo systemctl status audio-recorder.service` to check if the service is running

## Documentation and tutorials

- to create a Flask webapp : https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-fr
- https://superuser.com/questions/1183663/determining-audio-level-peaks-with-ffmpeg
- https://gist.github.com/jn0/8b98652f9fb8f8d7afbf4915f63f6726