import urllib.parse
import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
from urllib.parse import unquote, quote_plus
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

    def webdriver_setup(self):
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        ff_opt = Options()
        # ff_opt.add_argument('-headless')
        ff_opt.add_argument('--no-sanbox')
        ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.page_load_strategy = 'eager'

        driver = WebDriver(options=ff_opt)
        return driver

    def get_download_link(self, driver, url, username, pw, free_id):
        driver.get(url)

        #login
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar-menu.anonymous'))).click()
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#authentication_method_email'))).send_keys(username + Keys.RETURN)
        element = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input#user_password')))
        element.click()
        element.send_keys(pw + Keys.RETURN)

        #search
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#NavTextField'))).send_keys(free_id + Keys.RETURN)
        download_loc = (By.CSS_SELECTOR, 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button')
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable(download_loc))
        cookies = driver.get_cookies()

        # logout
        element = driver.find_element(By.CSS_SELECTOR, 'div.user-wrap > a#nav_login')
        element.move_to_element(element)
        WebDriverWait(driver,10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.content.content-model.user > ul > li:nth-of-type(5) > a'))).click()
        # driver.close()
        return cookies

    def to_download_page(self, cookies, free_urls):
        cookie_jar = dict()
        for item in cookies:
            cookie_jar[f"{item['name']}"] = item['value']
        print(cookie_jar)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        }
        s = httpx.Client(headers=headers, cookies=cookie_jar)
        response = s.get('https://auth.turbosquid.com/users/sign_in')

    def get_free_urls(self):
        df = pd.read_csv('sofa_result.csv')
        free_urls = list(df[df['price']=='Free']['page_link'])
        free_ids = list(df[df['price']=='Free']['product_id'])
        return free_urls, free_ids

if __name__ == '__main__':
    base_url = 'https://www.turbosquid.com'
    d = Download_link()
    free_urls, free_ids= d.get_free_urls()
    driver = d.webdriver_setup()
    cookies = d.get_download_link(driver, base_url, username=creds.username, pw=creds.pw, free_id=free_ids[0])

    # print('=======================================')
    # print(d.to_download_page(cookies))

