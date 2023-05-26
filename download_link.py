import time

import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import creds
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains

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
        wait = WebDriverWait(driver, 30)

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
        wait = WebDriverWait(driver, 10)
        driver.get(f'https://www.turbosquid.com/FullPreview/{id}')

        # detail page
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button'))).click()
        # time.sleep(1)
        button_url = driver.current_url
        driver.close()
        return button_url


    def toDownloadPage(self, url, cookies):
        driver = self.webdriver_setup()
        driver.fullscreen_window()
        driver.get(self.base_url)
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        driver.implicitly_wait(10)
        driver.close()


    def get_free_ids(self):
        df = pd.read_csv('sofa_result.csv')
        free_ids = list(df[df['price'] == 'Free']['product_id'])
        return free_ids


    def main(self):
        # cookies = self.getCookies()
        # print(cookies)
        cookies = [{'name': '_gaexp', 'value': 'GAX1.2.SNZDkz_8Q9mdK2o-StOSYQ.19589.1!siH7jPeaSTWjI9V3wjuEGA.19594.0', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1692921600, 'sameSite': 'None'}, {'name': '_gcl_au', 'value': '1.1.1217554792.1685132188', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1692908188, 'sameSite': 'None'}, {'name': '_hp2_props.3723677730', 'value': '%7B%7D', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1719209788, 'sameSite': 'Lax'}, {'name': '_ga', 'value': 'GA1.2.1280599239.1685132189', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1748204188, 'sameSite': 'None'}, {'name': '_gid', 'value': 'GA1.2.2003663997.1685132189', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685218588, 'sameSite': 'None'}, {'name': '_gat_UA-227915-1', 'value': '1', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685132248, 'sameSite': 'None'}, {'name': '_clck', 'value': '12gbnkc|2|fbx|0|1241', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1716668189, 'sameSite': 'None'}, {'name': 'SnapABugRef', 'value': 'https%3A%2F%2Fwww.turbosquid.com%2F%20', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1685139389, 'sameSite': 'None'}, {'name': 'SnapABugHistory', 'value': '1#', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1716668189, 'sameSite': 'None'}, {'name': 'SnapABugUserAlias', 'value': '%23', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1716668189, 'sameSite': 'None'}, {'name': 'SnapABugVisit', 'value': '1#1685132190', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': False, 'sameSite': 'None'}, {'name': 'cfid', 'value': '0452158b-5def-4ad6-8cae-ed481b516c2e', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 2631758882, 'sameSite': 'None'}, {'name': 'cftoken', 'value': '0', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 2631758882, 'sameSite': 'None'}, {'name': 'M', 'value': 'B9B011FF-850A-4CFF-9C46-30EEF14888F9', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 2631758882, 'sameSite': 'None'}, {'name': '_uetsid', 'value': '3508ae00fc0211eda023cf243879079c', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685218598, 'sameSite': 'None'}, {'name': '_uetvid', 'value': '3508d850fc0211edade133b93b688895', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1718828198, 'sameSite': 'None'}, {'name': '_hp2_ses_props.3723677730', 'value': '%7B%22ts%22%3A1685132192844%2C%22d%22%3A%22www.turbosquid.com%22%2C%22h%22%3A%22%2F%22%7D', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685133998, 'sameSite': 'Lax'}, {'name': '_hp2_id.3723677730', 'value': '%7B%22userId%22%3A%227704569345787039%22%2C%22pageviewId%22%3A%227951262828186356%22%2C%22sessionId%22%3A%227477514024191006%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1719209798, 'sameSite': 'Lax'}, {'name': '_clsk', 'value': '1a30fes|1685132199506|2|1|x.clarity.ms/collect', 'path': '/', 'domain': '.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685218599, 'sameSite': 'None'}, {'name': 'M20UR15', 'value': '%7B%22s%22%3A%22222830DE-12BA-4DB8-B7FD-014F8EC8210F%22%2C%22csrf%22%3A%220C3C5867A30358F968D42CF44D12A001F489CB15%22%2C%22d%22%3A%222023-05-26T20%3A21%3A32Z%22%2C%22clnt%22%3A%221%22%2C%22name%22%3A%22KM-member3536253678%22%2C%22email%22%3A%22naruoutlet%40gmail.com%22%2C%22industry%22%3A%22Game%20Developer%20-%20PC%2FConsole%2FMobile%22%2C%22application%22%3A%223ds%20Max%22%2C%22engine%22%3A%22Unity%22%7D', 'path': '/', 'domain': '.www.turbosquid.com', 'secure': True, 'httpOnly': False, 'expiry': 1687724201, 'sameSite': 'None'}, {'name': '_M20UR15', 'value': '79AF88A761C9B45DE0D81A530BA8405D', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': True, 'httpOnly': True, 'expiry': 1685996201, 'sameSite': 'None'}, {'name': 'OSD', 'value': '%7B%22eligible_cart%22%3A0%2C%22code%22%3A%22%22%7D', 'path': '/', 'domain': 'www.turbosquid.com', 'secure': False, 'httpOnly': False, 'expiry': 1685305001, 'sameSite': 'None'}]
        free_ids = self.get_free_ids()
        for id in free_ids:
            button_url = self.exportItem(id, cookies=cookies)
        self.toDownloadPage(url=button_url, cookies=cookies)


        # button_url = self.exportItem(free_ids, cookies=cookies)
        # print(button_url)
        # self.toDownloadPage(url=button_url, cookies=cookies)


if __name__ == '__main__':
    d = Download_link()
    d.main()
