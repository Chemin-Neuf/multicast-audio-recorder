'''
Here we start a re-cording based on the DB level
'''

import os, sys, subprocess, signal, re
from time import sleep
from datetime import datetime
from pathlib import Path
from threading import Timer
from status import get_state, add_state, is_running


autorec_timers = {}
autorec_states = {}
true_recording = None
autorec_status = {'level': 0, 'state': -1}

autorec_stop = False


def get_autorec_status():
    return get_state('autorec')

# starts the main process of autorec
def start_process():
    global autorec_stop
    autorec_stop = False
    start_state(0)

# stops the main process of autorec
def stop_process():
    global autorec_stop
    autorec_stop = True
    timer_stop_recording('rec1', False)
    timer_stop_recording('rec2', False)
    autorec_status['state'] = -1
    add_state('autorec', {'state': -1})

    return True


'''
The state machine to handle the auto recording
'''
def start_state(n):
    global autorec_timers, autorec_states, autorec_status, true_recording, autorec_stop

    # stop everything if asked to
    if autorec_stop: return stop_process()

    autorec_status['state'] = n
    add_state('autorec', {'state': n})

    # we start the auto record state machine
    if n == 0:
        # start first recording
        start_recording('rec1')
        # start second recording after 5min
        t = Timer(5 * 60., lambda: start_recording('rec2'))
        t.start()
        start_state(1)

    # we are waiting for a high audio level to start true recording
    elif n == 1:
        # wait for audio level to be above threshold
        db_level = get_db_level()
        while db_level < -50:
            if autorec_stop: return stop_process()
            db_level = get_db_level()
            sleep(1)
        # check mean db level for 1min and see if it's ok
        add_state('autorec', {'state': 1.5})
        db_level = get_db_level(60)
        if db_level < -50:
            start_state(1)
        else:
            start_state(2)

    # we remove the timer to keep the recording going
    elif n == 2:
        # get oldest rec
        oldest_rec = 'rec1'
        newest_rec = 'rec2'
        if autorec_states['rec1'] == None or ('rec2' in autorec_states and not autorec_states['rec2'] == None and autorec_states['rec1']['start_date'] > autorec_states['rec2']['start_date']): 
            oldest_rec = 'rec2'
            newest_rec = 'rec1'
        true_recording = oldest_rec
        # remove its timer
        autorec_timers[oldest_rec].cancel()
        # cancel other newer recording
        timer_stop_recording(newest_rec, False)
        start_state(3)

    # wait for db_level dropping to stop recording
    elif n == 3:
        db_level = get_db_level()
        while db_level > -55:
            if autorec_stop: return stop_process()
            db_level = get_db_level()
            sleep(1)
        # wait 7min and see if db_level is still ok
        add_state('autorec', {'state': 3.5})
        db_level = get_db_level(7 * 60)
        if db_level > -55:
            start_state(3)
        else:
            start_state(4)

    # stop recording and start from scratch
    elif n == 4:
        timer_stop_recording('rec1', False)
        timer_stop_recording('rec2', False)
        start_state(0)


def start_recording(name):
    global autorec_timers, autorec_states

    timer_stop_recording(name)

    # start ffmpeg recording
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_autorec.wav")
    filepath = os.path.dirname(os.path.realpath(__file__)) + "/data/" + filename
    print('recording on file '+filepath)
    cmd = "ffmpeg -protocol_whitelist rtp,file,udp -i source.sdp -c:a pcm_s24le \""+filepath+"\""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn = os.setsid)

    # save state pid + timestamp
    autorec_states[name] = {'filepath': filepath, 'filename': filename, 'pid': os.getpgid(p.pid),  'start_date': datetime.now().timestamp()}
    add_state(name, autorec_states[name])

    # set timer to go off in 10min
    autorec_timers[name] = Timer(10 * 60., lambda: timer_stop_recording(name))
    autorec_timers[name].start()

    return

def timer_stop_recording(name, restart = True):
    global autorec_timers, autorec_states

    if name in autorec_timers: autorec_timers[name].cancel()

    # get status
    # status = get_state(name)
    status = autorec_states[name] if name in autorec_states else {}
    if not status or not 'pid' in status: return

    # kill ffmpeg
    res = os.killpg(status['pid'], signal.SIGTERM)
    sleep(1)

    # remove state
    autorec_states[name] = None
    add_state(name, {})

    # start fresh recording
    if restart: 
        # remove audio file
        if os.path.exists(status['filepath']):
            os.remove(status['filepath'])
        start_recording(name)


'''
Returns the current audio DB level
'''
def get_db_level(timespan = 4):
    global autorec_status

    audio_level_file = "audio_levels.txt"

    cmd = "ffmpeg -protocol_whitelist rtp,file,udp -i source.sdp -loglevel quiet -af asetnsamples=44100,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=" + audio_level_file + " -f null -"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn = os.setsid)
    sleep(timespan)
    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    sleep(1)
    
    # read the result from file
    with open(audio_level_file, "r") as f1:
        lines = f1.readlines()
        if not len(lines): return -201
        mean = 0.
        i = 0
        for l in lines:
            m = re.findall(r"RMS_level=(.+)$",l.strip())
            if not len(m) : continue
            mean += float(m[0])
            i += 1
        if i < 1: return -202
        autorec_status['level'] = mean / i

    add_state('autorec', {'level': autorec_status['level']})
    return autorec_status['level']




# def kill_watcher():
#     status_name = 'auto_record_status'
#     status = get_state(status_name)
#     if not 'pid_watcher' in status or not is_running(status['pid_watcher']): return

#     # kill the process
#     os.killpg(status['pid_watcher'], signal.SIGTERM)

#     # remove temp audio_levels file
#     # os.remove('audio_levels.txt')

#     # save recording status
#     add_state(status_name, {'pid_watcher': None})



