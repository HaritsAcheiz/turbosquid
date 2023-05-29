import os
import glob
import time

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
        ff_opt.add_argument('-headless')
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

        # with httpx.Client(headers=headers, follow_redirects=True) as client:
        #     response = client.get(url)
        # with open(filepath, "wb") as f:
        #     f.write(response.content)

        with httpx.stream("GET", url, follow_redirects=True, headers=headers) as response:
            with open(filepath, "wb") as file:
                for chunk in response.iter_raw():
                    file.write(chunk)

        # with httpx.Client(headers=headers, follow_redirects=True) as client:
        #     with open(filepath, "wb") as file:
        #         response = client.get(url, stream=True)
        #         for chunk in response.iter_bytes():
        #             file.write(chunk)


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
        while 1:
            try:
                wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div#divEmptyStateScreenContainer')))
                break
            except:
                items = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody.yui-dt-data > tr')))
                print('Downloading...')
                for i, item in enumerate(items,start=1):
                    if item.get_attribute('class') != 'ProductFileRow ThumbnailsRow show':
                        folderpath = os.path.join(os.getcwd(), fr"result\{item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').strip().split('/')[-1]}")
                        os.makedirs(folderpath, exist_ok=True)
                    else:
                        try:
                            item.find_element(By.CSS_SELECTOR, 'div.RowAction.ActionShowAll').click()
                        except:
                            pass
                        subitems = item.find_elements(By.CSS_SELECTOR, 'a')
                        for subitem in subitems:
                            filepath = fr'{folderpath}\{subitem.text}'
                            url = subitem.get_attribute('href')
                            self.downloadContent(filepath=filepath, url=url)
                    driver.find_element(By.CSS_SELECTOR, 'input.cbItemSelectAll').click()
                    driver.find_element(By.CSS_SELECTOR, 'div#miRemove').click()
                    wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'span.yui-button:nth-child(1)'))).click()


        driver.close()


    def get_free_ids(self):
        folder_path = os.path.join(os.getcwd(), 'ids')
        file_pattern = '*.csv'
        file_paths = glob.glob(os.path.join(folder_path, file_pattern))

        data_list = []
        for file_path in file_paths:
            df = pd.read_csv(file_path)
            data_list.append(df)
        combined_df = pd.concat(data_list)

        return list(combined_df['product_id'])


    def main(self):
        print("Getting cookies...")
        cookies = self.getCookies()
        print("Reading ids...")
        free_ids = self.get_free_ids()
        for i, id in enumerate(free_ids, start=1):
            retries = 3
            retry_delay = 1
            for _ in range(retries):
                if id != free_ids[-1]:
                    try:
                        print(f"Adding item {id}...({i} of {len(free_ids)})")
                        self.exportItem(id, cookies=cookies)
                        break
                    except Exception as e:
                        print(f"Retrying due to {e}...")
                        time.sleep(retry_delay)
                else:
                    try:
                        print(f"Adding item {id}...({i} of {len(free_ids)})")
                        self.toDownloadPage(id, cookies=cookies)
                        print("Download Completed")
                        break
                    except Exception as e:
                        print(f"Retrying due to {e}...")
                        time.sleep(retry_delay)

if __name__ == '__main__':
    d = Download_link()
    d.main()
