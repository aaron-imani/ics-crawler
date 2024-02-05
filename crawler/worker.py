from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
from urllib.parse import urlparse
from utils import get_contenthash
from time import sleep
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.seen_hashes = set()

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
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
            if content_hash in self.seen_hashes:
                self.logger.info(f"Content of {tbd_url} is already seen.")
                self.frontier.mark_url_complete(tbd_url)
                continue

            self.seen_hashes.add(content_hash)
            # text_content = resp.text if resp and resp.text else ""

            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
                
            # Update last visit time for the domain
            self.frontier.last_visited[domain] = time.time()
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
