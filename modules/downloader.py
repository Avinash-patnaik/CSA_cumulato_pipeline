import subprocess
import os
import time
import configparser
from datetime import datetime

class FOLDownloader:
    def __init__(self, config_file="config.cfg", max_retries: int = 2, retry_delay: int = 5):
        # Load configuration
        cfg = configparser.ConfigParser()
        if not cfg.read(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # SFTP credentials and paths
        self.winscp_exe_path    = cfg.get('FTP', 'winscp_exe_path').strip('"')
        self.winscp_script_path = cfg.get('FTP', 'winscp_script_path').strip('"')
        self.ftp_host           = cfg.get('FTP', 'ftp_host').strip('"')
        self.ftp_port           = cfg.get('FTP', 'ftp_port').strip('"')
        self.ftp_username       = cfg.get('FTP', 'ftp_username').strip('"')
        self.ftp_password       = cfg.get('FTP', 'ftp_password').strip('"')

        # Remote directories
        self.remote_directory_fol       = cfg.get('FTP', 'remote_directory_fol').strip('"')
        self.remote_directory_indicator = cfg.get('FTP', 'remote_directory_indicator').strip('"')

        # Today's folder
        today_str = datetime.now().strftime('%Y%m%d')
        self.today_str = today_str
        self.local_directory = os.path.join("data", "FOL", today_str)
        os.makedirs(self.local_directory, exist_ok=True)

        # Retry config
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        print(f"[FOLDownloader] Initialized.")
        print(f"  Local dir  : {self.local_directory}")
        print(f"  SFTP server: {self.ftp_host}:{self.ftp_port}")
        print(f"  Remote FOL : {self.remote_directory_fol}")
        print(f"  Remote IND : {self.remote_directory_indicator}")

    def download_files(self):
        """Download main FOL files for today (*.zip and *.md5)"""
        patterns = [f"{self.today_str}*.zip", f"{self.today_str}*.md5"]
        print("[FOLDownloader] Downloading FOL main files...")
        return self._download_from_remote(patterns, self.remote_directory_fol, "FOL main files")

    def download_indicator_files(self):
        """Download indicator files for today"""
        patterns = [
            f"indicatori-sintetici-di-qualita-{self.today_str}*",
            f"indicatori-sintetici-di-qualita-capi-{self.today_str}*"
        ]
        print("[FOLDownloader] Downloading indicator files...")
        return self._download_from_remote(patterns, self.remote_directory_indicator, "Indicator files")

    def _download_from_remote(self, patterns, remote_directory, description="files"):
        """
        Create and run WinSCP script to download files via SFTP.
        """
        # Build SFTP URL
        ftp_url = f'sftp://{self.ftp_username}:{self.ftp_password}@{self.ftp_host}:{self.ftp_port}'

        # Generate WinSCP script
        script_lines = [
            "option batch abort",
            "option confirm off",
            f'open {ftp_url}',                # Open SFTP connection
            f'lcd "{self.local_directory}"',  # Local folder
            f'cd "{remote_directory}"'        # Remote folder
        ]
        for pattern in patterns:
            script_lines.append(f'get -resume "{pattern}"')  # Download matching files
        script_lines.extend(["close", "exit"])

        # Write script file
        with open(self.winscp_script_path, "w", encoding="utf-8") as f:
            f.write("\n".join(script_lines))
        print(f"[FOLDownloader] WinSCP script written: {self.winscp_script_path}")

        # WinSCP command
        cmd = [
            self.winscp_exe_path,
            f'/script={self.winscp_script_path}',
            '/log=winscp_log.txt',
            '/ini=nul',
            '/quiet'
        ]

        # Retry loop
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"[FOLDownloader] Attempt {attempt} - running WinSCP for {description}...")
                subprocess.run(cmd, check=True)
                print(f"[FOLDownloader] {description} downloaded successfully.")
                return True
            except subprocess.CalledProcessError as e:
                print(f"[FOLDownloader] Error on attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    raise
                print(f"[FOLDownloader] Retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)

        return False
