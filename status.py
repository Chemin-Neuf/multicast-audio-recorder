'''
Here we manage the app state
'''


import json, os, re, subprocess
from pathlib import Path
from datetime import datetime



# class State:

#     name = ''
#     state_zero = {}
#     data = {}

#     def __init__(self, name, opt = {}):
#         self.name = name
#         if 'state_zero' in opt:
#             self.state_zero = opt['state_zero']
#         if 'data' in opt:
#             self.data = opt['data']
#         return

#     '''
#     Be careful when using this ! A process may be running and its pid may be lost
#     '''
#     def set(self, status = None):
#         if status == None:
#             status = {}
#         with open(self.name + '.json', 'w') as outfile:
#             json.dump(status, outfile, indent=4)
#         return status

#     '''
#     Writes some app status data to disk
#     '''
#     def add(self, data):
#         status = self.get()
#         with open(self.name + '.json', 'w') as outfile:
#             status.update(data)
#             json.dump(status, outfile, indent=4)
#         return status

#     '''
#     Gets the state as a dict
#     '''
#     def get(self):
#         file = self.name + '.json'
#         if not os.path.exists(file):
#             return self.state_zero
#         # we open the status file
#         with open(file) as json_file:
#             data = json.load(json_file)
#             if data == None: data = self.state_zero
#             return data



def get_state(name):
    file = name + '.json'
    if not os.path.exists(file): return {}
    with open(file) as json_file:
        try:
            data = json.load(json_file)
            if data == None: return {}
            return data
        except:
            return {}

def add_state(name, data):
    status = get_state(name)
    with open(name + '.json', 'w') as outfile:
        status.update(data)
        json.dump(status, outfile, indent=4)
    return status



'''
Be careful when using this ! A process may be running and its pid may be lost
'''
def set_status(status = None):
    if status == None:
        status = {
            'status': "init",
            'pid': None,
            'filename': '',
            'filepath': '',
        }
    with open('status.json', 'w') as outfile:
        json.dump(status, outfile, indent=4)
    return status


'''
Writes some app status data to disk
'''
def add_status(data):
    global status
    status = status_recording()
    with open('status.json', 'w') as outfile:
        status.update(data)
        json.dump(status, outfile, indent=4)
    return status


def status_recording(status_name = None):
    status_file = 'status.json' if not status_name else status_name + '.json'
    empty_status = {
        'status': "stopped",
        'pid': None,
        'filename': '',
        'filepath': '',
    }
    if not os.path.exists(status_file):
        return empty_status
    # we open the status file
    with open(status_file) as json_file:
        data = json.load(json_file)
        if data == None: data = empty_status

        # we get info about the last audio
        if os.path.isfile(data['filepath']):
            data['filesize'] = Path(data['filepath']).stat().st_size
        
        data['running'] = is_running(data['pid'])
        if data['status'] != 'recording':
            if not os.path.exists(data['filepath']):
                data['filepath'] = ''
                data['filename'] = ''
                data['filesize'] = 0
                set_status(data)
            else:
                data['ffmpeg'] = get_audio_file_info( data['filepath'])
        else:
            data['current_time'] = datetime.now().timestamp()
        # print(subprocess.run(['ps -A | grep '+str(data['pid'])], shell=True))
        return data


'''
Returns info about an audio file, based on ffmpeg -i [filepath] output
'''
def get_audio_file_info(filepath):
    p = subprocess.run(['ffmpeg', '-i', filepath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    raw_ffmpeg = p.stdout.decode("utf-8")
    data = {
        'duration': '',
        'bitrate': '',
        'codec': '',
        'sample_rate': '',
    }
    
    duration = re.findall(r"Duration\s*\:\s*(\d{2}\:\d{2}\:\d{2})", raw_ffmpeg, re.MULTILINE)
    if len(duration) > 0: data['duration'] = duration[0]

    bitrate = re.findall(r"bitrate\s*:\s*(\d+)\s+([^\s]+)\s", raw_ffmpeg, re.MULTILINE)
    if len(bitrate) > 0: data['bitrate'] = {'val': bitrate[0][0], 'unit': bitrate[0][1]}

    codec = re.findall(r"Audio\s*:\s*([^\s]+)\s", raw_ffmpeg, re.MULTILINE)
    if len(codec) > 0: data['codec'] = codec[0]

    res = re.findall(r"(\d+)\s+Hz\,\s*([^\,]+)\,\s*([^\,]+)\,", raw_ffmpeg, re.MULTILINE)
    if len(res) > 0: 
        data['sample_rate'] = res[0][0]
        data['channels'] = res[0][1]
        data['bit_depth'] = res[0][2]

    return data


def is_running(pid):
    if pid == None: return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True