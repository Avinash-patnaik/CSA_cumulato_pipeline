import ftplib
import os
from datetime import datetime, timedelta 
import configparser

class FTPdownloader:
    def  __int__(self, config_file="config.cfg"):
        
        # Config file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        self.winscp_exe_path    = self.config.get('FTP', 'winscp_exe_path').strip('"')
        self.winscp_script_path = self.config.get('FTP', 'winscp_script_path').strip('"')
        self.host_key           = self.config.get('FTP', 'host_key').strip('"')
        self.ftp_host           = self.config.get('FTP', 'ftp_host').strip('"')
        self.ftp_username       = self.config.get('FTP', 'ftp_username').strip('"')
        self.ftp_password       = self.config.get('FTP', 'ftp_password').strip('"')
        
        # Remote directories
        self.remote_directory_fol       = self.config.get('FTP', 'remote_directory_fol').strip('"')
        self.remote_directory_indicator = self.config.get('FTP', 'remote_directory_indicator').strip('"')
        
        # Create daily folder 
        today_str = datetime.now().strftime("%Y%m%d")
        self.local_directory = os.path.join("data", "FOL", today_str)
        os.makedirs(self.local_directory, exist_ok=True)
        print(f"[Downloader] Created local directory: {self.local_directory}")
        
    def download_files(self):
        print(f"[Downloader] connecting to FTP: {self.host} ...")
        with ftplib.FTP(self.host, self.user, self.password) as ftp:
            ftp.cwd(self.remote_path)
            remote_files = ftp.nlst()
            print(f"[Downloader] Found {len(remote_files)} files on FTP...")
            