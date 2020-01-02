from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
import json
import datetime
import sys
import os
import re


class Etf_scrape:
    """
    Blueprint to define how each issuers website is scraped.
    - Initial scope is to scrape 80% of assets from Issuers websites
    - Made Possible as ETFs require this transparency to be publicly available
    - Subsequently will look at other use cases
    - Make note - do all websites require selenium or can html suffice?
    - The only manual maitenance should be a list of all issuer websites - but maybe even this can be sourced?
    """

    def __init__(self, debug=True):

        # Initiate default options for the instance
        chrome_options = Options()

        # Used to toggle GUI Browser interface
        self.debug = debug
        if self.debug == False:
            chrome_options.add_argument('--headless')    # When debugging is off - no GUI needed
        else: print('Debugging Mode ON')

        # setting download preferences
        prefs = {'download.prompt_for_download': False,
         'download.directory_upgrade': True,
         'safebrowsing.enabled': False,
         'safebrowsing.disable_download_protection': True,
        'download.default_directory': os.getcwd() + '\data\\'}
        chrome_options.add_experimental_option('prefs', prefs)


        # Selecting driver based on OS
        if sys.platform == 'win32':
            self.browser_path = 'drivers/chromedriver_win.exe'
        elif sys.platform == 'darwin':
            self.browser_path = 'drivers/chromedriver_mac'

        # Initiating the web driver
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=self.browser_path)

        # Used to define the correct cookies for the session
        with open('web_cookies.txt', 'r') as fp:
            self.cookies = json.load(fp)

        # navigate to start page
        self.driver.get('https://www.google.co.uk/')

        # add cookies to the session
        for cooki in self.cookies:
            self.driver.add_cookie(cooki)

        # importing the mappings for each website
        self.mappings = pd.read_excel('data/datapoint_mapping.xlsx')


    def pBDP(self, isin=None, datapoint=None,FX=None):
        '''
        Python Data Point alternative to BDP.
        Simply a selector for the various BDP implementations of each site
        '''
        pass


    def update_isins(self, many=True):
        '''
        Fetching a current list of ISIN's from all issuers websites
        Yet to be implemented; many worth collecting all data from these files directly?
        '''
        pass


    def pBDH(self, isin=None, datapoint=None, start_date=None, end_date=None, FX=None):
        '''
        Python Historical Data Point alternative to BDH
        Designed to behave similarly
        - Handling an array of ISINs and datapoints (?)
        '''
        pass


    def jpmBDP(self, isins=None, datapoints=None):
        '''
        method returning a single datapoint on a single jpm isin
        Being built out at present to explore exactly how this class should be structured
        '''
        # defining the scraping website
        website = 'https://am.jpmorgan.com/'
        # convert single queries to lists so works w/ vectorisation
        if isinstance(isins,str):
            isins = [isins]
        if isinstance(datapoints,str):
            datapoints = [datapoints]

        old_len = len(datapoints)
        old_name = datapoints[0].lower()
        # fetching all variables if asked for
        if datapoints[0].lower() == 'all':
            datapoints = self.mappings.loc[self.mappings['website'] == website,'alias']
        else:
            datapoints = self.mappings.loc[(self.mappings['Datapoint'].isin(datapoints)) & (self.mappings['website'] == website), 'alias']

        # Warning if a datapoint mapping wasn't found
        # TODO: currently doesn't work
        if (len(datapoints) != old_len) & (old_name != 'all'):
            print('WARNING: one or more datapoints not mapped to "data-test-id" on specified site')

        # a list of all possible columns for lopping later
        #column_list = self.mappings['Datapoint'].unique().tolist()

        # creating the blank dataframe
        df = pd.DataFrame(columns = ['ISIN', 'DATAPOINT', 'VALUE'])
        df.loc[0] = None

        # wait maximum 15 seconds to locate an element
        #self.driver.implicitly_wait(5)

        # fetching the JPM website
        self.driver.get(website)



        wait = WebDriverWait(self.driver, 2)

        # loop through all requested ISINs for all requested datapoints
        for isin in isins:
            search = self.driver.find_element_by_id('searchbox')
            search.send_keys(isin)
            time.sleep(1)
            search.send_keys(Keys.RETURN)
            time.sleep(2)
            tries = 0
            loaded = []
            while (len(loaded) < 1) & (tries <= 20):
                try:
                    loaded = driver.find_elements_by_id(id_ = 'searchbox')
                    time.sleep(0.5)
                    tries = tries + 1
                except:
                    tries = tries + 1


            for datapoint in datapoints:
                if datapoint == 'title':
                    dp = self.driver.title.replace(' - J.P. Morgan Asset Management', '')
                    df.loc[max(df.index) + 1] = [isin, datapoint, dp]

                elif datapoint == 'shareclass_dist_status':
                    dp = self.driver.title
                    dp = re.findall('(acc|dist)', dp)
                    dp = dp[0]
                    df.loc[max(df.index) + 1] = [isin, datapoint, dp]

                else:
                    try:
                        dp = self.driver.find_element_by_css_selector('[data-testid=' + datapoint + ']')
                        dp = dp.get_attribute('innerHTML')
                        soup = BeautifulSoup(dp, features='lxml')
                        dp = soup.get_text()
                        df.loc[max(df.index) + 1] = [isin, datapoint, dp]
                    except:
                        # add a not found row if not found
                        df.loc[max(df.index) + 1] = [isin, datapoint, 'not found']
            time.sleep(0.5)


        df.drop(df.index[0], inplace=True)

        # Data cleansing step
        df = df.merge(self.mappings, left_on = 'DATAPOINT', right_on = 'alias', how='left')
        df = df.loc[:, ['ISIN', 'Datapoint', 'VALUE']]
        df.rename(columns = {'Datapoint':'DATAPOINT'}, inplace=True)
        df = df.drop_duplicates()
        df = df.pivot(index = 'ISIN', columns = 'DATAPOINT',values = 'VALUE')
        df.replace('not found', np.nan, inplace=True)
        #for col in column_list:
        #    if col not in df.columns:
        #        df[col] = np.nan
        if 'fund_aum_currency' in df.columns: df['fund_aum_currency'] = df['fund_aum_currency'].str.slice(stop = 3)
        if 'fund_aum' in df.columns: df['fund_aum'] = df['fund_aum'].str.slice(start = 4, stop = -3).astype('float64') * 1000000
        if 'fund_aum_asof' in df.columns: df['fund_aum_asof']  = df['fund_aum_asof'].str.replace('As of ', '').astype('datetime64')
        if 'shareclass_nav_currency' in df.columns: df['shareclass_nav_currency'] = df['shareclass_nav_currency'].str.slice(stop = 3)
        if 'shareclass_nav' in df.columns: df['shareclass_nav'] = df['shareclass_nav'].str.slice(start = 4).astype('float64')
        if 'shareclass_nav_asof' in df.columns: df['shareclass_nav_asof']  = df['shareclass_nav_asof'].str.replace('As of ', '').astype('datetime64')
        if 'shareclass_inception_date' in df.columns: df['shareclass_inception_date'] = df['shareclass_inception_date'].astype('datetime64')
        if 'fund_number_of_holdings' in df.columns: df['fund_number_of_holdings'] = df['fund_number_of_holdings'].astype('float64')
        if 'shareclass_shares_outstanding_asof' in df.columns: df['shareclass_shares_outstanding_asof'] = df['shareclass_shares_outstanding_asof'].str.replace('As of ', '').astype('datetime64')
        if 'shareclass_shares_outstanding' in df.columns: df['shareclass_shares_outstanding'] = df['shareclass_shares_outstanding'].str.replace(',','').astype('float64')
        if 'shareclass_total_expense_ratio' in df.columns: df['shareclass_total_expense_ratio'] = df['shareclass_total_expense_ratio'].str.replace('%','').astype('float64') * 100
        if 'yield_to_maturity' in df.columns: df['yield_to_maturity'] = df['yield_to_maturity'].str.replace('%','').astype('float64')
        if 'yield_to_maturity_asof' in df.columns: df['yield_to_maturity_asof']  = df['yield_to_maturity_asof'].str.replace('As of ', '').astype('datetime64')
        if old_name.lower() == 'all': df['shareclass_assets_base'] = df['shareclass_shares_outstanding'] * df['shareclass_nav']
        df.dropna(axis = 1, how = 'all', inplace=True)
        df['SOURCE'] = website
        df['SOURCE_DATE'] = datetime.date.today()
        return(df)



    def jpmPORT(self, isins=None):
        #ie00bf4g6y48
        # enable vectorisation
        if isinstance(isins,str):
            isins = [isins]

        isins = [x.lower() for x in isins]

        # component parts of URL for isin to be inserted into
        start_url = 'https://am.jpmorgan.com/FundsMarketingHandler/excel?type=dailyETFHoldings&cusip='
        end_url = '&country=gb&role=adv&locale=en-GB'

        df = pd.DataFrame(columns = ['Name', 'ISIN', 'Asset class', 'Country', 'Currency', 'Weight', 'Base market\nvalue', 'Price'])

        # loop through and download holdings for each ISIN
        for isin in isins:
            path = start_url + isin + end_url
            temp_df = pd.read_excel(path, skipfooter=9)
            asofdate = temp_df.iloc[4, 7]
            headers = temp_df.iloc[6,]
            temp_df = temp_df.iloc[7:,]
            temp_df.columns = headers
            temp_df.reset_index(drop=True)
            df = df.append(temp_df, ignore_index=True, sort=False)
            df['asof'] = asofdate.replace('As of Date:', '')
            df['asof'] = df['asof'].astype('datetime64')
            df['etf_isin'] = isin
        return df


    def get_jpmISIN(self):
        """
        method to update the list of currently available isins for JPMETFs
        """
        path1 = os.path.join('data','Export.xls')
        if 'Export.xls' in os.listdir('data'):
            os.remove(path1)

        path2 = os.path.join('data','Export.xlm')
        if 'Export.xlm' in os.listdir('data'):
            os.remove(path2)


        self.driver.get('http://www.jpmorganassetmanagement.ie/en/showpage.aspx?pageID=18')
        self.driver.find_element_by_css_selector('[value="Export to Excel"]').click()
        self.driver.find_element_by_css_selector('[value="Download"]').click()

        time.sleep(10)

        # convert the file to xlm from xls
        os.rename(path1, path2)

        with open(path2) as fp:
            t = fp.read()

        isins = re.findall(r'[A-Z]{2}[A-Z0-9]{9}[0-9]{1}',t)

        jpm_isins = isins

        # waiting for download to complete
        #jpm_isins = pd.DataFrame()
        #TODO: TIME AWARE
        #for _ in range(20):
        #    if jpm_isins.size == 0:
        #        try:
        #            jpm_isins = pd.read_excel(path)
        #        except:
        #            pass
        #        time.sleep(0.5)
        #    else:
        #        break
        return jpm_isins




## testing
if __name__ == '__main__':
    etf = Etf_scrape(debug=False)
    #df = etf.jpmBDP(isins= ['IE00BD9MMF62','IE00BJK9H753'], datapoints= ['fund_aum', 'yield_to_maturity', 'isin'])
    #df = etf.jpmBDP(isins= ['IE00BD9MMF62','IE00BJK9H753'], datapoints= 'all')
    #print(df.shape)

    df = etf.jpmBDP(isins='IE00BD9MMF62', datapoints = 'shareclass_dist_status')
    print(df)
