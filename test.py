
import auto_record, lib


# auto_record.start_state(0)
# print(auto_record.get_db_level())


# print(lib.psGrep('ffmpeg'))

# To get DB LEVELS
# see https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
import subprocess
import sys
process = subprocess.Popen("ffmpeg -protocol_whitelist rtp,file,udp -nostats -i source.sdp -filter_complex ebur128=peak=true -f null -", stdout=subprocess.PIPE)
for c in iter(lambda: process.stdout.read(1), b''): 
    # sys.stdout.buffer.write(c)
    print("ok")