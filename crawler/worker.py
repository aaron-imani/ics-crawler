from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
from urllib.parse import urlparse
from utils import get_contenthash
from time import sleep
import time
import shelve

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.save = shelve.open(self.config.seen_hashes)
        self._load_save_file()

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
    
    def _load_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        if not 'seen_hashes' in self.save:
            self.save['seen_hashes'] = set()
    
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            
            # Extract domain from the URL
            domain = urlparse(tbd_url).netloc
            
            
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            # Check if the content is already seen
            if not resp or not resp.raw_response or not resp.raw_response.content:
                self.logger.info(f"Failed to fetch {tbd_url}. Status code: {resp.status}")
                self.frontier.mark_url_complete(tbd_url)
                continue

            content_hash = get_contenthash(resp.raw_response.content)
            if content_hash in self.save['seen_hashes']:
                self.logger.info(f"Content of {tbd_url} is already seen.")
                self.frontier.mark_url_complete(tbd_url)
                continue

            self.save['seen_hashes'].add(content_hash)
            self.save.sync()

            scraped_urls, message = scraper.scraper(tbd_url, resp)
            self.logger.info(message)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
                
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
