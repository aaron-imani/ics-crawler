import re

def extract_info(original_file_path, output_file_path):
    with open(original_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Use regular expression to find matches for all links with the specified format
    pattern = re.compile(r'File: /Users/abhinandganesh/Desktop/ics-crawler/visited/(.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)[\S\s]*?Number of Characters: (\d+)[\S\s]*?Number of Paragraphs: (\d+)[\S\s]*?Information Ratio: ([\d.]+)\nFile Size: (\d+)')
    matches = pattern.findall(content)

    if not matches:
        print("No matches found. Please check the regular expression.")

    extracted_info = []
    for match in matches:
        link, tokens, characters, paragraphs, info_ratio, file_size = match
        # Remove the common prefix from the link
        link = link.replace('/Users/abhinandganesh/Desktop/ics-crawler/visited/', '')
        extracted_info.append(f"\nFile: {link}.html\n==============================\nNumber of Tokens: {tokens}\nNumber of Characters: {characters}\nNumber of Paragraphs: {paragraphs}\nInformation Ratio: {info_ratio}\nFile Size: {file_size}")

    if not extracted_info:
        print("No information extracted. Please check the content and regular expression.")

    # Write the extracted information to the new file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(extracted_info)

# Example usage
original_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/final_log.txt'
output_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Extracted_html_links_final.txt'
extract_info(original_file_path, output_file_path)
