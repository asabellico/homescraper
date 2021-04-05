import pathlib
from selenium import webdriver
import urllib
from urllib.request import urlopen

from homescraper.exceptions import PageNotFound

driver = None

def get_http_url(url: str, use_selenium: bool = False):
    # check url existence before running selenim
    try:
        resp = urlopen(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise PageNotFound(f'URL {url} does not exist')

    if use_selenium:
        global driver
        if driver is None:
            # init selenium webdriver
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
            options.add_argument('headless')
            options.add_argument('window-size=0x0')
            web_driver_path = pathlib.Path(__file__).parent.absolute() / '..' / '..' / 'resources' / 'chromedriver.exe'
            driver = webdriver.Chrome(executable_path=str(web_driver_path), chrome_options=options)

        # driver.manage().deleteAllCookies()
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        resp_content = driver.page_source

        return resp_content
    else:
        return  resp.read()