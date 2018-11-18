import json
from collections import defaultdict
from urllib import request

# http://eshop-checker.xyz/beta
with open('games.json') as f:
    data = map(lambda info: info['price'], json.load(f)['list'])

try:
    with request.urlopen('https://api.exchangeratesapi.io/latest', timeout=3) as r:
        rate = json.loads(r.read().decode('utf-8'))['rates']
    rate['EUR'] = 1
except Exception:
    # http://eshop-checker.xyz/beta
    with open('currency_rate.json') as f:
        rate = json.load(f)['rates']

# 2 char country code to 3 char currency code
# https://www.nationsonline.org/oneworld/country_code_list.htm
# https://www.iban.com/currency-codes
code_name_conversion = {'CA': 'CAD',
                        'MX': 'MXN',
                        'US': 'USD',
                        'DK': 'DKK',
                        'EE': 'EUR',
                        'FI': 'EUR',
                        'IE': 'EUR',
                        'LV': 'EUR',
                        'LT': 'EUR',
                        'NO': 'NOK',
                        'SE': 'SEK',
                        'GB': 'GBP',
                        'HR': 'EUR',
                        'CY': 'EUR',
                        'GR': 'EUR',
                        'IT': 'EUR',
                        'MT': 'EUR',
                        'PT': 'EUR',
                        'SI': 'EUR',
                        'ES': 'EUR',
                        'BG': 'EUR',
                        'CZ': 'CZK',
                        'HU': 'EUR',
                        'PL': 'PLN',
                        'RO': 'EUR',
                        'RU': 'RUB',
                        'SK': 'EUR',
                        'AT': 'EUR',
                        'BE': 'EUR',
                        'FR': 'EUR',
                        'DE': 'EUR',
                        'LU': 'EUR',
                        'NL': 'EUR',
                        'CH': 'CHF',
                        'AU': 'AUD',
                        'NZ': 'NZD',
                        'ZA': 'ZAR',
                        'JP': 'JPY',
                        }


result = defaultdict(int)
for game in data:
    normalized_price = iter((area, lambda: price / rate[code_name_conversion[area]])
                            for area, price in game.items())
    min_ = min(normalized_price, key=lambda info: info[1]())
    result[min_[0]] += 1
print(max(result, key=lambda country: result[country]))
print(result)
