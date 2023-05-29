# Turbosquid
Steps by step to install and run the script from the "turbosquid" repository:

1. Download the repository:
   - Go to the turbosquid repository on GitHub: https://github.com/HaritsAcheiz/turbosquid
   - Click on the green "Code" button and select "Download ZIP".
   - Save the ZIP file to a location on the client's computer.

2. Extract the downloaded ZIP file:
   - Locate the downloaded ZIP file on the client's computer.
   - Right-click on the file and select "Extract All" or use a file extraction utility of their choice.
   - Choose a destination folder to extract the contents of the ZIP file.

3. Contact the developer:
   - Reach out to the developer of the turbosquid Python application to obtain the `creds.py` file.
   - Send a message or email explaining that you would like to use the application and request the `creds.py` file containing the necessary credentials.
   - The developer will provide you with the `creds.py` file or guide you on how to generate the required credentials.

4. Place the `creds.py` file in the repository directory:
   - Once you have the `creds.py` file, copy it to the directory where you extracted the turbosquid repository files.

5. Install the required dependencies:
   - Open a terminal or command prompt.
   - Change to the extracted repository directory using the `cd` command. For example:
     ```
     cd path/to/turbosquid
     ```
   - Run the following command to install the required dependencies using pip:
     ```
     pip install -r requirements.txt
     ```

6. Run the `async_scraper.py` script:
   - In the terminal or command prompt, navigate to the turbosquid directory if not already there.
   - Run the following command to execute the `async_scraper.py` script:
     ```
     python async_scraper.py
     ```
   - The script will prompt the client to enter the item they want to search for on TurboSquid.
   - The script will collect the item IDs and store them in a file named `ids/<keyword>_result.csv`.

7. Open the CSV file:
   - Locate the `ids/<keyword>_result.csv` file in the turbosquid directory.
   - Open the CSV file using a spreadsheet program such as Microsoft Excel or Google Sheets.

8. Filter the IDs to be downloaded:
   - Use the filtering capabilities of the spreadsheet program to filter the item IDs based on specific criteria (e.g., certain price range, specific formats, etc.).
   - Apply the desired filters to the appropriate column(s) in the spreadsheet to narrow down the list of item IDs that need to be downloaded.
   - Once the filtering is complete, save the modified CSV file.

9. Run the `downloader.py` script:
   - In the terminal or command prompt, navigate to the turbosquid directory if not already there.
   - Run the following command to execute the `downloader.py` script:
     ```
     python downloader.py
     ```
   - The script will read the item IDs from the modified CSV file.
   - It will download the 3D model files associated with each item ID and store them in folders named with the item title and product ID under the `results` directory.

10. Wait for the download process to complete:
   - The script will display the progress of the downloads in the terminal.
   - Once the download process is finished, the 3D model files will be available in the respective folders under the `results` directory.
