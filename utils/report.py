import os
import shelve
from utils import get_logger
from urllib.parse import urlparse
import re
from glob import glob
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from utils.tokenization import tokenize, computeWordFrequencies, print_sorted
from utils.storage_check import does_shelve_exist

class Report(object):
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("REPORT")
    
        if not does_shelve_exist(self.config.save_file):
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                "unable to generate a report.")
            self.save = None
            return

        text_files = glob("visited/**/*.txt",recursive=True)
        if not text_files:
            self.logger.info(
                "No text files found in visited directory. "
                "Converting html to text.")
            self._convert_visited_pages_to_text()
        
        self._load_text_files()

        self.save = shelve.open(self.config.save_file)
    
    def get_unique_urls_count(self):
        unique_urls = 0
        for _, completed in self.save.values():
            if completed:
                unique_urls += 1
        return unique_urls
    
    def get_most_common_words(self):
        all_tokens = [] 
        longest_tokens = []
        longest_page = ''

        for file, text in self.text_files.items():
            tokens = tokenize(text)
            all_tokens.extend(tokens)

            if len(tokens) > len(longest_tokens):
                longest_tokens = tokens
                longest_page = 'https://' + file.replace('visited/', '').replace('\\', '/').replace('.txt', '.html')

        
        word_frequencies = computeWordFrequencies(all_tokens)
        top_50_words = print_sorted(word_frequencies, 50)
        with open("report/top_50_words.txt", "w") as f:
            f.write(top_50_words)
        
        self.logger.info("Top 50 common words written to report/top_50_words.txt")
        self.logger.info(f"Longest page: {longest_page}")
    
    def _to_text(self, html):
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\\n+', '\\n', text)
        return text
    
    def _convert_visited_pages_to_text(self):
        html_files = glob("visited/**/*.html",recursive=True)
        for file in tqdm(html_files,desc="Converting html to text"):
            with open(file, "r") as f:
                html = f.read()
            text = self._to_text(html)
            with open(file.replace(".html", ".txt"), "w") as f:
                f.write(text)

    def _load_text_files(self):
        self.text_files = {}
        text_files = glob("visited/**/*.txt",recursive=True)
        for file in text_files:
            with open(file, "r", encoding='utf-8') as f:
                lines = []
                for line in f:
                    lines.append(line)
                self.text_files[file] = '\n'.join(lines)

    def get_ics_subdomains(self):
        subdomains = {}
        ics_patttern = re.compile(r"^(.+)\.ics\.uci\.edu$")

        for url, completed in self.save.values():
            url = url.replace('www.', '')
            parsed_url = urlparse(url)
            match = re.match(ics_patttern, parsed_url.netloc)
            if match and completed:
                subdomain = parsed_url.scheme + "://" + match.group(1).strip() + '.ics.uci.edu'
                if subdomain not in subdomains:
                    subdomains[subdomain] = 1
                else:
                    subdomains[subdomain] += 1

        # sort subdomains by key
        with open("report/subdomains.txt", "w") as f:
            for k, v in sorted(subdomains.items(), key=lambda item: item[0].split('//')[1].lower()):
                f.write(f"{k}, {v}\n")
        self.logger.info(f"Found {len(subdomains)} subdomains under ics. Subdomains written to report/subdomains.txt")

    def generate_report(self):
        if not self.save:
            self.logger.info("No data retrieved from save file. Unable to generate report.")
            return


        # How many unique pages did you find?
        unique_urls = self.get_unique_urls_count()
        self.logger.info(f"Unique urls found: {unique_urls}")

        os.makedirs("report", exist_ok=True)
        # the list of subdomains found in the ics.uci.edu domain ordered alphabetically  
        self.get_ics_subdomains()

        # the longest page in terms of number of words
        # top 50 most common words
        self.get_most_common_words()

    def __del__(self):
        if self.save:
            self.save.close()