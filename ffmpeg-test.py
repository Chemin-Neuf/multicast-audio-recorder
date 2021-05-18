import ffmpeg, os

# ffmpeg -protocol_whitelist rtp,file,udp -i source.sdp -c:a pcm_s24le -af asetnsamples=44100,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=" + audio_level_file + " -f null -
# stream = ffmpeg.input('source.sdp')
# stream = ffmpeg.filter(filter_name='astats', metadata=1)
# stream = ffmpeg.output('-', format='null')

# ffmpeg.run(stream)
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'protocol_whitelist;file,rtp,udp'
(
    ffmpeg
    .input('source.sdp')
    .filter('astats', metadata=1)
    .output('-', format='null')
    .run()
)