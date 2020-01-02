import requests
import urllib
import pandas as pd


def get_fx(quoted, dates, base='USD', main_api ='http://data.fixer.io/api/', key='c263b908a641e8146deac4b2eeb27c17'):
    # convert to list of not
    if isinstance(quoted, str):
        quoted = [quoted]
    
    if isinstance(dates, str):
        dates = [dates]
   #old_quoted = tuple(quoted.copy())[0]
    
    
    if base not in quoted:
        quoted.append(base)
    
        
    # comma seperate the currencies
    quoted = ','.join(quoted)
    
    # set parameters
    params = {'access_key': key,
              'base': 'EUR',
              'symbols': quoted}
    
    params = urllib.parse.urlencode(params)
    
    new_rates_df = pd.DataFrame()
    
    for date in dates:
        # constructing the URL
        url = main_api + date + '?' + params
        
        # request
        fx = requests.get(url).json()
        
        #creating object with just the output
        #TODO: check for success
        rates = fx['rates']
        
        # Working back to the base exchange rate to get around free trial limitation of base == EUR only
        r_base = 1 / rates[base]
        
        new_rates = {}
        
        # creating new dictionary with rates vs chosen base
        for k, v in rates.items():
            
            new_rates[k] = v * r_base
            
        #new_rates = pd.DataFrame(new_rates)
        date_df = pd.DataFrame({'currency': list(new_rates.keys()), 'rate': list(new_rates.values()), 'date': date})
        new_rates_df = new_rates_df.append(date_df)
        # if there is only one currency requested, then just return the number, not a dictionary
        #if len([old_quoted]) == 1:
        #   new_rates = new_rates[old_quoted]
        new_rates_df['date'] = new_rates_df['date'].astype(pd.np.datetime64)
    
    return new_rates_df
    