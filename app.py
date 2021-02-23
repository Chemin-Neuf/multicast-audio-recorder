from flask import Flask, render_template, jsonify, request, send_from_directory
from inspect import signature
import record, sdp_writer, schedule_recording, discover_device, auto_record
import threading

app = Flask(__name__)

autorec_thread = None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/json/<action>', methods=['GET', 'POST'])
def run_action(action):
    global autorec_thread

    params = request.json

    # get the action function to execute
    fn = None
    if hasattr(record, action):
        fn = getattr(record, action)
    elif hasattr(sdp_writer, action):
        fn = getattr(sdp_writer, action)
    elif hasattr(schedule_recording, action):
        fn = getattr(schedule_recording, action)
    elif hasattr(discover_device, action):
        fn = getattr(discover_device, action)
    elif hasattr(auto_record, action):
        fn = getattr(auto_record, action)
    elif action == 'start_autorec':
        autorec_thread = threading.Thread(target=auto_record.start_process)
        autorec_thread.start()
        return {'autorec_started': True}
    elif action == 'stop_autorec':
        if not autorec_thread: return {'autorec_stopped': True, 'already_stopped': True}
        return {'autorec_stopped': auto_record.stop_process()}
    if fn == None: return {'error': 'ACTION_NOT_FOUND', 'details': 'Action '+str(action)+' was not found'}

    # get action parameters and execute the action function
    res = None
    if params != None and len(params) > 0:
        sig = signature(fn)
        nb_params = len(sig.parameters)
        params[:nb_params]
        try:
            res = fn(*params)
        except Exception as err:
            print('Action "'+action+'" error:')
            print(err)
            return jsonify(result = {'error': 'ERROR', 'details': str(err), 'action': action, 'args': params})
    else:
        try:
            res = fn()
        except Exception as err:
            return jsonify(result = {'error': 'ERROR', 'action': action, 'details': str(err)})

    return jsonify(result = res)

@app.route('/data/<filename>')
def serve_recording(filename):
    return send_from_directory('data', filename)




if __name__ == "__main__":
    app.run()