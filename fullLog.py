import os

def concatenate_first_six_lines(directory_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as output:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as input_file:
                        lines = input_file.readlines()[:6]
                        output.write(f"File: {file_path}\n")
                        output.write("=" * 30 + "\n")
                        output.writelines(lines)
                        output.write("\n\n")

if __name__ == "__main__":
    summary_directory = "/Users/abhinandganesh/Desktop/ics-crawler/summary"
    full_log_file = "/Users/abhinandganesh/Desktop/ics-crawler/full_log.txt"

    concatenate_first_six_lines(summary_directory, full_log_file)
