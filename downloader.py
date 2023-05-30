import os
import glob
import time

from dataclasses import dataclass

from selenium.common import TimeoutException, StaleElementReferenceException

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
    download_directory: str = os.path.join(os.getcwd(), 'downloads')


    def webdriver_setup(self):
        # useragent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        useragent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/113.0'
        latitude = 37.7800
        longitude = -122.4200
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
        ff_opt.set_preference("browser.download.folderList", 2)
        ff_opt.set_preference("browser.download.manager.showWhenStarting", False)
        ff_opt.set_preference("browser.download.dir", self.download_directory)
        ff_opt.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

        driver = WebDriver(options=ff_opt)
        return driver


    def getCookies(self):
        driver = self.webdriver_setup()
        # driver.fullscreen_window()
        driver.maximize_window()
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


    # def downloadContent(self, filepath, url):
    #
    #     # Step 1: Get the actual download URL
    #     with httpx.Client() as client:
    #         response = client.get(url, follow_redirects=False)
    #         download_url = response.headers["Location"]
    #
    #     # Step 2: Download the file
    #     with httpx.stream("GET", download_url) as response:
    #         with open("Sofa_Set_01.fbx", "wb") as file:
    #             for chunk in response.iter_bytes():
    #                 file.write(chunk)
    #
    #     print("File downloaded successfully.")

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Connection': 'keep-alive',
    #     'Upgrade-Insecure-Requests': '1',
    #     'Sec-Fetch-Dest': 'document',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Sec-Fetch-Site': 'none',
    #     'Sec-Fetch-User': '?1'
    # }

    # with httpx.Client(headers=headers, follow_redirects=True) as client:
    #     response = client.get(url)
    # with open(filepath, "wb") as f:
    #     f.write(response.content)

    # with httpx.stream("GET", url, follow_redirects=True, headers=headers) as response:
    #     with open(filepath, "wb") as file:
    #         for chunk in response.iter_raw():
    #             file.write(chunk)

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
        while 1:
            try:
                wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div#divEmptyStateScreenContainer')))
                break
            except TimeoutException:
                # download page
                items = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody.yui-dt-data > tr')))
                print('Downloading...')
                count_of_files = 0
                for i in range(1, len(items) + 1):
                    subitems=[]
                    while 1:
                        try:
                            item = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'tbody.yui-dt-data > tr:nth-of-type({str(i)})')))
                            item.get_attribute('class')
                            break
                        except StaleElementReferenceException:
                            driver.refresh()
                    if item.get_attribute('class') != 'ProductFileRow ThumbnailsRow show':
                        folderpath = os.path.join(os.getcwd(), fr"downloads\{item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').strip().split('/')[-1]}")
                        # os.makedirs(folderpath, exist_ok=True)
                    else:
                        try:
                            WebDriverWait(item, 20).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.RowAction.ActionShowAll'))).click()
                        except:
                            pass
                        subitems = WebDriverWait(item,20).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'a')))
                        # for j in range(1, len(subitems)+1):
                        #     subitem = item.find_element(By.CSS_SELECTOR, f'a:nth-of-type({str(j)})')
                        #     filepath = fr'{folderpath}\{subitem.text}'
                        #     subitem.click()
                        for subitem in subitems:
                            print(subitem.text)
                            print(subitem.get_attribute('outerHTML'))
                            subitem.click()
                            # filepath = fr'{folderpath}\{subitem.text}'
                            count_of_files += 1
                    while 1:
                        time.sleep(3)
                        print("waiting")
                        # Check if the download directory has any new files
                        files = os.listdir(self.download_directory)
                        if (count_of_files == len(files)):
                            # File download is completed
                            break
                            # url = subitem.get_attribute('href')
                            # self.downloadContent(filepath=filepath, url=url)
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
        os.makedirs(self.download_directory, exist_ok=True)
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
                    # try:
                    print(f"Adding item {id}...({i} of {len(free_ids)})")
                    self.toDownloadPage(id, cookies=cookies)
                    print("Download Completed")
                    break
                    # except Exception as e:
                        # print(f"Retrying due to {e}...")
                        # time.sleep(retry_delay)

if __name__ == '__main__':
    d = Download_link()
    d.main()
