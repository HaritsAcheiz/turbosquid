from setuptools import setup, find_packages

# # Read the requirements.txt file
# with open('requirements.txt', 'r', encoding='utf-8-sig') as file:
#     requirements = [line.strip() for line in file if line.strip()]
# print(requirements)

setup(
    name='turbosquid',
    version='1.0',
    packages=find_packages(),
    install_requires=['aiohttp==3.8.4',
                      'requests==2.30.0',
                      'selectolax==0.3.13'],
    entry_points={
        'console_scripts': [
            'turbosquid-scraper = turbosquid.scraper:main',
        ],
    },
    author='Harits',
    author_email='harits.muhammad.only@gmail.com',
    description='A script for scraping data from TurboSquid website',
    url='https://github.com/HaritsAcheiz/turbosquid',
)
