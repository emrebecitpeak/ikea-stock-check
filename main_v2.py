import requests as re
import os

import pandas as pd
import json
import io
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_stock_info(prod_codes):
    
    url_list = prod_codes
    
    
    df_all = pd.DataFrame([], columns=['url', 'para', 'location', 'stock_info'])

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


        xpath = '//*[@id="aspnetForm"]/div[7]/div/div[1]/div[1]/div[2]/div/a'
        element = driver.find_element(by=By.XPATH, value=xpath)
        element.click()

        html = driver.page_source
        soup = BeautifulSoup(html)
        
        para = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_divPrice'}).text.strip()

        div = soup.find('div', {'id': 'check-stock-modal'}).find_all('div', {'class': 'stock-card'})

        names = [i.find('h3').text for i in div]

        stock_info = [i.find('strong').text for i in div]        
        i=0
        while len(names)==0:
            i+=1
            if i>15:
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=get_options())
                driver.get(url)
                xpath = '//*[@id="aspnetForm"]/div[7]/div/div[1]/div[1]/div[2]/div/a'
                element = driver.find_element(by=By.XPATH, value=xpath)
                element.click()
                i=0
            print('looking again')
        
            html = driver.page_source
            soup = BeautifulSoup(html)

            div = soup.find('div', {'id': 'check-stock-modal'}).find_all('div', {'class': 'stock-card'})

            names = [i.find('h3').text for i in div]

            stock_info = [i.find('strong').text for i in div]        




        df = pd.DataFrame(list(zip(names, stock_info)), columns=['location', 'stock_info'])

        df['url'] = url
        df['para'] = para

        df_all = df_all.append(df)
    
    return df_all.pivot(index=['url', 'para'], columns='location', values='stock_info')[['IKEA BAYRAMPAŞA', 'IKEA ÜMRANİYE', 'IKEA KARTAL', 'İNTERNET MAĞAZASI']]


urls = ['https://www.ikea.com.tr/urun/pax-beyaz-100x58x236-cm-gardirop-iskeleti-50214560',
         'https://www.ikea.com.tr/urun/komplement-beyaz-100x58-cm-dolap-ici-separator-00246417',
         'https://www.ikea.com.tr/urun/komplement-beyaz-58-cm-sepet-rayi-30263245',
         'https://www.ikea.com.tr/urun/komplement-beyaz-50x58-cm-tel-sepet-10257306',
         'https://www.ikea.com.tr/urun/komplement-beyaz-50x58-cm-cekmece-10246308',
         'https://www.ikea.com.tr/urun/komplement-beyaz-50x58-cm-surgulu-pantolon-askisi-30446537',
         'https://www.ikea.com.tr/urun/komplement-gri-frenli-mentese-30214504',
         'https://www.ikea.com.tr/urun/bergsbo-beyaz-50x229-cm-gardirop-kapagi-30160407',
         'https://www.ikea.com.tr/urun/bagganas-siyah-143-mm-kulp-80338413',
         'https://www.ikea.com.tr/urun/komplement-beyaz-100x58-cm-raf-70277957',
         'https://www.ikea.com.tr/urun/oversidan-koyu-gri-96-cm-led-li-aydinlatma-seridi-00474904',
         'https://www.ikea.com.tr/urun/komplement-beyaz-100-cm-aski-borusu-30256891',
         'https://www.ikea.com.tr/urun/komplement-beyaz-75-100x58-cm-dolap-ici-separator-60246396',
         'https://www.ikea.com.tr/urun/komplement-beyaz-50x58-cm-raf-30277959',
         'https://www.ikea.com.tr/urun/fornimma-beyaz-3-5-m-baglanti-kablosu-50446881',
         'https://www.ikea.com.tr/urun/silverglans-beyaz-30-w-kablosuz-kontrol-surucusu-10474772',
         'https://www.ikea.com.tr/urun/malm-beyaz-160x200-cm-cift-kisilik-baza-20404806',
         'https://www.ikea.com.tr/urun/hemnes-beyaz-vernik-160x95-cm-8-cekmeceli-sifonyer-10239280',
         'https://www.ikea.com.tr/urun/hemnes-beyaz-vernik-46x35x70-cm-komodin-20200456',

        ]


df_all = get_stock_info(urls)


df_all = df_all[['IKEA BAYRAMPAŞA', 'IKEA ÜMRANİYE', 'IKEA KARTAL', 'İNTERNET MAĞAZASI']]





import dataframe_image as dfi

dfi.export(df_all, 'dataframe.png')


img = open("dataframe.png", 'rb').read()
# Authenticate to the Slack API via the generated token
client = WebClient(os.environ['SLACK_API_TOKEN'])
# Send the image
client.files_upload(
       channels = "emre-slack-api-2",
       filename = "Apollo 11",
       content = img)

client.chat_postMessage(
        channel="emre-slack-api-2",
        text='\n'.join(urls)
    )
