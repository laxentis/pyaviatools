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

    def get(self, icao):
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

    def get(self, icao):
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
        self.__getA1()
        self.__getA2()
        self.__getA3()
        self.__getA4()
        self.driver.quit()
        self.__clearData()

    def get(self, area):
        return self.data[area]

    def __getA1(self):
        self.driver.find_element_by_css_selector("area[alt=\"01\"]").click()
        self.element = self.driver.find_element(by=By.ID, value="prdata")
        self.data["A1"] = self.element.text.split('\n')

    def __getA2(self):
        self.driver.find_element_by_css_selector("area[alt=\"02\"]").click()
        self.element = self.driver.find_element(by=By.ID, value="prdata")
        self.data["A2"] = self.element.text.split('\n')

    def __getA3(self):
        self.driver.find_element_by_css_selector("area[alt=\"03\"]").click()
        self.element = self.driver.find_element(by=By.ID, value="prdata")
        self.data["A3"] = self.element.text.split('\n')

    def __getA4(self):
        self.driver.find_element_by_css_selector("area[alt=\"04\"]").click()
        self.element = self.driver.find_element(by=By.ID, value="prdata")
        self.data["A4"] = self.element.text.split('\n')

    def __clearData(self):
        for g in self.data.values():
            del g[0]
