import urllib.parse

import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
from urllib.parse import unquote, quote_plus

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import ActionChains

@dataclass
class Download_link:

    def webdriver_setup(self):
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        ff_opt = Options()
        # ff_opt.add_argument('-headless')
        ff_opt.add_argument('--no-sanbox')
        ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.page_load_strategy = 'eager'

        driver = WebDriver(options=ff_opt)
        return driver

    def get_download_link(self, driver, url, username, pw):
        driver.get(url)
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar-menu.anonymous'))).click()
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#authentication_method_email'))).send_keys(username + Keys.RETURN)
        print(driver.current_url)
        el = driver.find_element(By.CSS_SELECTOR, 'form#new_user > input[name="utf8"]')
        ActionChains(driver).move_to_element(el).click(el).send_keys(pw + Keys.RETURN).perform()
        # WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#user_password'))).send_keys(pw + Keys.RETURN)
        print(driver.title)
        # driver.close()
        return

    # def to_download_page(self, cookies):
    #     cookie_jar = dict()
    #     for item in cookies:
    #         cookie_jar[f"{item['name']}"] = item['value']
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
    #     }
    #     s = httpx.Client(headers=headers, cookies=cookie_jar)
    #     response = s.get('https://auth.turbosquid.com/users/sign_in')
    #     return response
        # url = unquote('https://auth.turbosquid.com/users/authentication_method?locale=en&utf8=%E2%9C%93&authentication_method%5Bemail%5D=naruoutlet%40gmail.com&commit=Continue')
        # response_payload = s.get(url)
        # print(response_payload)

if __name__ == '__main__':
    base_url = 'https://www.turbosquid.com'
    username = 'naruoutlet@gmail.com'
    pw = 'mitsutani'
    d = Download_link()
    driver = d.webdriver_setup()
    d.get_download_link(driver, base_url, username=username, pw=pw)
    # print('=======================================')
    # print(d.to_download_page(cookies))

