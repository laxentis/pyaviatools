#! /usr/bin/python

import re
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest
import time

class Metar:
    """Class for reading METARs in EPWW FIR"""

    def __init__(self):
        self.airfields = {}
        self.refresh()
    
    def refresh(self):
        self.res = []
        self.__getGG30()
        self.__getMIL()
        self.__makeDict()

    def __getitem__(self, icao):
        return self.airfields[icao]

    def __getGG30(self):
        self.__parseIMGW('http://awiacja.imgw.pl/index.php?product=metar30m')

    def __getMIL(self):
        self.__parseIMGW('http://awiacja.imgw.pl/index.php?product=metar_mil')

    def __parseIMGW(self, url):
        r = urllib.request.urlopen(url)
        html = r.read()
        soup = BeautifulSoup(html)
        doc = soup.find_all('div', {'class':'forecast'})[0].find_all('tr')
        for line in doc:
            self.res.append(line.get_text())

    def __makeDict(self):
        p = re.compile('(METAR (EP[A-Z][A-Z]) .*=)')
        for line in self.res:
            r = p.match(line)
            self.airfields[r.groups()[1]] = r.groups()[0]

class Taf:
    """Class for reading TAFs in EPWW FIR"""

    def __init__(self):
        self.airfields = {}
        self.refresh()

    def refresh(self):
        self.res = []
        self.__getFC()
        self.__getFT()
        self.__getMIL()
        self.__makeDict()

    def __getitem__(self, icao):
        return self.airfields[icao]

    def __getMIL(self):
        self.__parseIMGW('http://awiacja.imgw.pl/index.php?product=taf_mil')

    def __getFC(self):
        self.__parseIMGW('http://awiacja.imgw.pl/index.php?product=taffc')

    def __getFT(self):
        self.__parseIMGW('http://awiacja.imgw.pl/index.php?product=tafft')

    def __parseIMGW(self, url):
        r = urllib.request.urlopen(url)
        html = r.read()
        soup = BeautifulSoup(html)
        doc = soup.find_all('div', {'class':'forecast'})[0]
        doc = doc.get_text().split('=')
        for line in doc:
            self.res.append(line)

    def __makeDict(self):
        p = re.compile('(TAF (EP[A-Z][A-Z]) .*)')
        for line in self.res:
            r = p.match(line)
            if r:
                self.airfields[r.groups()[1]] = r.groups()[0]
class Gamet:
    """Class for reading GAMETs in EPWW FIR"""

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(30)
        self.data = {}
        self.driver.get("http://awiacja.imgw.pl/index.php?product=gamet")
        self.__getSectors()
        self.driver.quit()
        self.__clearData()

    def __getitem__(self, area):
        return self.data[area]

    def print(self, area):
        for line in self.data[area]:
            print(line)

    def __getSectors(self):
        for i in range(1,6):
            self.__getSector(i)
        
    def __getSector(self, sector):
        self.driver.find_element_by_css_selector("area[alt=\"0"+str(sector)+"\"]").click()
        self.element = self.driver.find_element(by=By.ID, value="prdata")
        self.data["A"+str(sector)] = self.element.text.split('\n')

    def __clearData(self):
        for g in self.data.values():
            del g[0]

