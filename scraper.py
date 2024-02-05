import re
from urllib.parse import urlparse
from urllib.parse import urljoin, urldefrag
from lxml import html
import os
from configparser import ConfigParser
from urllib.parse import urlparse, urlunparse
from utils import normalize

config_parser = ConfigParser()
config_parser.read('config.ini')
MIN_TOKEN_COUNT = config_parser.getint('SCRAPER', 'MIN_TOKEN_COUNT', fallback=100)
MIN_TEXT_CONTENT_LENGTH = config_parser.getint('SCRAPER', 'MIN_TEXT_CONTENT_LENGTH', fallback=1000)
MAX_DEPTH = config_parser.getint('SCRAPER', 'MAX_DEPTH', fallback=10)
MAX_FILE_SIZE_BYTES = 36220  # DESCRIBE IN THE README HOW WE GOT THIS DIYA
last_vistied = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def _store_webpage(url, content):
    splitted = url.split("://")[1].split("/")
    save_dir = os.path.join('visited',*splitted[:-1])

    os.makedirs(save_dir, exist_ok=True)
    
    file_name = splitted[-1]
    file_name.replace('htm', 'html')

    if 'html' not in file_name:
        file_name += '.html'

    file_path = os.path.join(save_dir, file_name)
    with open(file_path, 'w') as f:
        f.write(content)


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    global last_vistied #DIYA CHECK 
    unq_links = set()
    
    content_size = len(resp.raw_response.content)
    if content_size > MAX_FILE_SIZE_BYTES:
        print(f"File size exceeds the maximum threshold for {url}. Skipping extraction.")
        return []

    # Checking dead URL
    if resp.status != 200:
        print(f"Failed to fetch {url}. Status code: {resp.status}")
        return []
    try:
        tree = html.fromstring(resp.raw_response.content)
        # Extracting link
        for link in tree.xpath('//a'):
            if 'nofollow' in link.get('rel', ''):
                continue
            link = link.get('href')
            # To handle traps
            full_url = urljoin(resp.url, link)
            normalized_url = normalize(full_url)
            unq_links.add(normalized_url)

        # calculating the textual ration 
        text_content = tree.text_content().strip()
        total_content = resp.raw_response.content.decode('utf-8').strip()

        should_store = True

        # Checking whitescapes
        if not text_content or not total_content:
            print(f"Empty content for {url}. Skipping extraction.")
            should_store = False
        
        text_content_ratio = len(text_content) / max(len(total_content), 1)
        text_content_threshold = 0.25
        if text_content_ratio < text_content_threshold or len(text_content) < MIN_TEXT_CONTENT_LENGTH:
            print(f"Low textual content for {url}. Skipping extraction.")
            should_store = False
        
        if should_store:
            _store_webpage(url, total_content)
        
    except Exception as e:
        print(f"Could not extract links from {url}: {e}")
    
    return list(unq_links)

    

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower(),
        ) and (
            re.match(r".*\.(ics|cs|informatics|stat)\.uci\.edu$", parsed.netloc)
            or re.match(
                r".*today\.uci\.edu/department/information_computer_sciences/.*", url
            )
        ):
            path_segments = parsed.path.split('/')
            depth = len(list(filter(None, path_segments)))
            # handling the depth and repetition of the path
            return not re.match(r'(.*?/).*?\1.*?\1', parsed.path) and depth <= MAX_DEPTH

    except TypeError:
        print("TypeError for ", parsed)
        raise
