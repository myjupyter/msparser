#!/usr/bin/env python3

import os
import json
import sys

try:
    import bs4
    from bs4 import BeautifulSoup
except ImportError:
    import BeautifulSoup
    from BeautifulSoup import BeautifulSoup 

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import tools.tools as tls

EXE = os.getcwd() + '/path'
URL = 'https://support.microsoft.com/ru-ru/help/977519/description-of-security-events-in-windows-7-and-in-windows-server-2008'
FUNC_NAME = 'microsoft.support.prefetchedArticle'

def main():
    options = Options()
    options.set_headless(headless=True)
    driver = webdriver.Firefox(EXE, firefox_options=options)
    driver.get(URL)

    html = driver.page_source
    res = driver.execute_script('return ' + FUNC_NAME)
    driver.quit()
    
    html = res['ru-ru/977519']['details']['body'][1]['content'][0]
    #html = res['en-us/977519']['details']['body'][1]['content'][0]

    soup = BeautifulSoup(html, 'html.parser')
    des = tls.Descriptions(soup)

    f = open('a.json', 'wt')
    f.write(des.to_json())
    f.close()

if __name__ == '__main__':
    main()
