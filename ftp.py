import ftplib, json, os


# load FTP config
ftp_config = {}
with open('config.json') as json_file:
    ftp_config = json.load(json_file)
    ftp_config = ftp_config['ftp']

'''
Saves a local file to the remote FTP working directory
'''
def save_file(local_path):
    global ftp_config
    if not os.path.exists(local_path): return {'error': 'SOURCE_FILE_NOT_FOUND', 'msg': 'The source file '+local_path+' was not found'}
    ftp = ftplib.FTP(host = ftp_config['host'], user = ftp_config['user'], passwd = ftp_config['pass'])
    ftp.encoding = 'utf-8'
    filename = os.path.basename(local_path)
    with open(local_path, "rb") as file:
        ftp.storbinary("STOR "+os.path.join(ftp_config['working_dir'], filename), file)
    ftp.cwd(ftp_config['working_dir'])
    return filename in ftp.nlst()

def remove_file(remote_path):
    return "TODO"



'''
Lists all files in remote working directory
'''
def list_files():
    return "TODO"


'''
Copies a remote file in /data and returns a download url to download the file
'''
def get_file_url(remote_file):
    return "TODO"