import subprocess
import logging
import os
import time
import glob
from datetime import datetime
from frappe.core.doctype.communication.email import make


logging.basicConfig(filename='backup_logging.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

now = time.time()

def create_backup(sitename):
    try:
        subprocess.run(['bench', '--site', sitename, 'backup',"--with-files"], check=True)
        logging.info(f'Successfully created backup for {sitename}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error creating backup for {sitename}: {e}')
        send_failure_email(sitename, f'Error creating backup: {e}')

def check_older_files(path):
    today = datetime.today().strftime('%Y%m%d')
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y%m%d')
        # Delete if the file is not created today
        if file_date != today:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    logging.info(f'Removed old backup file: {filename}')
                except OSError as e:
                    logging.error(f'Error deleting file {file_path}: {e}')

def copy_backup(files, remote_path):
    logging.info("Copying backup")
    try:
        for file in files:
            subprocess.run(['rclone', 'copy', file, remote_path], check=True)
            logging.info(f'Successfully copied backup file {file} to {remote_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error copying backup for {file}: {e}')
        send_failure_email(None, f'Error copying backup: {e}')

def send_failure_email(site_name, error_message):
    recipient = "admin@example.com"
    subject = f"Backup Failure for Site {site_name}" if site_name else "Backup Copy Failure"
    message = f"The backup process has failed.\n\nError Message:\n{error_message}"
    
    try:
        make(subject=subject, content=message, recipients=recipient).send()
        logging.info(f'Failure notification email sent for {site_name}')
    except Exception as e:
        logging.error(f'Error sending failure email: {e}')

def main():
    sitename = 'cas.com.np'
    path = f'/home/cas/frappe-bench/sites/{sitename}/private/backups'
    remote_path = 'erpBackup:/home/cas/Downloads'
    
    # Perform the backup
    create_backup(sitename)
    
    # Check and delete older files
    check_older_files(path)
    
    # Get today's backup files and copy them to the remote location
    patterns = ['*.sql.gz*','*.tar*','*.json']
    files = []
    
    for pattern in patterns:
        files.extend(glob.iglob(os.path.join(path, pattern)))
        
    # files = list(glob.iglob(os.path.join(path, pattern)))
    print(files)

    copy_backup(files, remote_path)

if __name__ == "__main__":
    main()

