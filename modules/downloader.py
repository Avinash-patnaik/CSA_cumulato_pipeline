import ftplib
import os
from datetime import datetime, timedelta 
import configparser

class FTPdownloader:
    def  __int__(self, config_file="config.cfg"):
        
        # Config file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # FTP connection detials
        self.host = self.config.get("FTP", "host")
        self.user = self.config.get("FTP", "user")
        self.password = self.config.get("FTP", "password")
        self.port = self.config.get("FTP", "port")
        self.remote_path = self.config.get("FTP", "remote_path")
        
        # Local directory
        self.local_path = self.config.get("file paths", "download_path")
        os.makedirs(self.local_path, exist_ok=True)
        
        # yesterday date 
        yesterday = datetime.now() - timedelta(days=1)
        self.yesterday_str = yesterday.strftime("%Y%m%d")
        
        print(f"[Downloader] Config loaded. Download folder: {self.local_path}")
        print(f"[Downloader] Yesterday's date: {self.yesterday_str}")
        
    def download_files(self):
        print(f"[Downloader] connecting to FTP: {self.host} ...")
        with ftplib.FTP(self.host, self.user, self.password) as ftp:
            ftp.cwd(self.remote_path)
            remote_files = ftp.nlst()
            print(f"[Downloader] Found {len(remote_files)} files on FTP...")
            