#!/usr/bin/env python3

try:
    import bs4
    from bs4 import BeautifulSoup
except ImportError:
    import BeautifulSoup
    from BeautifulSoup import BeautifulSoup 
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import json
import sys

EXE = os.getcwd() + '/path'
URL = 'https://support.microsoft.com/ru-ru/help/977519/description-of-security-events-in-windows-7-and-in-windows-server-2008'
FILENAME = 'a.html'
REMOTE_EXEC = 'http://test-polygon-bus.etecs.ru:4444/wd/hub'

CONT_SELECTOR = 'div[class="table-responsive"] table[class="sbody-table table"]'
ITEM_SELECTOR = 'tr[class="sbody-tr"]'
PART_SELECTOR = 'td[class="sbody-td"]'
CATH_SELECTOR = 'h3[class="sbody-h3"]'
SUBCATH_SELECTOR = 'h4[class="sbody-h4"]'
CATH_AND_SUBCATH = {'h3' : 'sbody-h4', 'h4': 'sbody-h3'}


def getcontent(tag):
    if len(tag.contents):
        return tag.contents[0]
    return ""

def check_tags(tag):
    if len(tag.select(PART_SELECTOR)):
        return True
    return False


class Item:
    def __init__(self, parser):
        parts = parser.select(PART_SELECTOR)
        self.__value = str(getcontent(parts[0]))
        self.__meaning = str(getcontent(parts[1]))

    def to_json(self):
        return {
            "EventCode": self.__value,
            "Description": self.__meaning 
        }


class ItemContainer:
    def __init__(self, parser, sub_cath = "default"):
        items = parser.select(ITEM_SELECTOR)
        self.__items = [Item(i) for i in filter(check_tags ,items)]
        self.__sub_cath = sub_cath

    def set_sub_cath(self, sub_cath):
        self.__sub_cath = sub_cath

    def to_json(self):
        return {
            "Title": self.__sub_cath,
            "Items": [i.to_json() for i in self.__items]
        }
    

class Cathegory:
    def __init__(self, cath = 'default'):
        self.__cath = cath 
        self.__containers = list()

    def append(self, cont):
        self.__containers.append(cont)

    def set_cath(cath):
        self.__cath = cath 
    
    def to_json(self):
        return {
            "Title": self.__cath,
            "Items": [c.to_json() for c in self.__containers]
        }


class Descriptions:
    def __init__(self, parser):
        containers = parser.select(CONT_SELECTOR)
        sub_caths = parser.select(SUBCATH_SELECTOR)
        
        conts = [ItemContainer(c) for c in containers]
        
        self.__caths = list()
        
        iterator = iter(conts)
        for head in parser.find_all(CATH_AND_SUBCATH):    
            head_name = getcontent(head).split(':')
            head = head.get('class')[0]

            if len(head_name) == 1:
                return

            if head == 'sbody-h3':
                self.__caths.append(Cathegory(head_name[1]))
            if head == 'sbody-h4':
                cont = next(iterator)
                cont.set_sub_cath(head_name)
                self.__caths[-1].append(cont)

        next(iterator)

    def to_json(self):
        return json.dumps({
            "data": [cath.to_json() for cath in self.__caths]
        })

def main():
        
   # driver = webdriver.Remote(
   #         desired_capabilities=DesiredCapabilities.CHROME,
   #         command_executor = remote_executor
   # )
   # driver.get(url)
   # page = driver.source_page

   # print(page)
   # driver.quit()

   #try:
    options = Options()
    options.set_headless(headless=True)
    driver = webdriver.Firefox(EXE, firefox_options=options)
    driver.get(URL)

    html = driver.page_source
    res = driver.execute_script("return microsoft.support.prefetchedArticle")

    html = res['ru-ru/977519']['details']['body'][1]['content'][0]
    #html = res['en-us/977519']['details']['body'][1]['content'][0]

    soup = BeautifulSoup(html, 'html.parser')
    des = Descriptions(soup)

    f = open('a.json', 'wt')
    f.write(des.to_json())
    f.close()
    #except:
    #    print(sys.exc_info()[0])
    #finally:
    #    driver.quit()

if __name__ == '__main__':
    main()
