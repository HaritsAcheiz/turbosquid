import httpx
from selectolax.parser import HTMLParser
import json
import asyncio
from dataclasses import dataclass

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


    async def fetch_id(self, client, url):
        staging_loc = 'div#SearchResultAssets > div.search-lab.AssetTile-md.tile-large'
        detail_url_loc = 'div.AssetInner > div'
        response = await client.get(url)
        tree = HTMLParser(response.text)
        staging = tree.css(staging_loc)
        item_ids = [article.css_first(detail_url_loc).attributes['data-id'] for article in staging]
        return item_ids

    async def fetch_all_id(self):
        async with httpx.AsyncClient() as client:
            tasks = []
            for page_num in range(2):
                url = f'https://www.turbosquid.com/3d-model/sofa?page_num={page_num}&page_size=500&sort_column=a7&sort_order=desc'
                tasks.append(self.fetch_id(client,url))

            item_ids = await asyncio.gather(*tasks)
            results = []
            for group_id in item_ids:
                results.extend(group_id)
            return results

    async def fetch_detail(self, client, url):
        response = await client.get(url)
        json_data = response.json()
        json_formatted_str = json.dumps(json_data, indent=2)
        # print(json_formatted_str)
        return json_formatted_str

    async def fetch_all_detail(self, ids):
        async with httpx.AsyncClient() as client:
            tasks = []
            for id in ids[0:2]:
                url = f'https://www.turbosquid.com/API/v1/Search/Preview/{id}'
                tasks.append(self.fetch_id(client,url))

            data = await asyncio.gather(*tasks)
            print(data)

            # return

if __name__ == '__main__':
    s=Scraper()
    ids = asyncio.run(s.fetch_all_id())
    print(ids)
#
#
# url = f'https://www.turbosquid.com/3d-model/sofa?page_num={page_num}&page_size=500&sort_column=a7&sort_order=desc'

# if __name__ == '__main__':
#     with httpx.Client() as client:
#         headers2 = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
#             # 'Accept': 'application/json, text/javascript, */*; q=0.01',
#             # 'Accept-Language': 'en-US,en;q=0.5',
#             # 'Accept-Encoding': 'gzip, deflate, br',
#             # 'X-Requested-With': 'XMLHttpRequest',
#             # 'Connection': 'keep-alive',
#             # 'Referer': 'https://www.turbosquid.com/3d-model/sofa',
#             # 'Sec-Fetch-Dest': 'empty',
#             # 'Sec-Fetch-Mode': 'cors',
#             # 'Sec-Fetch-Site': 'same-origin'
#         }
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
#             # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#             # 'Accept-Language': 'en-US,en;q=0.5',
#             # 'Accept-Encoding': 'gzip, deflate, br',
#             # 'Referer': 'https://www.turbosquid.com/?&utm_source=google&utm_medium=cpc&utm_campaign=RoAsia-en-TS-Brand&utm_content=Brand-TurboSquid&utm_term=turbosquid&mt=e&dev=c&itemid=&targid=kwd-297496938642&loc=9072593&ntwk=g&dmod=&adp=&gclid=CjwKCAjwgqejBhBAEiwAuWHioLyF2JRBqOjUWgfjwDFU8deo7iAObptWjgqW7rtE5dh9uzQ5frw_dRoCFgQQAvD_BwE&gclsrc=aw.ds',
#             # 'Connection': 'keep-alive',
#             # 'Upgrade-Insecure-Requests': '1',
#             # 'Sec-Fetch-Dest': 'document',
#             # 'Sec-Fetch-Mode': 'navigate',
#             # 'Sec-Fetch-Site': 'same-origin',
#             # 'Sec-Fetch-User': '?1'
#         }
#         client.get('https://www.turbosquid.com/3d-model/sofa?page_size=500&sort_column=a7&sort_order=desc', headers=headers)
#         response = client.get('https://www.turbosquid.com/API/v1/Search/Preview/1286600', headers=headers2)
#         print(response.json())