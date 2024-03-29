/**
 * Clear local recordings folder
 * send to FTP
 */


const app = new Vue({
    el: "#app",
    data: {
        loading: {
            discoverDevice: false,
            getDbLevel: false,
        },
        audio_title: '',
        recording_timer: {end_time: null, timer: null},
        recording: {
            status: 'init',
        },
        autorec: {
            level: -200,
            state: -1,
        },
        discoveredDevices: [],
        selectedDevice: -1,
        sdp: {},
        timer: null,
        preferences: {},
        notification: {type: 'info', msg: ''}
    },

    // on page load, we execute this
    async mounted() {
        await this.status()
        console.log('status', this.recording)
        if (this.recording.status == 'recording') this.timer = setInterval(_ => this.status(), 1000)
        this.getAppPreferences() // load the app preferences (default recording time, ...)
        this.sdpData() // get content of SDP file
        this.discoverDevice() // discover devices multicasting on the network
        this.autorecStatus(); // we get state of autorec
        //this.getDbLevel(true)
    },

    // formatting filters
    filters: {
        duration: function(d) {
            if (!d) return '';
            let h = ('0' + Math.floor(d / 3600.)).slice(-2);
            let m = ('0' + Math.floor((d - h * 3600) / 60.)).slice(-2);
            let s = ('0' + Math.floor(d - h * 3600 - m * 60)).slice(-2);
            return `${h}:${m}:${s}`;//moment.duration(d, 'seconds')
        }
    },

    // the methods we will use for recording
    methods: {

        async updateRecordingTimeout(nb_sec) {
            if (this.recording.status != 'recording') return;
            this.loading.addRecordingTimeout = true
            try {
                let res = await run_action('schedule_stop_recording_add_seconds', [nb_sec])
                this.recording.schedule_stop_recording = res.result
                this.status()
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.addRecordingTimeout = false
        },

        // starts/stops a recording
        async toggleRecord() {
            return (this.recording.status == 'recording') ? this.stop() : this.record()
        },

        // starts a new recording
        async record() {
            if (this.loading.record) return console.log('already recording');
            this.loading = {...this.loading, record: true};
            // this.audio_title = "coco"
            console.log("recording...", this.loading.record)
            try {
                let res = await run_action('start_recording', [this.audio_title])
                this.recording = res.result
                this.timer = setInterval(_ => this.status(), 1000);
                // add a default timeout if it is set in the app preferences
                if (this.preferences.default_recording_time_minutes > 0) await this.updateRecordingTimeout(this.preferences.default_recording_time_minutes * 60)
            } catch(e) {
                notify('error', e)
            }
            this.loading.record = false
            console.log("done", this.loading)
        },

        // stops an ongoing recording
        async stop() {
            this.loading.stop = true
            try {
                let res = await run_action('stop_recording')
                this.recording = res.result
                this.audio_title = '';
                this.status()
                console.log('status', status)
                clearInterval(this.timer)
            } catch(e) {
                notify('error', e)
            }
            this.loading.stop = false
        },

        // get the current recording status
        async status() {
            let res = await run_action("status_recording");
            if (res.error) return this.notify("error", res);

            // parse filesize in MB
            res.result.filesize = Math.round(100 * res.result.filesize / (1024 * 1024)) / 100;
            // parse date ISO string in timestamp
            if (res.result.schedule_stop_recording) res.result.schedule_stop_recording = (new Date(res.result.schedule_stop_recording+'Z')).getTime() / 1000;
            // set audio title
            if (res.result.status == 'recording') this.audio_title = res.result.filename;
            this.recording = res.result;

            // we clear any residual status timer if no recording is ongoing
            if (this.recording.status != 'recording') clearInterval(this.timer);

            // we get the current recording duration
            this.recording.time = this.recording.current_time - this.recording.start_time;
        },

        // deletes the recording file
        async removeRecording() {
            this.loading.removeRecording = true
            try {
                let res = await run_action('remove_recording')
                await this.status()
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.removeRecording = false
        },

        /* ===================================== */
        /*          GET AUTOREC STATUS           */
        /* ===================================== */
        async getDbLevel(loop = false) {
            if (this.loading.getDbLevel) return
            this.loading.getDbLevel = true
            try {
                let res = await run_action('get_db_level')
                if (!loop) console.log('getDbLevel', res)
                this.autorec.level = res.result
            } catch(e) {
                this.notify('error', e)
            } finally {
                this.loading.getDbLevel = false
                if (loop && this.autorec.state == -1) setTimeout(_ => this.getDbLevel(loop), 5000)
            }
        },
        async autorecStatus(loop = false) {
            this.loading.autorecStatus = true
            try {
                let res = await run_action('get_autorec_status')
                this.autorec.level = res.result.level
                this.autorec.state = res.result.state
                if (this.autorec.state > -1) setTimeout(_ => this.autorecStatus(loop), 5000);
            } catch(e) {
                this.notify('error', e)
            } finally {
                this.loading.autorecStatus = false
                if (loop) setTimeout(_ => this.autorecStatus(loop), 5000)
            }
        },
        async autorecStart() {
            if (this.loading.autorecStart) return
            this.loading.autorecStart = true
            try {
                let res = await run_action('start_autorec')
                console.log('autorecStart', res)
                this.autorecStatus()
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.autorecStart = false
        },
        async autorecStop() {
            if (this.loading.autorecStop) return
            this.loading.autorecStop = true
            try {
                let res = await run_action('stop_autorec')
                console.log('autorecStop', res)
                this.autorecStatus()
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.autorecStop = false
        },

        /* ===================================== */
        /*       DISCOVER BROADCAST DEVICE       */
        /* ===================================== */
        async discoverDevice() {
            this.loading.discoverDevice = true
            try {
                let res = await run_action('run_tcpdump')
                console.log('discover device', res)
                this.discoveredDevices = res.result
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.discoverDevice = false
        },

        async chooseDevice() {
            if (this.selectedDevice < 0 || this.selectedDevice >= this.discoveredDevices.length) return;
            let device = this.discoveredDevices[this.selectedDevice]
            console.log('loading device', device)
            this.sdp.multicast_ip = device.ip
            this.sdp.port = device.port
            this.sdp.channels = device.channels
        },


        /* ===================================== */
        /*           SDP FILE MANAGEMENT         */
        /* ===================================== */

        async sdpData() {
            this.loading.sdpData = true
            try {
                let res = await run_action('parse_sdp')
                this.sdp = res.result;
                this.sdp.raw_content = this.sdp.raw_content.replace(/\n/g, '<br>')
            } catch(e) {
                notify('error', e)
            }
            this.loading.sdpData = false
        },

        async sdpSaveDate() {
            if (this.recording.status == 'recording') this.notify('error', 'Impossible de sauver le fichier SDP pendant un enregistrement')
            
            this.loading.sdpSaveDate = true
            try {
                let res = await run_action('write_sdp', [this.sdp])
                this.sdpData()
            } catch(e) {
                notify('error', e)
            }
            this.loading.sdpSaveDate = false
        },


        /* ===================================== */
        /*           GET APP PREFERENCES         */
        /* ===================================== */
        async getAppPreferences() {
            try {
                let res = await run_action('preferences')
                console.log("preferences result", res)
                if (res.result) this.preferences = res.result
            } catch(e) {
                notify('error', e)
            }
        },


        notify(type, msg) {
            this.notification = {type, msg}
            setTimeout(_ => this.notification = {type: 'info', msg: ''}, 7000)
        }

    }
});

async function run_action(action, params = null) {

  return new Promise((resolve, reject) => {
    $.ajax({
      url: $SCRIPT_ROOT + "/json/" + action,
      contentType: "application/json; charset=utf-8",
      type: "post",
      dataType: "json",
      data: JSON.stringify(params),
    })
      .fail((err) => {
        console.log("ERROR in ajax", err);
        reject(err);
      })
      .done((res) => {
        if (res.error) {
          console.log("ERROR ajax", res);
          return reject(res);
        }
        resolve(res);
      });
  });
}

function notify(type, msg) {
  $("#msg")
    .removeClass("error")
    .removeClass("success")
    .addClass(type)
    .html(JSON.stringify(msg));
}

$(document).ready(function() {
    $('[data-toggle]').each(function() {
        let cl = $(this).data('toggle')
        $(this).click(function() {
            $(this).toggleClass(cl)
        })
        $(this).find('.content').click(e => e.stopPropagation())
    })
})

