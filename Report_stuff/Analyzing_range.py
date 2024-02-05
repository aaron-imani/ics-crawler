import re
file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Extracted_html_links.txt'

def get_links_in_range_by_tokens(file_path, min_tokens, max_tokens, output_file_path):
    return get_links_in_range(file_path, min_tokens, max_tokens, output_file_path, 'Tokens')

def get_links_in_range_by_characters(file_path, min_characters, max_characters, output_file_path):
    return get_links_in_range(file_path, min_characters, max_characters, output_file_path, 'Characters')

def get_links_in_range_by_paragraphs(file_path, min_paragraphs, max_paragraphs, output_file_path):
    return get_links_in_range(file_path, min_paragraphs, max_paragraphs, output_file_path, 'Paragraphs')

def get_links_in_range_by_ratio(file_path, min_ratio, max_ratio, output_file_path):
    return get_links_in_range(file_path, min_ratio, max_ratio, output_file_path, 'Ratio')

def get_links_in_range(file_path, min_value, max_value, output_file_path, criterion):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    links_in_range = []
    extracted_info = []
    
    pattern = re.compile(r'File: (.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)[\S\s]*?Number of Characters: (\d+)[\S\s]*?Number of Paragraphs: (\d+)[\S\s]*?Information Ratio: ([\d.]+)')
    matches = pattern.findall(content)

    for link, tokens, characters, paragraphs, info_ratio in matches:
        value = None
        if criterion == 'Tokens':
            value = int(tokens)
        elif criterion == 'Characters':
            value = int(characters)
        elif criterion == 'Paragraphs':
            value = int(paragraphs)
        elif criterion == 'Ratio':
            value = float(info_ratio)

        if min_value <= value <= max_value:
            links_in_range.append(link)
            extracted_info.append(f"\nFile: {link}.html\n==============================\nNumber of Tokens: {tokens}\nNumber of Characters: {characters}\nNumber of Paragraphs: {paragraphs}\nInformation Ratio: {info_ratio}\n")
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(extracted_info)

    return links_in_range

'''
#-------------------------------------------------
# Example usage for tokens
min_tokens = 341
max_tokens = 350
output_tokens_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Range_extracted_links.txt'
links_in_range_tokens = get_links_in_range_by_tokens(file_path, min_tokens, max_tokens, output_tokens_file_path)
'''
#-------------------------------------------------
min_characters = 1000
max_characters = 2000
output_characters_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Range_extracted_links.txt'
links_in_range_characters = get_links_in_range_by_characters(file_path, min_characters, max_characters, output_characters_file_path)
'''
#-------------------------------------------------
min_paragraphs = 5
max_paragraphs = 10
output_paragraphs_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Range_extracted_links.txt'
links_in_range_paragraphs = get_links_in_range_by_paragraphs(file_path, min_paragraphs, max_paragraphs, output_paragraphs_file_path)
#-------------------------------------------------
min_ratio = 1.2
max_ratio = 1.5
output_ratio_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Range_extracted_links.txt'
links_in_range_ratio = get_links_in_range_by_ratio(file_path, min_ratio, max_ratio, output_ratio_file_path)
'''