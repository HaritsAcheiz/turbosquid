import os
import glob
import time
import shutil

from dataclasses import dataclass

from selenium.common import TimeoutException, StaleElementReferenceException

import creds
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
import pandas as pd

@dataclass
class Download_link:

    base_url:str = 'https://www.turbosquid.com'
    download_directory: str = os.path.join(os.getcwd(), 'temp')
    latitude: float = -6.2088
    longitude: float = 106.8456

    def webdriver_setup(self):
        useragent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        # useragent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/113.0'

        ff_opt = Options()
        ff_opt.add_argument('-headless')
        ff_opt.add_argument('--no-sandbox')
        ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.page_load_strategy = 'eager'

        # geolocation
        # latitude = 37.7749
        # longitude = -122.4194
        # ff_opt.set_preference('geo.enabled', True)
        # ff_opt.set_preference('geo.provider.use_corelocation', False)
        # ff_opt.set_preference('geo.prompt.testing', True)
        # ff_opt.set_preference('geo.prompt.testing.allow', True)
        # ff_opt.set_preference('geo.wifi.uri', 'data:application/json,{"location": {"lat": ' + str(latitude) + ', "lng": ' + str(longitude) + '}, "accuracy": 100.0}')

        # download folder
        ff_opt.set_preference("browser.download.folderList", 2)
        ff_opt.set_preference("browser.download.manager.showWhenStarting", False)
        ff_opt.set_preference("browser.download.dir", self.download_directory)
        ff_opt.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

        driver = WebDriver(options=ff_opt)
        return driver

    def getCookies(self):
        driver = self.webdriver_setup()
        driver.execute_script(f"navigator.geolocation.getCurrentPosition = function(success) {{ success({{ coords: {{ latitude: {self.latitude}, longitude: {self.longitude} }} }}); }};")
        # driver.fullscreen_window()
        driver.maximize_window()
        driver.get(self.base_url)
        wait = WebDriverWait(driver, 15)

        # login
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar-menu.anonymous'))).click()
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#authentication_method_email'))).send_keys(creds.username + Keys.RETURN)
        element = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input#user_password')))
        element.click()
        element.send_keys(creds.pw + Keys.RETURN)
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input#NavTextField')))
        cookies = driver.get_cookies()

        print('Cleaning download asset...')
        driver.get(self.base_url+'/AssetManager/Index.cfm')
        while 1:
            try:
                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div#divEmptyStateScreenContainer')))
                break
            except TimeoutException:
                select = Select(driver.find_element(By.CSS_SELECTOR, 'select[title="Rows per page"]'))
                select.select_by_value("500")
                driver.find_element(By.CSS_SELECTOR, 'input.cbItemSelectAll').click()
                driver.find_element(By.CSS_SELECTOR, 'div#miRemove').click()
                wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'span.yui-button:nth-child(1)'))).click()

        driver.close()
        return cookies

    def exportItem(self, id, cookies):
        driver = self.webdriver_setup()
        driver.fullscreen_window()
        driver.get(self.base_url)
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        wait = WebDriverWait(driver, 15)
        driver.get(f'https://www.turbosquid.com/FullPreview/{id}')

        # detail page
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button'))).click()

        driver.close()

    def moveFiles(self, source_folder, destination_folder):
        print(f'Organizing files of {destination_folder}')
        # List all files in the source folder
        files = os.listdir(source_folder)

        # Move each file from the source folder to the destination folder
        for file in files:
            # Construct the source and destination file paths
            source_file = os.path.join(source_folder, file)
            destination_file = os.path.join(destination_folder, file)

            # Move the file to the destination folder
            shutil.move(source_file, destination_file)
        id = destination_folder.split('-')
        if len(id) != 1:
            return id[-1]
        else:
            return destination_folder.split('\\')[-1]

    def checklist(self, id):
        folder_path = os.path.join(os.getcwd(), 'ids')
        file_pattern = '*.csv'
        file_paths = glob.glob(os.path.join(folder_path, file_pattern))
        data_list = []
        for file_path in file_paths:
            df = pd.read_csv(file_path)
            data_list.append(df)
        combined_df = pd.concat(data_list, ignore_index=True)
        combined_df.loc[combined_df['product_id'] == id, 'checklist'] = True
        combined_df.to_csv(file_paths[0], index=False)
        print(f'Item {id} checked!')

    def toDownloadPage(self, id, cookies):
        driver = self.webdriver_setup()
        driver.execute_script(f"navigator.geolocation.getCurrentPosition = function(success) {{ success({{ coords: {{ latitude: {self.latitude}, longitude: {self.longitude} }} }}); }};")
        driver.fullscreen_window()
        driver.get(self.base_url)
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        wait = WebDriverWait(driver, 15)
        driver.get(f'https://www.turbosquid.com/FullPreview/{id}')

        # detail page
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.row_lab > div.shortContainer > div.purchaseSection > div.btn-container > a#FPAddToCart > button'))).click()
        successes = 0
        errors = 0
        while 1:
            # download page
            WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody.yui-dt-data > tr')))
            select = Select(driver.find_element(By.CSS_SELECTOR, 'select[title="Rows per page"]'))
            select.select_by_value("500")
            items = driver.find_elements(By.CSS_SELECTOR, 'tbody.yui-dt-data > tr')
            print(len(items))
            for i in range(1, len(items) + 1):
                os.makedirs(self.download_directory, exist_ok=True)
                while 1:
                    try:
                        item = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'tbody.yui-dt-data > tr:nth-of-type({str(i)})')))
                        item.get_attribute('class')
                        break
                    except StaleElementReferenceException:
                        driver.refresh()
                if item.get_attribute('class') != 'ProductFileRow ThumbnailsRow show':
                    folder_name = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').strip().split('/')[-1]
                    folderpath = os.path.join(os.getcwd(), fr"downloads\{folder_name}")
                    print(f'\nDownloading {folder_name}...')
                    os.makedirs(folderpath, exist_ok=True)
                else:
                    try:
                        WebDriverWait(item, 15).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.RowAction.ActionShowAll'))).click()
                    except:
                        pass
                    subitems = WebDriverWait(item, 15).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'a')))

                    count_of_files = len(subitems)
                    for subitem in subitems:
                        subitem.click()
                        time.sleep(5)

                    print(f"Downloading {str(count_of_files)} items...")
                    counter = 0
                    success = False
                    while counter < 900:
                        print('.', end='')
                        counter +=1
                        tracker = []
                        time.sleep(1)
                        files = [item.lower() for item in os.listdir(self.download_directory)]
                        if len(files) == count_of_files:
                            all_downloads_completed = True
                            for subitem in subitems:
                                if subitem.text.lower().replace(' ', '_') not in files:
                                    all_downloads_completed = False
                                    break
                                else:
                                    tracker.append(subitem.text.lower().replace(' ', '_'))
                                # for i, item in enumerate(tracker):
                                #     print(f'{item} download completed ({len(tracker)} of {str(count_of_files)})')
                            if all_downloads_completed:
                                success = True
                                break
                    if success == True:
                        print(f"\n Download {folder_name} completed!")
                        checklist_id = self.moveFiles(source_folder=self.download_directory, destination_folder=folderpath)
                        self.checklist(int(checklist_id))
                        successes += 1
                    else:
                        print(f"\n Download {folder_name} failed!")
                        errors += 1
                    os.removedirs(self.download_directory)
            driver.find_element(By.CSS_SELECTOR, 'input.cbItemSelectAll').click()
            driver.find_element(By.CSS_SELECTOR, 'div#miRemove').click()
            wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'span.yui-button:nth-child(1)'))).click()
            try:
                WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div#divEmptyStateScreenContainer')))
                print('All downloads completed!')
                break
            except TimeoutException:
                print('Timeout')
                driver.refresh()
        print(f"Status (Successes:{successes}, Errors:{errors})")
        time.sleep(3)
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

        return list(combined_df[combined_df['checklist'] == False]['product_id'])

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
                    except TimeoutException as e:
                        print(f"Retrying due to error {e}")
                        time.sleep(retry_delay)
                    continue
                else:
                    try:
                        print(f"Adding item {id}...({i} of {len(free_ids)})")
                        self.toDownloadPage(id, cookies=cookies)
                        break
                    except TimeoutException as e:
                        print(f"Retrying due to error {e}")
                        time.sleep(retry_delay)

if __name__ == '__main__':
    d = Download_link()
    d.main()
