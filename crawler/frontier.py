import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty
from configparser import ConfigParser

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        self.last_visited = {}  # Store last visit time for each domain
        config_parser = ConfigParser()
        config_parser.read('config.ini')
        SIMILAR_PAGES_THRESHOLD = config_parser.getfloat('SCRAPER', 'SIMILAR_PAGES_THRESHOLD', fallback=0.9)

        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url, "")
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url, "")

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
        

    def _simhash(self, text):
        features = {}
        for word in text.split():
            features[word] = features.get(word, 0) + 1
        b = 64  
        hash_values = {word: hash(word) % b for word in features}
        vector = [0] * b
        for word, weight in features.items():
            hash_value = hash_values[word]
            for i in range(b):
                if (hash_value >> i) & 1:
                    vector[i] += weight
                else:
                    vector[i] -= weight
        fingerprint = 0
        for i in range(b):
            if vector[i] > 0:
                fingerprint |= (1 << i)
        return fingerprint

    def get_tbd_url(self):
        try:
            tbd_url = self.to_be_downloaded.pop()
            for existing_url, (_, _, existing_fingerprint) in self.save.items():
                similarity = self._calculate_similarity(existing_fingerprint, self.save[tbd_url][2])
                if similarity > self.SIMILARITY_THRESHOLD:
                    self.logger.info(f"Avoiding {tbd_url} as it is similar to {existing_url}")
                    return self.get_tbd_url() 
            return tbd_url
        except IndexError:
            return None


    def add_url(self, url, text):
        url = normalize(url)
        urlhash = get_urlhash(url)
        fingerprint = self._simhash(text)

        for existing_url, (_, _, existing_fingerprint) in self.save.items():
            similarity = self._calculate_similarity(existing_fingerprint, fingerprint)
            if similarity > self.SIMILARITY_THRESHOLD:
                self.logger.info(f"Avoiding {url} as it is similar to {existing_url}")
                return

        if urlhash not in self.save:
            self.save[urlhash] = (url, False, fingerprint)
            self.save.sync()
            self.to_be_downloaded.append(url)


    def _calculate_similarity(self, fingerprint1, fingerprint2):
        hamming_distance = bin(fingerprint1 ^ fingerprint2).count('1')
        similarity = 1 - (hamming_distance / 64)  
        return similarity

    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.save.sync()
