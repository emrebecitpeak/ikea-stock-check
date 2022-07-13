import requests as re
import os

xml = re.request(url='https://cdn.ikea.com.tr/sitemap/sitemap.xml', method='GET')

from bs4 import BeautifulSoup

bs = BeautifulSoup(xml.content)

links = [i.text for i in bs.find_all('loc')][1:]

prod_links = []
for url in links:
    xml_inner = re.request(url=url, method='GET')  
    if xml_inner.status_code != 200:
        print('Error', url)
    
    bs = BeautifulSoup(xml_inner.content)
    temp_links = [i.text for i in bs.find_all('loc')]
    prod_links.append(temp_links)

flattened = [val for sublist in prod_links for val in sublist]

prod_codes = [link.split('/')[-2] for link in flattened]

prod_desc = [link.split('/')[-2:] for link in flattened]
prod_desc = [' // '.join(i).rstrip('.aspx') for i in prod_desc]

import pandas as pd

df_codes = pd.DataFrame(list(zip(prod_codes, flattened, prod_desc)), columns=['prod_code', 'url', 'prod_desc'])



def get_stock_info(prod_codes, df_codes):
    
    url_list = df_codes[df_codes['prod_code'].isin(prod_codes)]['url'].values
    
    
    df_all = pd.DataFrame([], columns=['url', 'location', 'stock_info'])

    for url in url_list:

        from bs4 import BeautifulSoup
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By

        def get_options():
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--headless")
            return chrome_options


        driver = webdriver.Chrome(ChromeDriverManager().install(), options=get_options())
        driver.get(url)


        xpath = '//*[@id="ctl00_ContentPlaceHolder1_liTabInfoStockStatus"]/a'
        element = driver.find_element(by=By.XPATH, value=xpath)
        element.click()

        html = driver.page_source
        soup = BeautifulSoup(html)

        div = soup.find("div", {'class', 'product-info'}).find('div', {'id': 'tab-stock-status'}).find('div', {'class': 'control-result'})

        names = [i.text for i in div.find_all('h4')]

        stock_info = [i.find('span').text for i in div.find_all('div', {'class': 'stock-info-container'})]
        
        i=0
        while len(names)==0:
            i+=1
            if i>15:
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=get_options())
                driver.get(url)
                xpath = '//*[@id="ctl00_ContentPlaceHolder1_liTabInfoStockStatus"]/a'
                element = driver.find_element(by=By.XPATH, value=xpath)
                element.click()
                i=0
            print('looking again')
        
            html = driver.page_source
            soup = BeautifulSoup(html)

            div = soup.find("div", {'class', 'product-info'}).find('div', {'id': 'tab-stock-status'}).find('div', {'class': 'control-result'})

            names = [i.text for i in div.find_all('h4')]

            stock_info = [i.find('span').text for i in div.find_all('div', {'class': 'stock-info-container'})]




        df = pd.DataFrame(list(zip(names, stock_info)), columns=['location', 'stock_info'])

        df['url'] = df_codes[df_codes['url'] == url].prod_desc.values[0]

        df_all = df_all.append(df)
    
    return df_all.pivot(index='url', columns='location', values='stock_info')[['IKEA BAYRAMPAŞA', 'IKEA ÜMRANİYE', 'IKEA KARTAL', 'İNTERNET MAĞAZASI']]



df_all = get_stock_info(['80261258',
                         '60295532'], df_codes)


df_all = df_all[['IKEA BAYRAMPAŞA', 'IKEA ÜMRANİYE', 'IKEA KARTAL', 'İNTERNET MAĞAZASI']]



import pandas as pd
import json
import io
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import dataframe_image as dfi

dfi.export(df_all, 'dataframe.png')


img = open("dataframe.png", 'rb').read()
# Authenticate to the Slack API via the generated token
# client = WebClient(os.environ['SLACK_API_TOKEN'])
# Send the image
# client.files_upload(
        channels = "emre-slack-api-2",
        filename = "Apollo 11",
        content = img)
