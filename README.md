# turbosquid
Steps by step to install and run the script from the "turbosquid" repository:

1. Download the repository: In a web browser, navigate to the repository's page on GitHub (https://github.com/HaritsAcheiz/turbosquid). Click on the green "Code" button and select "Download ZIP" to download the repository as a ZIP file.

2. Extract the ZIP file: Once the ZIP file is downloaded, you should extract its contents to a desired location on your computer.

3. Open a command line interface: open a command line interface or terminal on your computer.

4. Check Python installation: You should ensure that Python is installed on your computer and added to the system's path. You can do this by running the following command:
   ```
   python --version
   ```

   If Python is installed correctly, the command will display the installed Python version. If Python is not found or an error is displayed, you should install Python from the official Python website (https://www.python.org) and make sure to select the option to add Python to the system's PATH during the installation process.

5. Change directory: You need to navigate to the directory where they extracted the repository's contents using the `cd` command. For example:
   ```
   cd path/to/turbosquid
   ```

6. Create a virtual environment (optional): It's recommended to create a virtual environment to isolate the dependencies. You can create one by running the following command:
   ```
   python -m venv env
   ```

7. Activate the virtual environment (optional): You should activate the virtual environment by running the appropriate command based on your operating system:
   - For Windows:
     ```
     .\env\Scripts\activate
     ```
   - For Linux/Mac:
     ```
     source env/bin/activate
     ```

8. Install dependencies: Install the required dependencies using the following command:
   ```
   pip install -r requirements.txt
   ```

9. Run the script: You can run the script by executing the `scraper.py` file with Python:
   ```
   python scraper.py
   ```

That's it! The script should now be running and performing the scraping task. Ensure that You has provided the necessary configurations or inputs as required by the script.

Note: If You encounters any errors during the installation or execution of the script, make sure you have followed all the steps correctly, Python is installed properly, and your environment is set up correctly.
