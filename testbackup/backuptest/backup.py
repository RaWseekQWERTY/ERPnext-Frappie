import subprocess
import logging
import os
import time
import glob
# import smtplib
# from dotenv import load_dotenv

# load_dotenv()

now = time.time()
logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO
)

def create_backup(sitename):
    try:
        
        result = subprocess.run(['bench', '--site', sitename, 'backup'], check=True)
        logging.info(f'Successfully created backup for {sitename}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error creating backup for {sitename}: {e}')

def check_older_files(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        # if file is 1 day old then remove
        if os.path.getmtime(file_path) < now - 1 * 86400:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f'Removed file: {filename}')

def copy_backup(files, remote_path):
    logging.info("Copying backup")
    try:
        for file in files:
            subprocess.run(['rclone', 'copy', file, remote_path], check=True)
            logging.info(f'Successfully copied backup file {file} to {remote_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error copying backup for {file}: {e}')

def main():
    path = r'/home/cas/frappe-bench/sites/cas.com.np/private/backups'
    source_dir = '/home/cas/frappe-bench/sites/cas.com.np/private/backups'
    files = list(glob.iglob(os.path.join(source_dir, "*.gz")))
    remote_path = 'erpBackup:/home/cas/Downloads'
    create_backup('cas.com.np',source_dir)
    check_older_files(path)
    copy_backup(files, remote_path)

if __name__ == "__main__":
    main()
