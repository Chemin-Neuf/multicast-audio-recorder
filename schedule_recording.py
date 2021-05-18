import record
from threading import Timer
from datetime import datetime, timedelta
import dateutil.parser

'''
In this module we schedule the recordings (start and stop)
'''


timers = {
    'stop_recording': {'timer': None, 'end_timestamp': None},
}


def reset_timers():
    global timers
    timers = {
        'stop_recording': {'timer': None, 'end_timestamp': None},
    }



'''
Adds nb_sec to the current stop_recording timer
'''
def schedule_stop_recording_add_seconds(nb_sec):
    global timers

    if nb_sec == 0: return None
    status = record.status_recording()

    # unschedule previous stop_recording timer
    if isinstance(timers['stop_recording'], dict) and timers['stop_recording']['timer'] != None:
        timers['stop_recording']['timer'].cancel()

    # if no recording ongoing, we return
    if status['status'] != 'recording': 
        record.add_status({'schedule_stop_recording': None})
        return {'error': 'NOT_RECORDING', 'msg': 'You can add a stop timer only while recording'}

    # we add end_timestamp if the timer is not set already
    if timers['stop_recording']['end_timestamp'] == None:
        timers['stop_recording']['end_timestamp'] = datetime.utcnow()

    # we add nb_sec to the end_timestamp
    timers['stop_recording']['end_timestamp'] += timedelta(seconds=nb_sec)

    # we just keep the timer cancelled if end_timestamp has already expired
    if timers['stop_recording']['end_timestamp'] <= datetime.utcnow():
        timers['stop_recording'] = {'timer': None, 'end_timestamp': None}
        record.add_status({'schedule_stop_recording': None})
        return {'error': 'EXPIRED'}

    # start Timer
    def aux_stop():
        record.stop_recording()
        record.add_status({'schedule_stop_recording': None})
        timers['stop_recording'] = {'timer': None, 'end_timestamp': None}
    t = Timer((timers['stop_recording']['end_timestamp'] - datetime.utcnow()).total_seconds(), aux_stop)
    t.start()

    # save new timer
    timers['stop_recording']['timer'] = t

    # save status
    record.add_status({'schedule_stop_recording': timers['stop_recording']['end_timestamp'].isoformat()})

    return timers['stop_recording']['end_timestamp']


'''
Schedules to stop the recording in nb_sec seconds
'''
def schedule_stop_recording(nb_sec):
    global timers

    # unschedule previous stop_recording timer
    if isinstance(timers['stop_recording'], dict) and timers['stop_recording']['timer'] != None:
        timers['stop_recording']['timer'].cancel()
        timers['stop_recording'] = {'timer': None, 'end_timestamp': None}

    # we just cancel the timer if nb_sec <= 0
    if nb_sec <= 0:
        return timers['stop_recording']

    # start Timer
    t = Timer(nb_sec, record.stop_recording)
    t.start()

    # save new timer
    end_t = (datetime.utcnow() + timedelta(seconds=nb_sec)).isoformat()
    timers['stop_recording'] = {'timer': t, 'end_timestamp': end_t}

    # save status
    record.add_status({'schedule_stop_recording': end_t})
    return timers['stop_recording']