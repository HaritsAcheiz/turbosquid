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

    def webdriver_setup(self):
        useragent = 'Mozilla / 5.0(Windows NT 10.0; WOW64; rv: 52.0) Gecko / 20100101 Firefox / 52.0'
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

    def get_download_link(self, driver, url, username, pw, free_id):
        driver.fullscreen_window()
        driver.get(url)
        wait = WebDriverWait(driver, 30)

        # login
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar-menu.anonymous'))).click()
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#authentication_method_email'))).send_keys(username + Keys.RETURN)
        element = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input#user_password')))
        element.click()
        element.send_keys(pw + Keys.RETURN)

        for id in free_id:
            # search
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#NavTextField'))).send_keys(str(id) + Keys.RETURN)

            # detail page
            wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'h1[itemprop="name"]')))
            button = driver.find_element(By.CSS_SELECTOR, ".addToCartBtn")
            driver.execute_script("arguments[0].click();", button)

            # download_loc = 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button'
            # download_loc = '.addToCartBtn'
            # obs = (By.CSS_SELECTOR, '#coupon')
            # wait.until(ec.invisibility_of_element(obs))
            # print(driver.find_element(By.TAG_NAME, 'html').get_attribute('outerHTML'))
            # driver.find_element(By.CSS_SELECTOR, download_loc).click()

            # download page
            wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '.normalFileIcon')))
            cookies = driver.get_cookies()

            # # logout
            # element = driver.find_element(By.CSS_SELECTOR, 'div.user-wrap > a#nav_login')
            # hidden_element = driver.find_element(By.CSS_SELECTOR, 'div.content.content-model.user > ul > li:nth-of-type(5) > a')
            # ActionChains(driver).move_to_element(element).click(hidden_element)
            # # WebDriverWait(driver,10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.content.content-model.user > ul > li:nth-of-type(5) > a'))).click()

        driver.close()
        return cookies

    def to_download_page(self, cookies, free_urls):
        cookie_jar = dict()
        for item in cookies:
            cookie_jar[f"{item['name']}"] = item['value']
        print(cookie_jar)
        headers = {
            'User-Agent': 'Mozilla / 5.0(Windows NT 10.0; WOW64; rv: 52.0) Gecko / 20100101 Firefox / 52.0'
        }
        s = httpx.Client(headers=headers)
        for cookie in cookie_jar:
            s.cookies.set(cookie['name'], cookie['value'])
        response = s.get('https://auth.turbosquid.com/users/sign_in')
        print(response)

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
    d.get_download_link(driver, base_url, username=creds.username, pw=creds.pw, free_id=free_ids)
    # print('=======================================')
    # print(d.to_download_page(cookies, free_urls=free_urls))
