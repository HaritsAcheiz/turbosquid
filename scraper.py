import time

import requests
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import os
import json
import csv
import creds
import re

@dataclass
class Item:
    model_name: str
    product_id: str
    publish_date: str
    page_link: str
    download_link: str
    price: str
    model_license: str
    format: str
    polygons: str
    vertices: str
    textures: str
    materials: str
    uv: str

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

    def get_detail(self, r):
        tree = HTMLParser(r.text)
        items = []
        i_formats = []
        model_name = tree.css_first('div#product-title > h1').text()
        product_id = tree.css_first('span#ProductID').text()
        publish_date = tree.css_first('span#FPDatePublished').text()
        page_link = r.url
        try:
            download_link = ''
        except:
            download_link = 'Not Available'
        price = tree.css_first('span.text-xl:nth-of-type(3)').text()
        if price == '':
            price = tree.css_first('span#product-price').text()
        else:
            pass
        model_license = tree.css_first(r'div.flex.flex-row.px-4 > span > span:nth-of-type(1) > span').text()
        formats = tree.css('div#formats-container > div')
        for i_format in formats:
            i_formats.append(re.sub(r'\s+',' ',i_format.text()))
        print(i_formats)
        format = ",".join(i_formats)
        polygons = tree.css_first('span#FPSpec_polygons').text()
        vertices = tree.css_first('span#FPSpec_vertices').text()
        if tree.css_first('span#FPSpec_textures'):
            textures = 'Yes'
        else:
            textures = 'No'
        if tree.css_first('span#FPSpec_materials'):
            materials = 'Yes'
        else:
            materials = 'No'
        if tree.css_first('span#FPSpec_unwrapped_uv'):
            uv = 'Yes'
        else:
            uv = 'No'
        items.append(asdict(Item(model_name=model_name,
                                 product_id=product_id,
                                 publish_date=publish_date,
                                 page_link=page_link,
                                 download_link=download_link,
                                 price=price,
                                 model_license=model_license,
                                 format=format,
                                 polygons=polygons,
                                 vertices=vertices,
                                 textures=textures,
                                 materials=materials,
                                 uv=uv)))
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
        trial = 1
        while trial < 3:
            print(f'Scraping page {page_num}...')
            if page_num == 1:
                url = f'https://www.turbosquid.com/3d-model/{search_term}?page_size=500&sort_column=a7&sort_order=desc'
            else:
                url = f'https://www.turbosquid.com/3d-model/{search_term}?page_num={page_num}&page_size=500&sort_column=a7&sort_order=desc'
            try:
                r = self.fetch(url)
                detail_urls.extend(self.get_detail_url(r))
                page_num += 1
                trial = 1
                break #prototype
            except Exception as e:
                print(e)
                time.sleep(3)
                print('try to reconnect')
                trial += 1
        self.detail_to_csv(set(detail_urls), 'detail_result2.csv')
        print('Scrape detail url completed')
        items = []
        trial = 1
        for detail_url in detail_urls[0:2]:
            while trial < 3:
                print('Get item details...')
                try:
                    r = self.fetch(detail_url)
                    # print(r.text)
                    items.append(self.get_detail(r))
                    trial = 1
                    break
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    print('try to reconnect')
                    trial += 1
            print(f'add detail from {detail_url}')
        self.to_csv(set(items), 'result.csv')

if __name__ == '__main__':
    s=Scraper()
    s.main()