from time import sleep
import time
from datetime import datetime
from pathlib import Path
import subprocess, os, signal, json, ftp, re

from lib import emptyFolder, getConf
from status import set_status, add_status, status_recording, get_audio_file_info
import schedule_recording

CONF = getConf()

'''
Returns the list of local recordings
'''
def list_recordings():
    root_folder = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(root_folder, "/data")
    onlyfiles = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    return onlyfiles



'''
This function starts recording (audio) on the multicast address
'''
def start_recording(title = ""):
    global CONF
    if title == "": title = "audio"

    # checks whether a recording is already ongoing
    status = status_recording()
    if status['status'] == "recording":
        return {
            'error': 'ALREADY_RECORDING',
            'status': status,
        }

    # remove all files in the local recording folder
    recording_dir_path = os.path.dirname(os.path.realpath(__file__)) + "/data/"
    errors = emptyFolder(recording_dir_path)
    if (len(errors)): print(json.dumps(errors))
    
    # start recording
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_"+title+".wav")
    filepath = recording_dir_path + filename
    print('recording on file '+filepath)
    # checks if file exists already TODO
    # cmd = "vlc -vvv source.sdp --sout \"#transcode{acodec=s16l,channels=1}:std{access=file,mux=wav,dst="+filepath+"}\""
    cmd = "ffmpeg -protocol_whitelist rtp,file,udp -i source.sdp -c:a pcm_s24le \""+filepath+"\""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn = os.setsid)
    
    # save recording status in status.json
    status = {
        'status': 'recording',
        'start_time': datetime.now().timestamp(),
        'current_time': datetime.now().timestamp(),
        'pid': os.getpgid(p.pid),
        'filename': filename,
        'filepath': filepath,
    }
    add_status(status)
    # with open('status.json', 'w') as outfile:
    #     json.dump(status, outfile, indent=4)

    # wait a few seconds and show file size
    sleep(5)
    if os.path.isfile(status['filepath']):
        status['filesize'] = Path(status['filepath']).stat().st_size # in bytes
    return status

'''
This function stop an ongoing recording
'''
def stop_recording():

    status = status_recording()
    if not status['running']:
        status['status'] = 'stopped'
        with open('status.json', 'w') as outfile:
            json.dump(status, outfile, indent=4)
        return {'error': 'NOT_RECORDING', 'status': status}

    # kill the process
    res = os.killpg(status['pid'], signal.SIGTERM)

    # stop all recording timers
    schedule_recording.reset_timers()

    # save recording status
    status['status'] = "stopped"
    with open('status.json', 'w') as outfile:
        json.dump(status, outfile, indent=4)

    # push to ftp
    status['ftp_saved'] = save_recording()

    return status







'''
Saves a recording on the FTP drive
'''
def save_recording(filepath = None):
    status = status_recording()
    if filepath == None: filepath = status['filepath']
    if status['status'] == 'recording' and filepath == status['filepath']:
        print("ERROR : recording ongoing")
        return {'error': 'RECORDING_ONGOING', 'msg': 'Cannot save recording while it is being recorded'}
    success = ftp.save_file(filepath)
    if not success: 
        print('FAILED TO send file '+filepath+' to FTP')

    return success

'''
Removes local recordings that are too old
'''
def purge_local_recordings():
    now = time.time()
    data_dir = os.path.dirname(os.path.realpath(__file__)) + "/data/"
    for f in os.listdir(data_dir):
        if os.stat(os.path.join(data_dir, f)).st_mtime < now - 7 * 86400:
            print(f)
    return





'''
Removes a recording from local and FTP dirs
'''
def remove_recording(filepath = None, local_only = False):
    status = status_recording()
    if filepath == None: filepath = status['filepath']
    if status['status'] == 'recording' and filepath == status['filepath']:
        return {'error': 'RECORDING_ONGOING', 'msg': 'Cannot delete recording while recording on the same file !'}
    if os.path.exists(filepath):
        os.remove(filepath)
        if (os.path.exists(filepath)): return {'error': 'Cannot remove file '+filepath}
    if local_only: return True
    return True



# TODO delete this
def ps_old(pid):
    proc1 = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', pid], stdin=proc1.stdout,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
    out, err = proc2.communicate()
    print('out: {0}'.format(out))
    print('err: {0}'.format(err))
    return out

