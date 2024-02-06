
import statistics
import re
from collections import defaultdict

file_path = "C:/Users/diyac/ics-crawler/Report_stuff/Extracted_html_links_final.txt"
output_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Unique_links.txt'

def extract_unique_links(file_path, output_file_path):
    unique_links = set() 
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    pattern = re.compile(r'File: (.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)[\S\s]*?Number of Characters: (\d+)[\S\s]*?Number of Paragraphs: (\d+)[\S\s]*?Information Ratio: ([\d.]+)\nFile Size: (\d+)')
    matches = pattern.findall(content)
    for link, _, _, _, _, _ in matches:
        domain = link.split('/')[0]
        unique_links.add(domain)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for link in unique_links:
            output_file.write(link + '\n')
    return unique_links

def count_subdomains(file_path): #DIYA CHECK 
    subdomain_counts = defaultdict(int)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    pattern = re.compile(r'File: (.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)[\S\s]*?Number of Characters: (\d+)[\S\s]*?Number of Paragraphs: (\d+)[\S\s]*?Information Ratio: ([\d.]+)\nFile Size: (\d+)')
    matches = pattern.findall(content)
    for link, _, _, _, _, _ in matches:
        domain = link.split('/')[0]
        if domain.endswith('.ics.uci.edu'):
            subdomain = '.'.join(domain.split('.')[-3:])
            subdomain_counts[subdomain] += 1
    return subdomain_counts

def get_links_in_range_by_tokens(file_path, min_tokens, max_tokens, output_file_path):
    return get_links_in_range(file_path, min_tokens, max_tokens, output_file_path, 'Tokens')

def get_links_in_range_by_characters(file_path, min_characters, max_characters, output_file_path):
    return get_links_in_range(file_path, min_characters, max_characters, output_file_path, 'Characters')

def get_links_in_range_by_paragraphs(file_path, min_paragraphs, max_paragraphs, output_file_path):
    return get_links_in_range(file_path, min_paragraphs, max_paragraphs, output_file_path, 'Paragraphs')

def get_links_in_range_by_ratio(file_path, min_ratio, max_ratio, output_file_path):
    return get_links_in_range(file_path, min_ratio, max_ratio, output_file_path, 'Ratio')

def get_links_in_range_by_fileSize(file_path, min_file_size, max_file_size, output_file_path):
    return get_links_in_range(file_path, min_file_size, max_file_size, output_file_path, 'File_size')

def get_links_in_range(file_path, min_value, max_value, output_file_path, criterion):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    links_in_range = []
    extracted_info = []
    file_sizes = []  # To store file sizes for later calculation
    tokens_values = []
    characters_values = []
    paragraphs_values = []
    ratio_values = []

    pattern = re.compile(r'File: (.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)[\S\s]*?Number of Characters: (\d+)[\S\s]*?Number of Paragraphs: (\d+)[\S\s]*?Information Ratio: ([\d.]+)\nFile Size: (\d+)')
    matches = pattern.findall(content)

    for link, tokens, characters, paragraphs, info_ratio, file_size in matches:
        tokens = int(tokens)
        characters = int(characters)
        paragraphs = int(paragraphs)
        info_ratio = float(info_ratio)
        file_size = int(file_size)

        if criterion == 'Tokens':
            tokens_values.append(tokens)
        elif criterion == 'Characters':
            characters_values.append(characters)
        elif criterion == 'Paragraphs':
            paragraphs_values.append(paragraphs)
        elif criterion == 'Ratio':
            ratio_values.append(info_ratio)
        elif criterion == 'File_size':
            file_sizes.append(file_size)

        if min_value <= tokens <= max_value:
            links_in_range.append(link)
            extracted_info.append(f"\nFile: {link}.html\n==============================\nNumber of Tokens: {tokens}\nNumber of Characters: {characters}\nNumber of Paragraphs: {paragraphs}\nInformation Ratio: {info_ratio}\nFile Size: {file_size}\n")

    # Write the extracted information to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(extracted_info)

    # Calculate min, max, and median values
    if criterion == 'File_size':
        min_value = min(file_sizes)
        max_value = max(file_sizes)
        median_value = statistics.median(file_sizes)
    elif criterion == 'Tokens':
        min_value = min(tokens_values)
        max_value = max(tokens_values)
        median_value = statistics.median(tokens_values)
    elif criterion == 'Characters':
        min_value = min(characters_values)
        max_value = max(characters_values)
        median_value = statistics.median(characters_values)
    elif criterion == 'Paragraphs':
        min_value = min(paragraphs_values)
        max_value = max(paragraphs_values)
        median_value = statistics.median(paragraphs_values)
    elif criterion == 'Ratio':
        min_value = min(ratio_values)
        max_value = max(ratio_values)
        median_value = statistics.median(ratio_values)

    print(f"Min {criterion}: {min_value}")
    print(f"Max {criterion}: {max_value}")
    print(f"Median {criterion}: {median_value}")

    return links_in_range


unique_links = extract_unique_links(file_path, output_file_path)
print("Number of unique links:", len(unique_links))
print("Unique links stored in:", output_file_path)

subdomain_counts = count_subdomains(file_path)
print("List of subdomains ordered alphabetically and their number of unique pages:")
for subdomain, count in sorted(subdomain_counts.items()):
    print(f"{subdomain}: {count}")

# Example usage for file size
min_file_size = 37997
max_file_size = 37998
output_file_size_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Range_extracted_links.txt'
links_in_range_file_size = get_links_in_range_by_tokens(file_path, min_file_size, max_file_size, output_file_size_path)
print("Range of links stored in:", output_file_size_path)

