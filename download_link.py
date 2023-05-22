import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
from urllib.parse import unquote


@dataclass
class Download_link:

    def to_download_page(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            # 'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Referer': 'https://www.turbosquid.com/',
            # 'Connection': 'keep-alive',
            # 'Cookie': '_gcl_au=1.1.1435640332.1684135211; _hp2_props.3723677730=%7B%22suggestions_version%22%3A%221%22%7D; _gaexp=GAX1.2.SNZDkz_8Q9mdK2o-StOSYQ.19589.0; _gcl_aw=GCL.1684744225.CjwKCAjwgqejBhBAEiwAuWHioLyF2JRBqOjUWgfjwDFU8deo7iAObptWjgqW7rtE5dh9uzQ5frw_dRoCFgQQAvD_BwE; _gcl_dc=GCL.1684744225.CjwKCAjwgqejBhBAEiwAuWHioLyF2JRBqOjUWgfjwDFU8deo7iAObptWjgqW7rtE5dh9uzQ5frw_dRoCFgQQAvD_BwE; _ga=GA1.2.1396011755.1684730612; _gid=GA1.2.118536761.1684730612; _gac_UA-227915-1=1.1684730612.CjwKCAjwgqejBhBAEiwAuWHioLyF2JRBqOjUWgfjwDFU8deo7iAObptWjgqW7rtE5dh9uzQ5frw_dRoCFgQQAvD_BwE; _clck=m4j9g4|2|fbt|0|1237; _clsk=ua9yea|1684795510699|20|1|s.clarity.ms/collect; _hp2_id.3723677730=%7B%22userId%22%3A%227268574273662309%22%2C%22pageviewId%22%3A%226348416734918648%22%2C%22sessionId%22%3A%222783820719840690%22%2C%22identity%22%3A%22KM-member5930312870%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%7D; __ssid=3a0299cee6dffbd05fb0828e6739d36; stck_anonymous_id=a581ad49-d5c4-4c55-bf7a-e57c49688df5; sstk_anonymous_id=a581ad49-d5c4-4c55-bf7a-e57c49688df5; ajs_anonymous_id=a581ad49-d5c4-4c55-bf7a-e57c49688df5; _keymaster_session=K1I5bmxIUVpNRitRM2JPd05TM2V1MWRuUG1XWWU5VkJkMGhMZTU5TmJ3M3V3OWpsRERXa3BOUGZQL29qRklwZUxBbU9FTTF3UkNiOHRLTUFRR3JUaWFOSjVzWXFidDNLOUJHaVlweXU4UjZ2eFJ3SDRIWVJpV1M1Q0NXMFhCY284ZmNUaW5vMlZWUWdqSzNpSEFsbGpQU3BRdDUrSmx6cDZpNEF0aHJyaFRnN0JVWWJCSGxTWHZ5RzF4YnNJY1Fiakg4akpmd3VQTzRMM2hqcHBvUVo5bkVldWtNZVltU0Jya1ZjSEpRbDJCZ3R4K01lanFHTDUrL282dG9MK3BiYmdzaWRleUw3THlJVjhLOHBIZFNSRHc9PS0tSDR2alpONzNmbVVUQjU0REFQN2tGUT09--f129f25b6628a47f2b79d6173cb7180b32cceafd; client_uid=eyJfcmFpbHMiOnsibWVzc2FnZSI6IklqTTROREUzTkRBNExUYzRNMk10TkdReU55MWlPV1UyTFRZd016bGtNVE5qWmpOall5ST0iLCJleHAiOiIyMDQzLTA1LTIyVDIyOjEyOjM1LjM0MloiLCJwdXIiOm51bGx9fQ%3D%3D--5a317116eeea323b2be39e8c0a957919f2a1ca29; _hp2_ses_props.3723677730=%7B%22ts%22%3A1684794566879%2C%22d%22%3A%22www.turbosquid.com%22%2C%22h%22%3A%22%2FFullPreview%2F2072922%22%7D; _uetsid=4ed26fa0f85b11ed8dce21ece622d157; _uetvid=4ed25c60f85b11ed900b99221ff03e2d',
            # 'Upgrade-Insecure-Requests': '1',
            # 'Sec-Fetch-Dest': 'document',
            # 'Sec-Fetch-Mode': 'navigate',
            # 'Sec-Fetch-Site': 'same-site',
            # 'Sec-Fetch-User': '?1',
            # 'If-None-Match': 'W/"35ee7637fbc4b75f64696342fe9135bd"'
        }
        s = httpx.Client(headers=headers)
        response = s.get('https://www.turbosquid.com')
        print(response.request.headers)
        response = s.get('https://auth.turbosquid.com/users/sign_in')
        print(response)
        print(response.request.headers)
        print(response.cookies)
        url = unquote('https://auth.turbosquid.com/users/authentication_method?locale=en&utf8=%E2%9C%93&authentication_method%5Bemail%5D=naruoutlet%40gmail.com&commit=Continue')
        print(url)
        response_payload = s.get(url)
        print(response_payload)

if __name__ == '__main__':
    d = Download_link()
    d.to_download_page()