import requests
import urllib
import pandas as pd
import os
from pathlib import Path

def get_fx(quoted, dates, base='USD', main_api ='http://data.fixer.io/api/', key=None):

    '''
    Returns historical FX rates from the fixer.io api for given currencies on a specified date

    Parameters
    ----------
    quoted : string or list
        the currency or currencies to return a rate for.
        Specified with 3 letter currency codes (i.e. "GBP")

    dates: string or list
        the date or dates to return the rate for.
        Specified in "YYY-MM-DD" format

    base: string
        the currency used to compare the quoted currencies too
        Specified with 3 letter currency codes

    Returns
    -------
    pandas.DataFrame containing exchange rates for each specified date & currency
    '''
    try:
        # Read in API access key when script or import
        path = Path(__file__).absolute().parent.parent.joinpath('data', 'access_key.txt')
        f = open(path)
        key = f.read()
        
    except FileNotFoundError as err:
        print(Path(__file__).absolute())
        raise FileNotFoundError('Please sign-up for fixer.io and create file w/APIkey in "data/access_key.txt"') from err
    except Exception:
        raise
    else:
        f.close()


    # converting parameters to list if string
    if isinstance(quoted, str):
        quoted = [quoted]

    if isinstance(dates, str):
        dates = [dates]

    if base not in quoted:
        # ensure base currency is included in fetch, important to get around free api restriction
        quoted.append(base)

    quoted = ','.join(quoted) # convert to comma seperated values for api parameter

    # set parameters for api call
    params = {'access_key': key,
              'base': 'EUR',
              'symbols': quoted}

    params = urllib.parse.urlencode(params)

    new_rates_df = pd.DataFrame() # empty DF object

    # loop through each date and call api
    for date in dates:
        url = main_api + date + '?' + params
        fx = requests.get(url).json()
        rates = fx['rates'] #TODO: check for success code
        r_base = 1 / rates[base] # getting around free api restriction of EUR only base
        new_rates = {}

        for k, v in rates.items():
        # dictionary with values relative to specified base
            new_rates[k] = v * r_base

        # converting each dictionary to a dataframe and appending
        date_df = pd.DataFrame({'currency': list(new_rates.keys()), 'rate': list(new_rates.values()), 'date': date})
        new_rates_df = new_rates_df.append(date_df)
        new_rates_df['date'] = new_rates_df['date'].astype(pd.np.datetime64)

    return new_rates_df


if __name__ == '__main__':
    print(get_fx('EUR', '2019-12-30'))