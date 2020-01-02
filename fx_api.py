import requests
import urllib


def get_fx(quoted, date, base='USD', main_api ='http://data.fixer.io/api/', key='c263b908a641e8146deac4b2eeb27c17'):
    old_quoted = tuple(quoted.copy())[0]
    # convert to list of not
    if isinstance(quoted, str):
        quoted = [quoted]
        
    if base not in quoted:
        quoted.append(base)
    
        
    # comma seperate the currencies
    quoted = ','.join(quoted)
    
    # set parameters
    params = {'access_key': key,
              'base': 'EUR',
              'symbols': quoted}
    
    
    url = main_api + date + '?' + urllib.parse.urlencode(params)
    
    fx = requests.get(url).json()
    
    rates = fx['rates']
    
    r_base = 1 / rates[base]
    
    new_rates = {}
    
    for k, v in rates.items():
        
        new_rates[k] = v * r_base
     
    if len([old_quoted]) == 1:
        new_rates = new_rates[old_quoted]
    
    return new_rates
    