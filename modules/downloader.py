import subprocess
import os
import time
import configparser
import re
from datetime import datetime

class Foldownloader:
    def __init__(self, config_file="config.cfg", max_retries: int = 2, retry_delay: int = 5):
        # Load config
        cfg = configparser.ConfigParser()
        read_files = cfg.read(config_file)
        if not read_files:
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # WinSCP 
        self.winscp_exe_path    = cfg.get('FTP', 'winscp_exe_path').strip('"')
        self.winscp_script_path = cfg.get('FTP', 'winscp_script_path').strip('"')
        self.ftp_host           = cfg.get('FTP', 'ftp_host').strip('"')
        self.ftp_port           = cfg.get('FTP', 'ftp_port').strip('"')
        self.ftp_username       = cfg.get('FTP', 'ftp_username').strip('"')
        self.ftp_password       = cfg.get('FTP', 'ftp_password').strip('"')  
        self.host_key           = cfg.get('FTP', 'host_key').strip('"')

        # Remote directories
        self.remote_directory_fol       = cfg.get('FTP', 'remote_directory_fol').strip('"')
        self.remote_directory_indicator = cfg.get('FTP', 'remote_directory_indicator').strip('"')

        # Local daily folder: data/FOL/YYYYMMDD
        today_str = datetime.now().strftime('%Y%m%d')
        self.local_directory = os.path.join("data", "FOL", today_str)
        os.makedirs(self.local_directory, exist_ok=True)

        # Retry config
        self.max_retries = int(max_retries)
        self.retry_delay = int(retry_delay)

        # Quick status
        print(f"[Downloader] Initialized.")
        print(f"  Local directory: {self.local_directory}")
        print(f"  Remote FOL dir : {self.remote_directory_fol}")
        print(f"  Remote IND dir : {self.remote_directory_indicator}")
        print(f"  Host (port)    : {self.ftp_host}:{self.ftp_port}")
        print("  NOTE: config.cfg must be in .gitignore to avoid leaking credentials.")

    def download_files(self):
        """Download FOL files (*.zip and *.md5) from FOL remote folder."""
        patterns = ["*.zip", "*.md5"]
        print("[Downloader] Starting download of FOL files...")
        return self._download_from_remote(patterns, self.remote_directory_fol, "FOL main files")

    def download_indicator_files(self):
        """Download indicator files from indicator remote folder."""
        patterns = ["indicatori-sintetici-di-qualita-*", "indicatori-sintetici-di-qualita-capi-*"]
        print("[Downloader] Starting download of indicator files...")
        return self._download_from_remote(patterns, self.remote_directory_indicator, "Indicator files")

    def _download_from_remote(self, patterns, remote_directory, description="files"):
        """
        Create and run WinSCP script to download `patterns` from `remote_directory`.
        Uses authentication via ftp://username:password@host:port and get -resume to avoid re-downloads.
        """
        # Build URL with credentials (be aware this exposes credentials in the script file & logs)
        host_with_port = f"{self.ftp_host}:{self.ftp_port}"
        ftp_url = f'ftp://{self.ftp_username}:{self.ftp_password}@{host_with_port}'

        # Build script lines
        script_lines = [
            "option batch abort",
            "option confirm off",
            # open with credentials; hostkey is added for security if available
            f'open "{ftp_url}" -hostkey="{self.host_key}"',
            f'lcd "{self.local_directory}"',
            f'cd "{remote_directory}"'
        ]
        # Use -resume flag for get to resume partial files and skip fully downloaded files
        for p in patterns:
            # get -resume "pattern"
            script_lines.append(f'get -resume "{p}"')
        script_lines.extend(["close", "exit"])

        # Write script to configured path
        script_path = self.winscp_script_path
        with open(script_path, 'w', encoding='utf-8') as fh:
            fh.write("\n".join(script_lines))
        print(f"[Downloader] WinSCP script written ({description}): {script_path}")

        # Command to run WinSCP
        cmd = [
            self.winscp_exe_path,
            f'/script={script_path}',
            '/log=winscp_log.txt',
            '/ini=nul',
            '/quiet'
        ]

        # Retry loop
        attempt = 0
        while attempt <= self.max_retries:
            try:
                attempt += 1
                print(f"[Downloader] Running WinSCP (attempt {attempt}) for {description}...")
                subprocess.run(cmd, check=True)
                print(f"[Downloader] WinSCP finished for {description}.")
                # Post-process: remove numeric timestamp prefix from downloaded filenames
                self._clean_filenames()
                return True
            except subprocess.CalledProcessError as e:
                print(f"[Downloader] WinSCP error on attempt {attempt}: {e}")
                if attempt > self.max_retries:
                    print("[Downloader] Max retries reached — failing.")
                    raise
                print(f"[Downloader] Retrying after {self.retry_delay}s...")
                time.sleep(self.retry_delay)
            except Exception as e:
                print(f"[Downloader] Unexpected error on attempt {attempt}: {e}")
                raise

    def _clean_filenames(self):
        """Remove leading timestamp digits and optional underscore from filenames in local_directory."""
        renamed = 0
        for fname in os.listdir(self.local_directory):
            old_path = os.path.join(self.local_directory, fname)
            if not os.path.isfile(old_path):
                continue
            # pattern: leading digits (timestamp) optionally followed by underscore; keep remainder
            new_fname = re.sub(r'^\d+_?', '', fname)
            new_path = os.path.join(self.local_directory, new_fname)
            # Avoid overwriting: if new_path exists, skip rename and leave original (you can adjust this behavior)
            if old_path != new_path and not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"[Downloader] Renamed '{fname}' -> '{new_fname}'")
                renamed += 1
            elif old_path != new_path and os.path.exists(new_path):
                print(f"[Downloader] Skipped renaming '{fname}' because '{new_fname}' already exists.")
        print(f"[Downloader] Filename cleaning done. Total renamed: {renamed}")
