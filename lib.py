import subprocess, re, os, signal, shutil

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


'''
Empties the folder
'''
def emptyFolder(folder_path):
    errors = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            errors.append('Failed to delete %s. Reason: %s' % (file_path, e))
    return errors