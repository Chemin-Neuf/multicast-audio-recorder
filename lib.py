import subprocess, re, os, signal

'''
runs a ps -A | grep [s]
and returns the list of pids returned by the command
'''
def psGrep(s):
    cmd = ['ps', '-A']
    ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    ps.wait()
    output = subprocess.check_output(('grep', s), stdin=ps.stdout)
    output_s = output.decode('utf-8').strip()
    pid_list = list(map(lambda l: int(l[1]), re.findall(r"(^|\n)(\d+)", output_s)))
    return pid_list


'''
uses psGrep to kill all corresponding processes
'''
def killGrep(s):
    proc_list = psGrep(s)
    for pid in proc_list:
        os.kill(pid, signal.SIGTERM)
    return proc_list
