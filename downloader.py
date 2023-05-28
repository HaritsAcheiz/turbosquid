import os
import httpx
from dataclasses import dataclass
import creds
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd

@dataclass
class Download_link:

    base_url:str = 'https://www.turbosquid.com'


    def webdriver_setup(self):
        useragent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        latitude = 37.7749
        longitude = -122.4194
        ff_opt = Options()
        # ff_opt.add_argument('-headless')
        ff_opt.add_argument('--no-sanbox')
        ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.page_load_strategy = 'eager'

        ff_opt.set_preference('geo.enabled', True)
        ff_opt.set_preference('geo.provider.use_corelocation', False)
        ff_opt.set_preference('geo.prompt.testing', True)
        ff_opt.set_preference('geo.prompt.testing.allow', True)
        ff_opt.set_preference('geo.wifi.uri', 'data:application/json,{"location": {"lat": ' + str(latitude) + ', "lng": ' + str(longitude) + '}, "accuracy": 100.0}')

        driver = WebDriver(options=ff_opt)
        return driver


    def getCookies(self):
        driver = self.webdriver_setup()
        driver.fullscreen_window()
        driver.get(self.base_url)
        wait = WebDriverWait(driver, 20)

        # login
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar-menu.anonymous'))).click()
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#authentication_method_email'))).send_keys(creds.username + Keys.RETURN)
        element = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input#user_password')))
        element.click()
        element.send_keys(creds.pw + Keys.RETURN)
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#NavTextField')))
        cookies = driver.get_cookies()
        driver.close()
        return cookies


    def exportItem(self, id, cookies):
        driver = self.webdriver_setup()
        driver.fullscreen_window()
        driver.get(self.base_url)
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        wait = WebDriverWait(driver, 20)
        driver.get(f'https://www.turbosquid.com/FullPreview/{id}')

        # detail page
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button'))).click()

        driver.close()


    def downloadContent(self, filepath, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        }

        with httpx.Client(headers=headers) as client:
            response = client.get(url)
        with open(filepath, "wb") as f:
            f.write(response.content)


    def toDownloadPage(self, id, cookies):
        driver = self.webdriver_setup()
        driver.fullscreen_window()
        driver.get(self.base_url)
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        wait = WebDriverWait(driver, 20)
        driver.get(f'https://www.turbosquid.com/FullPreview/{id}')

        # detail page
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button'))).click()

        # download page
        items = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody.yui-dt-data > tr')))
        for i, item in enumerate(items,start=1):
            if item.get_attribute('class') != 'ProductFileRow ThumbnailsRow show':
                folderpath = os.path.join(os.getcwd(), fr"result\{item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').strip().split('/')[-1]}")
                os.makedirs(folderpath, exist_ok=True)
            else:
                item.find_element(By.CSS_SELECTOR, 'div.RowAction.ActionShowAll').click()
                subitems = item.find_elements(By.CSS_SELECTOR, 'a')
                for subitem in subitems:
                    filepath = fr'{folderpath}\{subitem.text}'
                    url = subitem.get_attribute('href')
                    self.downloadContent(filepath=filepath, url=url)
        driver.find_element(By.CSS_SELECTOR, 'input.cbItemSelectAll').click()
        driver.find_element(By.CSS_SELECTOR, 'div#miRemove').click()
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'span.yui-button:nth-child(1)'))).click()
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div#divEmptyStateScreenContainer')))
        driver.close()


    def get_free_ids(self):
        df = pd.read_csv('sofa_result.csv')
        free_ids = list(df[df['price'] == 'Free']['product_id'])
        return free_ids


    def main(self):
        # cookies = self.getCookies()
        # print(cookies)
        cookies = [{'name': '_gaexp', 'value': 'GAX1.2.SNZDkz_8Q9mdK2o-StOSYQ.19589.1!siH7jPeaSTWjI9V3wjuEGA.19594.1', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1692921600, 'sameSite': 'None'}, {'name': '_gcl_au', 'value': '1.1.1068677332.1685224236', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1693000236, 'sameSite': 'None'}, {'name': '_ga', 'value': 'GA1.2.610493474.1685224237', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1748296236, 'sameSite': 'None'}, {'name': '_gid', 'value': 'GA1.2.792416333.1685224237', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685310636, 'sameSite': 'None'}, {'name': '_gat_UA-227915-1', 'value': '1', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685224296, 'sameSite': 'None'}, {'name': '_clck', 'value': '1b1k9pe|2|fby|0|1242', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1716760237, 'sameSite': 'None'}, {'name': 'SnapABugRef', 'value': 'https%3A%2F%2Fwww.turbosquid.com%2F%20', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1685231438, 'sameSite': 'None'}, {'name': 'SnapABugHistory', 'value': '1#', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1716760238, 'sameSite': 'None'}, {'name': 'SnapABugUserAlias', 'value': '%23', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1716760238, 'sameSite': 'None'}, {'name': 'SnapABugVisit', 'value': '1#1685224238', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'sameSite': 'None'}, {'name': 'cfid', 'value': '53840d57-2d9b-4cae-9012-82431bc5711e', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 2631850930, 'sameSite': 'None'}, {'name': 'cftoken', 'value': '0', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 2631850930, 'sameSite': 'None'}, {'name': 'M', 'value': '637EEB26-CC53-406C-A42F-43F219BEE6C3', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 2631850930, 'sameSite': 'None'}, {'name': '_uetsid', 'value': '8518c6e0fcd811eda48745e65ec5379c', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685310644, 'sameSite': 'None'}, {'name': '_uetvid', 'value': '8518ea80fcd811ed8ac2e5690cef7633', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1718920244, 'sameSite': 'None'}, {'name': '_clsk', 'value': '1cs2oao|1685224246596|2|1|x.clarity.ms/collect', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685310646, 'sameSite': 'None'}, {'name': 'M20UR15', 'value': '%7B%22s%22%3A%22F4CEA8B6-91CB-4253-9975-A1741A50FAB9%22%2C%22csrf%22%3A%226192FC468082A75B4563ED621AA6B4967B65F114%22%2C%22d%22%3A%222023-05-27T21%3A55%3A40Z%22%2C%22clnt%22%3A%221%22%2C%22name%22%3A%22KM-member3536253678%22%2C%22email%22%3A%22naruoutlet%40gmail.com%22%2C%22industry%22%3A%22Game%20Developer%20-%20PC%2FConsole%2FMobile%22%2C%22application%22%3A%223ds%20Max%22%2C%22engine%22%3A%22Unity%22%7D', 'path': '/', 'domain': '.www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1687816250, 'sameSite': 'None'}, {'name': '_M20UR15', 'value': 'A7338C7B32EB257E3F2CA7F4AB3913BF', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 1686088250, 'sameSite': 'None'}, {'name': 'OSD', 'value': '%7B%22eligible_cart%22%3A0%2C%22code%22%3A%22%22%7D', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685397050, 'sameSite': 'None'}, {'name': '_hp2_props.3723677730', 'value': '%7B%22Logged%20In%22%3A%22true%22%7D', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1719301850, 'sameSite': 'Lax'}, {'name': '_hp2_ses_props.3723677730', 'value': '%7B%22z%22%3A0%2C%22ts%22%3A1685224239478%2C%22d%22%3A%22www.turbosquid.com%22%2C%22h%22%3A%22%2F%22%2C%22t%22%3A%223D%20Models%20for%20Professionals%20%3A%3A%20TurboSquid%22%7D', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685226050, 'sameSite': 'Lax'}, {'name': '_hp2_id.3723677730', 'value': '%7B%22userId%22%3A%226611536676460406%22%2C%22pageviewId%22%3A%223129088425086254%22%2C%22sessionId%22%3A%221464417461816490%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1719301850, 'sameSite': 'Lax'}]
        free_ids = self.get_free_ids()
        for id in free_ids:
            if id != free_ids[-1]:
                self.exportItem(id, cookies=cookies)
            else:
                self.toDownloadPage(id, cookies=cookies)

if __name__ == '__main__':
    d = Download_link()
    d.main()
