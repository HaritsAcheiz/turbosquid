import httpx
from selectolax.parser import HTMLParser
import asyncio
from dataclasses import dataclass, asdict
import re
import csv
import os
import creds

@dataclass
class Item:
    model_name: str
    product_id: str
    # publish_date: str
    page_link: str
    # download_link: str
    price: str
    model_license: str
    format: str
    polygons: str
    vertices: str
    textures: str
    materials: str
    unwrapped_uvs: str
    uv_mapped: str
    checklist: bool

@dataclass
class Scraper:
    base_url: str = 'https://www.turbosquid.com'
    download_directory: str = os.path.join(os.getcwd(), 'temp')
    latitude: float = -6.2088
    longitude: float = 106.8456

    def get_page(self, keyword):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }
        url = f'https://www.turbosquid.com/Search/3D-Models/free/{keyword}?page_size=500'
        with httpx.Client() as client:
            response = client.get(url)
        tree = HTMLParser(response.text)
        return tree.css_first('span#ts-total-pages').text()

    def get_top_category(self):
        url = 'https://www.turbosquid.com/Search/3D-Models'
        with httpx.Client() as client:
            response = client.get(url)
        tree = HTMLParser(response.text)
        categories = []
        dict_cat = {'opt': None, 'url': None}
        children = tree.css('a.related-search-item')
        for child in children:
            temp = child.attributes['href'].strip().rsplit('/', maxsplit=1)
            dict_cat['opt'] = temp[-1]
            if child.parent.attributes['class'] == 'col-md-2 col-sm-4':
                dict_cat['url'] = temp[0]+'/free/'+dict_cat['opt']+'page_size=500'
            else:
                dict_cat['url'] = temp[0]+'/Search/3D-Models/free/'+dict_cat['opt']+'?page_size=500'
            categories.append(dict_cat.copy())
        return categories

    def get_page_cat(self, url):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }
        url = f'{url}?page_size=500'
        with httpx.Client() as client:
            response = client.get(url)
        tree = HTMLParser(response.text)
        return tree.css_first('span#ts-total-pages').text()

    async def fetch_id(self, client, url):
        retries = 3
        retry_delay = 0.3
        for _ in range(retries):
            try:
                response = await client.get(url, timeout=10)
                return response.text
            except:
                await asyncio.sleep(retry_delay)
        return ''

    async def fetch_all_id(self, keyword, last_page):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }

        urls = [f'https://www.turbosquid.com/3d-model/free/{keyword}?page_num={page_num}&page_size=500' for page_num in range(1, int(last_page)+1)]

        async with httpx.AsyncClient(proxies=proxies) as client:
            tasks = [asyncio.create_task(self.fetch_id(client,url)) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses

    async def fetch_all_id_cat(self, url, last_page):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }

        urls = [f'{url}?page_num={page_num}&page_size=500' for page_num in range(1, int(last_page)+1)]

        async with httpx.AsyncClient(proxies=proxies) as client:
            tasks = [asyncio.create_task(self.fetch_id(client,url)) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses

    def parse_id(self, responses):
        staging_loc = 'div#SearchResultAssets > div.search-lab.AssetTile-md.tile-large'
        detail_url_loc = 'div.AssetInner > div'
        item_ids = []
        for response in responses:
            tree = HTMLParser(response)
            staging = tree.css(staging_loc)
            item_ids.extend([article.css_first(detail_url_loc).attributes['data-id'] for article in staging])
        return item_ids

    async def fetch_detail(self, client, url):
        retries = 3
        retry_delay = 0.3
        for _ in range(retries):
            try:
                response = await client.get(url, timeout=10)
                return response.json()
            except:
                await asyncio.sleep(retry_delay)
        return ''
        # response = await client.get(url, timeout=20)
        # return response.json()

    async def fetch_all_detail(self, ids):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        }

        urls = [f'https://www.turbosquid.com/API/v1/Search/Preview/{id}' for id in ids if id.isnumeric()]
        async with httpx.AsyncClient(headers=headers, proxies=proxies) as client:
            tasks = [asyncio.create_task(self.fetch_detail(client, url)) for url in urls]
            datas = await asyncio.gather(*tasks, return_exceptions=True)
            return datas

    def parse_detail(self, responses):
        datas = []
        for response in responses:
            json_data = response
            # json_formatted_str = json.dumps(json_data, indent=2)
            # print(json_formatted_str)
            try:
                model_name = json_data['STCPRODUCT']['PRODUCT_NAME']
            except TypeError:
                continue
            product_id = HTMLParser(json_data['STCPRODUCT']['ACTION_HTML']).css_first('a').attributes['data-id']
            publish_date = ''
            page_link = json_data['STCPRODUCT']['PRODUCT_LINK']
            download_link = ''
            price = HTMLParser(json_data['STCPRODUCT']['PRICE_HTML']).text()
            try:
                model_license = HTMLParser(json_data['STCPRODUCT']['LICENSE_HTML']).css_first('span').text()
            except:
                model_license = None
            format = ", ".join([re.sub(r'\n                     ', ' | ', x.text().strip()) for x in
                                HTMLParser(json_data['STCPRODUCT']['PRODUCT_FILES_HTML']).css('li')])
            polygons = HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                'li#preview_details_specification_polygons').text()
            vertices = HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                'li#preview_details_specification_vertices').text()
            if HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                    'li#preview_details_specification_textures'):
                textures = 'Yes'
            else:
                textures = 'No'
            if HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                    'li#preview_details_specification_materials'):
                materials = 'Yes'
            else:
                materials = 'No'
            if HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                    'li#preview_details_specification_unwrapped_uvs'):
                unwrapped_uvs = 'Yes'
            else:
                unwrapped_uvs = 'No'
            if HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                    'li#preview_details_specification_uv_mapped'):
                uv_mapped = 'Yes'
            else:
                uv_mapped = 'No'

            data = asdict(Item(model_name=model_name,
                                product_id=product_id,
                                # publish_date=publish_date,
                                page_link=page_link,
                                # download_link=download_link,
                                price=price,
                                model_license=model_license,
                                format=format,
                                polygons=polygons,
                                vertices=vertices,
                                textures=textures,
                                materials=materials,
                                unwrapped_uvs=unwrapped_uvs,
                                uv_mapped=uv_mapped,
                                checklist=False))
            datas.append(data)
        return datas


    def to_csv(self, datas, filename):
        headers = ['model_name', 'product_id', 'page_link', 'price', 'model_license',
                   'format', 'polygons', 'vertices', 'textures', 'materials', 'unwrapped_uvs', 'uv_mapped', 'checklist']
        try:
            for data in datas:
                try:
                    # file_exists = os.path.isfile(filename)
                    folder_path = os.path.join(os.getcwd(), 'ids')
                    os.makedirs(folder_path, exist_ok=True)
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'a', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)
                        if os.path.getsize(file_path) == 0:
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

    async def main(self):
        print('*****************Turbosquid Scraper*******************')
        print('Scraper Method:')
        print('(1) By Keyword')
        print('(2) By Top Category')
        while 1:
            try:
                method = int(input('Please type search method number: '))
                if method >= 1 and method <= 2:
                    break
                else:
                    print("Input out of range")
                    continue
            except:
                print("Invalid input try again")
                continue

        if method == 1:
            keyword = input('What do you want to search? ').replace(' ','-')
            print('Getting Product IDs...')
            last_page = self.get_page(keyword)
            page_responses = []
            page_responses.extend(await self.fetch_all_id(keyword, last_page))
            ids = s.parse_id(page_responses)
            print('Getting Details...')
            responses = []
            responses.extend(await self.fetch_all_detail(ids))
            datas = s.parse_detail(responses)
            datas = [data for data in datas if data['price'] == 'Free']
            print(f'Saving data to {keyword.replace("-","_")}_result.csv')
            s.to_csv(datas, f'{keyword.replace("-","_")}_result.csv')
            print('Scraping data is done!')
            return responses

        elif method == 2:
            categories = self.get_top_category()
            for i, category in enumerate(categories):
                print(f'({i}) {category["opt"]}')
            while 1:
                try:
                    choosen_cat = int(input('Please type category number: '))
                    if choosen_cat >= 0 and choosen_cat <= len(categories):
                        break
                    else:
                        print("Input out of range")
                        continue
                except:
                    print("Invalid input try again")
                    continue

            category = categories[choosen_cat]
            print('Getting Product IDs...')
            last_page = self.get_page_cat(category['url'])
            page_responses = []
            page_responses.extend(await self.fetch_all_id_cat(category['url'], last_page))
            ids = s.parse_id(page_responses)
            print('Getting Details...')
            responses = []
            responses.extend(await self.fetch_all_detail(ids))
            datas = s.parse_detail(responses)
            datas = [data for data in datas if data['price'] == 'Free']
            print(f'Saving data to {category["key"]}_result.csv')
            s.to_csv(datas, f'{category["key"]}_result.csv')
            print('Scraping data is done!')
            return responses

if __name__ == '__main__':
    s=Scraper()
    responses = asyncio.run(s.main())
    errors = 0
    successes = 0
    for response in responses:
        if 'Error' in response:
            errors += 1
        else:
            successes += 1
    print(f"Status (Successes:{successes}, Errors:{errors})")