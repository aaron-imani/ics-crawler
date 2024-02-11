import shelve

from threading import RLock

from utils import get_logger, get_urlhash, normalize
from utils.storage_check import does_shelve_exist, remove_shelve
from scraper import is_valid
import time
from urllib.parse import urlparse

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        self.lock = RLock()
        self.last_download_time = {}

        if not does_shelve_exist(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif does_shelve_exist(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            remove_shelve(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)


    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")
    

    def get_tbd_url(self):
        with self.lock:
            try:
                tbd_url = self.to_be_downloaded.pop()
                domain = urlparse(tbd_url).netloc
                if domain in self.last_download_time:
                    time_since_last_download = time.time() - self.last_download_time[domain]
                    if time_since_last_download < self.config.time_delay:
                        # Not enough time has passed since the last download from this domain.
                        # Put the URL back and try another one.
                        self.to_be_downloaded.append(tbd_url)
                        return self.get_tbd_url()
                return tbd_url
            except IndexError:
                return None


    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)

        with self.lock:
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                self.to_be_downloaded.append(url)

    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        with self.lock:
            if urlhash not in self.save:
                self.logger.error(f"Completed url {url}, but have not seen it before.")
            self.save[urlhash] = (url, True)
            self.save.sync()
            self.last_download_time[urlparse(url).netloc] = time.time()
