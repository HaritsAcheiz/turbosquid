import httpx
from selectolax.parser import HTMLParser
import json
import asyncio
from dataclasses import dataclass, asdict
import re
import csv
import os
import creds
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

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
    unwarped_uvs: str
    uv_mapped: str

@dataclass
class Scraper:

    def get_page(self, keyword):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }
        url = f'https://www.turbosquid.com/3d-model/{keyword}?page_size=500&sort_column=a7&sort_order=desc'
        with httpx.Client() as client:
            response = client.get(url)
        tree = HTMLParser(response.text)
        return tree.css_first('span#ts-total-pages').text()


    async def fetch_id(self, client, url):
        response = await client.get(url, timeout=10.0)
        return response.text


    async def fetch_all_id(self, keyword, last_page):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }

        urls = [f'https://www.turbosquid.com/3d-model/{keyword}?page_num={page_num}&page_size=500&sort_column=a7&sort_order=desc' for page_num in range(1, int(last_page)+1)]

        async with httpx.AsyncClient(proxies=proxies) as client:
            tasks = [asyncio.create_task(self.fetch_id(client,url)) for url in urls[0:2]]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses


    def parse_id(self, responses):
        staging_loc = 'div#SearchResultAssets > div.search-lab.AssetTile-md.tile-large'
        detail_url_loc = 'div.AssetInner > div'
        for response in responses:
            tree = HTMLParser(response)
            staging = tree.css(staging_loc)
            item_ids = [article.css_first(detail_url_loc).attributes['data-id'] for article in staging]
        return item_ids


    async def fetch_detail(self, client, url):
        response = await client.get(url, timeout=10.0)
        return response.json()


    async def fetch_all_detail(self, ids):
        proxies = {
            'http://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}',
            'https://': f'http://{creds.proxy_username}:{creds.proxy_password}@{creds.proxy_url}:{creds.proxy_port}'
        }

        urls = [f'https://www.turbosquid.com/API/v1/Search/Preview/{id}' for id in ids if id.isnumeric()]
        async with httpx.AsyncClient(proxies=proxies) as client:
            tasks = [asyncio.create_task(self.fetch_detail(client,url)) for url in urls]
            datas = await asyncio.gather(*tasks, return_exceptions=True)
            return datas


    def parse_detail(self, responses):
        datas = []
        for response in responses:
            json_data = response
            # json_formatted_str = json.dumps(json_data, indent=2)
            # print(json_formatted_str)
            model_name = json_data['STCPRODUCT']['PRODUCT_NAME']
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
                    'li#preview_details_specification_unwarped_uvs'):
                unwarped_uvs = 'Yes'
            else:
                unwarped_uvs = 'No'
            if HTMLParser(json_data['STCPRODUCT']['SPECIFICATIONS_HTML']).css_first(
                    'li#preview_details_specification_uv_mapped'):
                uv_mapped = 'Yes'
            else:
                uv_mapped = 'No'

            data = asdict(Item(model_name=model_name,
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
                                unwarped_uvs=unwarped_uvs,
                                uv_mapped=uv_mapped))
            datas.append(data)
        return datas


    def to_csv(self, datas, filename):
        headers = ['model_name', 'product_id', 'publish_date', 'page_link', 'download_link', 'price', 'model_license',
                   'format', 'polygons', 'vertices', 'textures', 'materials', 'unwarped_uvs', 'uv_mapped']
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

    def get_cookies(self, url, ):
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        ff_opt = Options()
        # ff_opt.add_argument('-headless')
        ff_opt.add_argument('--no-sanbox')
        ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.page_load_strategy = 'eager'
        driver = WebDriver(options=ff_opt)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar-menu.anonymous'))).click()
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'input#authentication_method_email'))).send_keys(
            creds.username + Keys.RETURN)
        # el = driver.find_element(By.CSS_SELECTOR, 'form#new_user > input[name="utf8"]')
        # ActionChains(driver).move_to_element(el).click(el).send_keys(pw + Keys.RETURN).perform()
        element = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input#user_password')))
        element.click()
        element.send_keys(creds.pw + Keys.RETURN)

        # driver.close()
        return

    async def main(self):
        keyword = input('What do you want to search? ')
        print('Getting Product IDs...')
        last_page = self.get_page(keyword)
        responses = await self.fetch_all_id(keyword, last_page)
        ids = s.parse_id(responses)
        print('Getting Details...')
        responses = await self.fetch_all_detail(ids)
        datas = s.parse_detail(responses)
        print(f'Saving data to {keyword}_result.csv')
        s.to_csv(datas, f'{keyword}_result.csv')
        print('Scraping data is done!')

if __name__ == '__main__':
    s=Scraper()
    asyncio.run(s.main())