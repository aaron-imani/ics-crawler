import re
import statistics

file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Extracted_html_links.txt'

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

    pattern = re.compile(r'File: (.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)[\S\s]*?Number of Characters: (\d+)[\S\s]*?Number of Paragraphs: (\d+)[\S\s]*?Information Ratio: ([\d.]+)\nFile Size: (\d+)')
    matches = pattern.findall(content)

    for link, tokens, characters, paragraphs, info_ratio, file_size in matches:
        value = None
        if criterion == 'Tokens':
            value = int(tokens)
        elif criterion == 'Characters':
            value = int(characters)
        elif criterion == 'Paragraphs':
            value = int(paragraphs)
        elif criterion == 'Ratio':
            value = float(info_ratio)
        elif criterion == 'File_size':
            value = int(file_size)
            file_sizes.append(value)

        if min_value <= value <= max_value:
            links_in_range.append(link)
            extracted_info.append(f"\nFile: {link}.html\n==============================\nNumber of Tokens: {tokens}\nNumber of Characters: {characters}\nNumber of Paragraphs: {paragraphs}\nInformation Ratio: {info_ratio}\nFile Size: {file_size}\n")

    # Write the extracted information to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(extracted_info)

    # Calculate min, max, and median file size
    min_file_size = min(file_sizes)
    max_file_size = max(file_sizes)
    median_file_size = statistics.median(file_sizes)

    print(f"Min File Size: {min_file_size} bytes")
    print(f"Max File Size: {max_file_size} bytes")
    print(f"Median File Size: {median_file_size} bytes")

    return links_in_range

# Example usage for file size
min_file_size = 0
max_file_size = 1000
output_file_size_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Range_extracted_links.txt'
links_in_range_file_size = get_links_in_range_by_fileSize(file_path, min_file_size, max_file_size, output_file_size_path)
