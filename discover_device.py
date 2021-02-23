'''
Here we try to guess the multicast recorder config
'''

import os, subprocess, re

'''
Runs a detailed tcpdump to get the number of channels of a broadcast device
@param dict ip_dict     {ip: '...', port: '...'}
@return string
'''
def run_tcpdump_details(ip_dict):
    cmd = ['tcpdump', '-c', '1', 'host', ip_dict['ip'], 'and', 'port', ip_dict['port'], '-s0', '-v', '-X']
    ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    ps2 = subprocess.Popen(('grep', '0x0010:'), stdin=ps.stdout, stdout=subprocess.PIPE)
    output = subprocess.check_output(('cut', '-c43,44'), stdin=ps2.stdout)
    ps2.wait()
    channels = output.decode('utf-8').strip()

    return '96' if channels == '60' else '97'

'''
Runs a tcpdump to listen to any broadcast device
and returns the found broadcast ips as a list of dicts like [{ip:..., port:...}, ...]
'''
def run_tcpdump():
    cmd = ['tcpdump', '-c', '10', 'multicast']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').split("\n")
    line_model = {
        '_if': r"^\d", # consider only lines starting with a number
        'ip': r">\s+([\d\.]+)\.\d+\:",
        'port': r">\s+[\d\.]+\.(\d+)\:",
        #'raw_content': r"^(.+)$",
    }
    result = list(filter(lambda x: bool(x), map(lambda l: parse_line(l, line_model), lines)))

    # get only unique results
    mem = []
    result_unique = []
    for d in result:
        if d['ip']+d['port'] in mem: continue
        mem.append(d['ip']+d['port'])
        result_unique.append(d)

    # get the channels
    result = []
    for d in result_unique:
        d['channels'] = run_tcpdump_details(d)
        result.append(d)

    return result


def parse_line(line, line_model):
    d = {}

    # check if there is a condition
    if "_if" in line_model and not re.findall(line_model['_if'], line): return {}

    for (k, v) in line_model.items():
        if k[0] == '_': continue
        if isinstance(v, str):
            res = re.findall(v, line)
            if len(res): d[k] = res[0]
    return d

result = run_tcpdump()
print(result)