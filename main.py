from modules.downloader import FOLDownloader

def main():
    downloader = FOLDownloader(config_file="config.cfg")
    
    downloader.download_files()
    
    downloader.download_indicator_files()
    
if __name__ == "__main__":    
    main()