#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib3
import string

def extract_name(href):
    return href[href.index('/name-meaning/') + len('/name-meaning/'):]

def is_name_url(href):
    return 'http://baby-names.familyeducation.com/name-meaning/' in href

def scrape_page(url):
    names = set()
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    if r.status == 200:
         soup = BeautifulSoup(r.data, 'html.parser')
         for link in soup.find_all('a'):
             href = link.get('href')
             if is_name_url(href):
                names.add(extract_name(href))
    else:
        print('couldn\'t reach server')
    return names

def main():
    names = set()
    for letter in string.ascii_lowercase:
        for page_number in range(1, 256):
            url = 'http://baby-names.familyeducation.com/browse/letter/' + letter + '?page=' + str(page_number)
            print(url)
            page_names = scrape_page(url)
            if not page_names:
                break
            names |= page_names
    print(names)
    name_list = list(names)
    name_list.sort()
    with open('first_names.txt', 'w') as file:
        file.write('\n'.join(name_list))

if __name__ == '__main__':
    main()
