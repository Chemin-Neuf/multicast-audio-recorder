import os, re

sdp_path = os.path.dirname(os.path.realpath(__file__)) + "/source.sdp"

def write_sdp(data):
    global sdp_path
    channels = "96"
    channel_nb = "1"
    print(data)
    if str(data["channels"]) == "98": 
        channels = "98"
        channel_nb = "2"
    elif str(data["channels"]) == "97": 
        channels = "97"
        channel_nb = "2"
    print(channels)
    with open(sdp_path, 'w') as f:
        f.write("v=0\n")
        f.write("m=audio {} RTP/AVP {}\n".format(data['port'], channels))
        f.write("c=IN IP4 {}/32\n".format(data['multicast_ip']))
        f.write("a=rtpmap:{} L{}/{}/{}\n".format(channels, data['bit_depth'], data['sample_rate'], channel_nb))
    with open(sdp_path) as f:
        return f.read()

def parse_sdp():
    global sdp_path
    if not os.path.exists(sdp_path): return []
    with open(sdp_path) as f:
        content = f.read()
        return {
            'port': re.findall(r"^m=audio\s+([0-9]{1,5})\s+RTP\/AVP", content, re.MULTILINE)[0],
            'channels': re.findall(r"^m=audio\s+[0-9]{1,5}\s+RTP\/AVP\s(96|97|98)", content, re.MULTILINE)[0],
            'multicast_ip': re.findall(r"^c=IN\s+IP4\s+([^\s\/]+)\/", content, re.MULTILINE)[0],
            'bit_depth': re.findall(r"^a=rtpmap:[0-9]+\s+L([0-9]{1,2})[\s\/]", content, re.MULTILINE)[0],
            'sample_rate': re.findall(r"^a=rtpmap:[0-9]+\s+L[0-9]{1,2}[\s\/]([0-9]+)[\s\/]", content, re.MULTILINE)[0],
            'raw_content': content,
        }
