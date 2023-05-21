import time
import requests
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import os
import csv
import creds
import re
import asyncio
import aiohttp

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

    async def fetch_detail(self, s, url):
        proxies = f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        }

        async with s.post(url, headers=headers, proxy=proxies, timeout=7) as r:
            if r.status != 200:
                r.raise_for_status()

            return await r.json()

    async def fetch_all(self, s, ids):
        tasks = list()
        urls = [f'https://www.turbosquid.com/API/v1/Search/Preview/{id}' for id in ids]
        for url in urls:
            task = asyncio.create_task(self.fetch_detail(s, url))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
        return res

    async def run(self, ids):
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=7, sock_read=10)
        async with aiohttp.ClientSession(timeout=session_timeout) as s:
            json_datas = await self.fetch_all(s, ids)
        return json_datas

    def get_detail(self, r):
        tree = HTMLParser(r.text)
        model_name = tree.css_first('div#product-title > h1').text().strip()
        product_id = re.findall('\d+',tree.css_first('span#ProductID').text())[0]
        publish_date = tree.css_first('span#FPDatePublished').text().strip()
        page_link = r.url
        try:
            download_link = ''
        except:
            download_link = 'Not Available'
        price = tree.css_first('span.text-xl:nth-of-type(3)').text().strip()
        if price == '':
            price = tree.css_first('span#product-price').text().strip()
        else:
            pass
        model_license = tree.css_first(r'div.flex.flex-row.px-4 > span > span:nth-of-type(1) > span').text().strip()

        stage1 = tree.css('div#formats-container > div')
        sentences = []
        format = ''
        for x in stage1[1:]:
            stage2 = x.css('span')
            for y in stage2:
                char = re.sub('\n','',y.text().strip())
                word = ''.join(char)
                sentences.append(word)
        format = ", ".join(sentences)

        polygons = re.sub('\s+',' ',tree.css_first('span#FPSpec_polygons').text().strip())
        vertices = re.sub('\s+',' ',tree.css_first('span#FPSpec_vertices').text().strip())
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
        items = asdict(Item(model_name=model_name,
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
                                 uv=uv))
        return items

    def get_detail_url(self,r):
        locator = 'div#SearchResultAssets > div.search-lab.AssetTile-md.tile-large'
        detail_url_loc = 'div.AssetInner > div'
        tree = HTMLParser(r.text)
        staging = tree.css(locator)
        detail_urls = []
        for sub in staging:
            detail_url = sub.css_first(detail_url_loc).attributes['data-link']
            detail_urls.append(detail_url)
        return detail_urls

    def get_id(self, r):
        locator = 'div#SearchResultAssets > div.search-lab.AssetTile-md.tile-large'
        detail_url_loc = 'div.AssetInner > div'
        tree = HTMLParser(r.text)
        staging = tree.css(locator)
        ids = []
        for sub in staging:
            id = sub.css_first(detail_url_loc).attributes['data-id']
            ids.append(ids)
        return ids

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
        headers = ['model_name', 'product_id', 'publish_date', 'page_link', 'download_link', 'price', 'model_license',
                   'format', 'polygons', 'vertices', 'textures', 'materials','uv']
        while trial < 3:
            print(f'Scraping page {page_num}...')
            if page_num == 1:
                url = f'https://www.turbosquid.com/3d-model/{search_term}?page_size=500&sort_column=a7&sort_order=desc'
            else:
                url = f'https://www.turbosquid.com/3d-model/{search_term}?page_num={page_num}&page_size=500&sort_column=a7&sort_order=desc'
            try:
                r = self.fetch(url)
                detail_url = self.get_detail_url(r)
                if detail_url != []:
                    detail_urls.extend(detail_url)
                    page_num += 1
                    trial = 1
                else:
                    break
            except Exception as e:
                print(e)
                time.sleep(3)
                print('try to reconnect')
                trial += 1

        self.detail_to_csv(set(detail_urls), 'detail_result2.csv')
        print('Scrape detail url completed')
        items = []
        for i, detail_url in enumerate(set(detail_urls)):
            trial = 1
            while trial < 3:
                print(f'Get item details from {detail_url}')
                try:
                    r = self.fetch(detail_url)
                    items.append(self.get_detail(r))
                    trial = 1
                    break
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    print('try to reconnect')
                    trial += 1
            print(f'{i} detail added from {len(set(detail_urls))}')
        self.to_csv(items, 'result.csv', headers=headers)

        # responses = asyncio.run(self.run(set(detail_urls)))
        # items = [self.get_detail(response) for response in responses]
        # self.to_csv(items, 'result.csv', headers=headers)

if __name__ == '__main__':
    s=Scraper()
    s.main()