import os
from bs4 import BeautifulSoup
from collections import defaultdict

def get_file_details(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')

        num_tokens = len(content.split())
        text_content = soup.get_text()
        num_chars = len(text_content)
        num_paragraphs = len(soup.find_all('p'))

        total_content = len(soup.get_text(strip=True))
        information_ratio = num_chars / total_content if total_content > 0 else 0

        # Get file size in bytes
        file_size = os.path.getsize(file_path)

        return {
            'num_tokens': num_tokens,
            'num_chars': num_chars,
            'num_paragraphs': num_paragraphs,
            'information_ratio': information_ratio,
            'text_content': text_content,
            'file_size': file_size
        }

def print_file_details(file_path, file_details, output_directory):
    relative_path = os.path.relpath(file_path, directory_path)
    output_subdirectory = os.path.join(output_directory, os.path.dirname(relative_path))
    os.makedirs(output_subdirectory, exist_ok=True)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file_path = os.path.join(output_subdirectory, f"{file_name}.txt")

    with open(output_file_path, 'w', encoding='utf-8') as output:
        output.write(f"File: {file_path}\n")
        output.write("=" * 30 + "\n")
        output.write(f"Number of Tokens: {file_details['num_tokens']}\n")
        output.write(f"Number of Characters: {file_details['num_chars']}\n")
        output.write(f"Number of Paragraphs: {file_details['num_paragraphs']}\n")
        output.write(f"Information Ratio: {file_details['information_ratio']:.4f}\n")
        output.write(f"File Size: {file_details['file_size']}\n")
        output.write("\n")
        output.write(file_details['text_content'])
        output.write("\n\n")

# Rest of your code remains unchanged


def generate_summary(directory, output_directory):
    summary = defaultdict(int)
    full_log_path = os.path.join(output_directory, "FULL_LOG.txt")

    with open(full_log_path, 'w', encoding='utf-8') as full_log:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".html"):
                    file_path = os.path.join(root, file)
                    file_details = get_file_details(file_path)

                    print_file_details(file_path, file_details, output_directory)

                    for key, value in file_details.items():
                        if key != 'text_content':
                            summary[key] += value

                    full_log.write("=" * 30 + "\n")
                    full_log.write(f"File: {file_path}\n")
                    full_log.write("=" * 30 + "\n")
                    full_log.write(file_details['text_content'])
                    full_log.write("\n\n")

    print("Summary:")
    print("=" * 30)
    for key, value in summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    directory_path = "/Users/abhinandganesh/Desktop/ics-crawler/visited" 
    output_directory_path = "/Users/abhinandganesh/Desktop/ics-crawler/summary" 
    os.makedirs(output_directory_path, exist_ok=True)
    
    generate_summary(directory_path, output_directory_path)
