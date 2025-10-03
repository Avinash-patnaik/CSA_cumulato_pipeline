import sys
from modules.downloader import Foldownloader

def main():
    print("========== CSA Cumulato Pipeline ==========")
    try:
        # Initialize downloader
        downloader = Foldownloader(config_file="config.cfg")

        # Downloading FOL zip + md5 files
        downloader.download_files()

        # Downloading Indicator files
        downloader.download_indicator_files()

        print("✅ All downloads completed successfully.")
        print(f"Files saved in: {downloader.local_directory}")

    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
