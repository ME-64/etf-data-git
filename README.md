# European ETF Data - Web Scrape
***

Due to the regulatory requirement that Exchange Traded Funds (ETFs) must adhere too - the majority of financial data related to ETFs is publically available on each issuers respective websites, updated frequently.

This means that rather than rely on expensive and legacy data feeds from data vendors, one can go freely obtain this information from the internet.

This is the repository for the 'etfscraper' object that allows users to fetch this information from websites programatically.

Currently only 1 issuer website implemented, and not all desired datapoints either.


### Sample usage:
```
import pandas as pd

#Initiate the object
etf = Etf_scrape(debug=False)

#method to return a current datapoint for a given list of isins
df = etf.jpmBDP(isins = 'IE00BJK9H860', datapoints = 'fund_aum')
#>returns fund aum in dataframe
```


