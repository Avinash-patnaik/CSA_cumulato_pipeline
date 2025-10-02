import subprocess
import re
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
            """ Download main FOL files from FOL remote folder"""
            target_patterns = ["*.zip", "*.md5"]
            self._run_winscp(target_patterns, self.remote_directory_fol, description="FOL files")  
            
    def download_indicators(self):
        """ Download main FOL files from FOL remote folder"""
        target_patterns = [
                "indicatori-sintetici-di-qualita-*",
                "indicatori-sintetici-di-qualita-capi-*"
            ]  
        self._run_winscp(target_patterns, self.remote_directory_indicator, description="Indicator files")
    
    def _run_winscp(self, target_patterns, remote_directory, description="files"):
        """ Helper to create and run WinSCP script"""
        script_lines = [
            "option batch abort",
            "option confirm off",
            f'open "{self.ftp_host}" -hostkey="{self.host_key}"'
            f'lcd "{self.local_directory}"',
            f'cd "{remote_directory}"'
        ]
        
        for pattern in target_patterns:
            script_lines.append(f'get "{pattern}"')
        script_lines.extend(["close", "exit"])

        # Write script
        with open(self.winscp_script_path, 'w') as f:
            f.write("\n".join(script_lines))
        print(f"[Downloader] WinSCP script written for {description}")
        
        # Run script
        cmd = [
            self.winscp_exe_path,
            f'/script:{self.winscp_script_path}',
            '/log=winscp_log.txt',
            '/ini=nul',
            '/quiet',
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"[Downloader] {description} downloaded successfully to {self.local_directory}")

            # Remove timestamp prefix in filenames
            for filename in os.listdir(self.local_directory):
                new_name = re.sub(r'^\d+_', '', filename)
                old_path = os.path.join(self.local_directory, filename)
                new_path = os.path.join(self.local_directory, new_name)
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    print(f"[Downloader] Renamed '{filename}' -> '{new_name}'")

        except subprocess.CalledProcessError as e:
            print(f"[Downloader] WinSCP error while downloading {description}: {e}")
            raise
        except Exception as e:
            print(f"[Downloader] Unexpected error while downloading {description}: {e}")
            raise
            