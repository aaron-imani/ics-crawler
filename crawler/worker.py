from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
from time import sleep


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
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
            
            # Politeness delay 
            last_visited_time = self.frontier.last_visited.get(domain, 0)
            elapsed_time = time.time() - last_visited_time
            if elapsed_time < self.config.politeness_delay:
                self.logger.info(f"Politeness delay for {tbd_url}. Sleeping for {self.config.politeness_delay - elapsed_time} seconds.")
                sleep(self.config.politeness_delay - elapsed_time)
            
            
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
                
            # Update last visit time for the domain
            self.frontier.last_visited[domain] = time.time()
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
