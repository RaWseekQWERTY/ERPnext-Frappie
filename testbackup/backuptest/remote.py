import subprocess
import os
import glob
import frappe
from frappe.core.doctype.communication.email import make
from datetime import datetime

def take_backup(site_name):
    try:
        # Run the bench backup command
        subprocess.run(['bench', '--site', site_name, 'backup', '--with-files'], check=True)
        print("Backup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        send_failure_email(site_name, str(e))
        return None

    # Identify the latest backup file
    backup_dir = f'./sites/{site_name}/private/backups/'
    list_of_files = glob.glob(os.path.join(backup_dir, '*.sql*'))
    if not list_of_files:
        print("No backup files found.")
        send_failure_email(site_name, "No backup files found.")
        return None
    
    # Filter files created today and delete older backups
    delete_older_backups(list_of_files)

    latest_backup_file = max(list_of_files, key=os.path.getctime)
    return latest_backup_file

def delete_older_backups(list_of_files):
    today_date = datetime.today().strftime('%Y%m%d')
    
    for file_path in list_of_files:
        file_name = os.path.basename(file_path)
        if today_date not in file_name:
            try:
                os.remove(file_path)
                print(f"Deleted old backup file: {file_path}")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")

def send_backup_to_remote(backup_file, remote_location):
    try:
        # Use rclone to transfer the file
        subprocess.run(['rclone', 'copy', backup_file, remote_location], check=True)
        print("Backup transferred to remote server successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during file transfer: {e}")
        send_failure_email("cas.com.np", str(e))

def send_failure_email(site_name, error_message):
    recipient = "admin@example.com"
    subject = f"Backup Failure for Site {site_name}"
    message = f"The backup process for site {site_name} has failed.\n\nError Message:\n{error_message}"
    
    try:
        # Create the email
        make(subject=subject, content=message, recipients=recipient).send()
        print("Failure notification email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    print("Starting backup process for site: cas.com.np")

    # Take the backup
    backup_file = take_backup("cas.com.np")
    
    if backup_file:
        # If backup is successful, send it to the remote location
        send_backup_to_remote(backup_file, "erpBackup:/home/cas/Downloads")
    else:
        print("Backup process failed. No files to transfer.")

    print("Backup process completed.")

if __name__ == "__main__":
   
    # Call the main function
    main()
