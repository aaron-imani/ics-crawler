import re

def extract_info(original_file_path, output_file_path):
    with open(original_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Use regular expression to find matches for all links with the specified format
    pattern = re.compile(r'File: /Users/abhinandganesh/Desktop/ics-crawler/visited/(.+)\.html\n=*[\S\s]*?Number of Tokens: (\d+)\nNumber of Characters: (\d+)\nNumber of Paragraphs: (\d+)\nInformation Ratio: ([\d.]+)')
    matches = pattern.findall(content)

    if not matches:
        print("No matches found. Please check the regular expression.")

    extracted_info = []
    for match in matches:
        link, tokens, characters, paragraphs, info_ratio = match
        extracted_info.append(f"\nFile: {link}.html\n==============================\nNumber of Tokens: {tokens}\nNumber of Characters: {characters}\nNumber of Paragraphs: {paragraphs}\nInformation Ratio: {info_ratio}\n")

    if not extracted_info:
        print("No information extracted. Please check the content and regular expression.")

    # Write the extracted information to the new file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(extracted_info)

# Example usage
original_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/D_full_log.txt'
output_file_path = 'C:/Users/diyac/ics-crawler/Report_stuff/Extracted_html_links.txt'
extract_info(original_file_path, output_file_path)
