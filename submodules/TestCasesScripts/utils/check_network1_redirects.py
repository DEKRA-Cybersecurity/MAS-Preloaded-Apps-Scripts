import sys
import requests
import subprocess
import re
import datetime

def get_location(result):
    location_line = re.search(r'Location: (.+)', result)

    return location_line.group(1) if location_line else ""

def check_redirects(urls):
    urls_found = set()

    for url in urls:
        if url.startswith('http://') and not url.startswith('https://') and url:
            try:
                response = requests.get(url, timeout=5)
                
                status_code = response.status_code
                
                if status_code < 400:
                    result = subprocess.check_output(['curl', '-v', '--silent', url], stderr=subprocess.STDOUT, timeout=60)

                    location_url = get_location(result.decode('utf-8'))

                    if not 'https' in location_url:
                        urls_found.add(url)

            except (requests.exceptions.TooManyRedirects):
                print('request.exceptions.TooManyRedirects:', url)
                pass
            except Exception as e:
                pass

    return len(urls_found)

def get_set_urls(urls_path):

    urls_set = set()

    with open(urls_path, "r") as file:
        for line in file:
            url = line.strip() 
            urls_set.add(url)

    return urls_set


def check(urls_path, apk_hash, package_name, uuid_execution):
    # Get unique set of urls in file
    urls_set = get_set_urls(urls_path)

    urls = check_redirects(urls_set)

    return urls
