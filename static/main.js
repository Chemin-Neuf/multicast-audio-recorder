/**
 * Clear local recordings folder
 * send to FTP
 */


const app = new Vue({
    el: "#app",
    data: {
        loading: {
            discoverDevice: false,
        },
        audio_title: '',
        recording_timer: {end_time: null, timer: null},
        recording: {
            status: 'init',
        },
        discoveredDevices: [],
        selectedDevice: -1,
        sdp: {},
        timer: null,
        notification: {type: 'info', msg: ''}
    },

    // on page load, we execute this
    async mounted() {
        await this.status()
        console.log('status', this.recording)
        if (this.recording.status == 'recording') this.timer = setInterval(_ => this.status(), 1000)
        this.sdpData() // get content of SDP file
        this.discoverDevice() // discover devices multicasting on the network
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

            // we get state of autorec
            this.autorecStatus();
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
        async autorecStatus() {
            this.loading.autorecStatus = true
            try {
                let res = await run_action('get_autorec_status')
                console.log('autorecStatus', res)
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.autorecStatus = false
        },
        async autorecStart() {
            this.loading.autorecStart = true
            try {
                let res = await run_action('start_autorec')
                console.log('autorecStart', res)
            } catch(e) {
                this.notify('error', e)
            }
            this.loading.autorecStart = false
        },
        async autorecStop() {
            this.loading.autorecStop = true
            try {
                let res = await run_action('stop_autorec')
                console.log('autorecStop', res)
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

