import requests
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import os
import json
import csv
import creds

@dataclass
class Item:
    opt1: str
    opt2: str
    opt3: str

@dataclass
class Scraper:

    def fetch(self, url):

        # Create a dictionary with the proxy configuration including authentication
        proxies = {
            'http': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        }

        with requests.Session() as s:
            r = s.get(url, headers=headers, proxies=proxies)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)
        return r

    def parse(self, r):
        locator = ''
        opt1_loc = ''
        opt2_loc = ''
        opt3_loc = ''
        tree = HTMLParser(r.text)
        staging = tree.css(locator)
        items = []
        for sub in staging:
            try:
                opt1 = sub.css_first(opt1_loc)
                opt2 = sub.css_first(opt2_loc)
                opt3 = sub.css_first(opt3_loc)
                items.append(asdict(Item(opt1 = opt1, opt2=opt2, opt3=opt3)))
            except:
                continue
        return items

    def get_detail_url(self,r):
        locator = 'div#SearchResultAssets > div.search-lab.AssetTile-md.tile-large'
        detail_url_loc = 'div.AssetInner > div'
        tree = HTMLParser(r.text)
        staging = tree.css(locator)
        detail_urls = []
        for sub in staging:
            try:
                detail_url = sub.css_first(detail_url_loc).attributes['data-link']
                detail_urls.append(detail_url)
            except Exception as e:
                print(e)
                continue
        return detail_urls

    def download_img(self, img_urls, folder_name):
        for url in img_urls:
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            if url != None:
                with requests.Session() as s:
                    r = s.get(url)
                with open(f"{folder_name}/{url.split('/')[-1]}", 'wb') as f:
                    f.write(r.content)
            print('Image downloaded successfully!')

    def to_csv(self, datas, filename, headers):
        try:
            for data in datas:
                try:
                    file_exists = os.path.isfile(filename)
                    with open(filename, 'a', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)
                        if not file_exists:
                            writer.writeheader()
                        if data != None:
                            writer.writerow(data)
                        else:
                            continue
                except Exception as e:
                    print(e)
                    continue
        except:
            pass

    def detail_to_csv(self, datas, filename):
        try:
            for data in datas:
                try:
                    file_exists = os.path.isfile(filename)
                    with open(filename, 'a', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f, delimiter=',')
                        if not file_exists:
                            writer.writerow(['detail_url'])
                        if data != None:
                            writer.writerow([data])
                        else:
                            continue
                except Exception as e:
                    print(e)
                    continue
        except:
            pass

    def main(self):
        search_term = input('What do you want to search? ')
        page_num = 1
        detail_urls = []
        while 1:
            print(f'Scraping page {page_num} ...')
            if page_num == 1:
                url = f'https://www.turbosquid.com/3d-model/{search_term}?page_size=500&sort_column=a7&sort_order=desc'
            else:
                url = f'https://www.turbosquid.com/3d-model/{search_term}?page_num={page_num}&page_size=500&sort_column=a7&sort_order=desc'
            try:
                r = self.fetch(url)
                detail_urls.extend(self.get_detail_url(r))
                page_num += 1
            except Exception as e:
                print(e)
                break
        self.detail_to_csv(set(detail_urls), 'detail_result2.csv')
        print('Scrape detail url completed')


if __name__ == '__main__':
    s=Scraper()
    s.main()