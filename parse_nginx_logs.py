import re
from typing import List

def extract_ips(log_content):
    #Extracts IP addresses from nginx log content.
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    return ip_pattern.findall(log_content)

def read_log_file(file_path):
    #Reads the content of a log file.
    with open(file_path, 'r') as file:
        return file.read()

def write_ips_to_file(ips: List[str], output_path: str):
    #Writes the IP addresses to a new file.
    with open(output_path, 'w') as file:
        for ip in ips:
            file.write(f"https://ipinfo.io/{ip}\n")

def main(log_file_path, output_file_path):
    #Main function to parse log file and write IPs to a new file.
    log_content = read_log_file(log_file_path)
    ips = extract_ips(log_content)
    write_ips_to_file(ips, output_file_path)

if __name__ == "__main__":
    # Define the paths to the log file and the output file
    log_file_path = 'nginx_access.log'
    output_file_path = 'extracted_ips.txt'
    
    # Run the main function
    main(log_file_path, output_file_path)
