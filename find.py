import json
from collections import defaultdict
from gzip import decompress
from urllib import request

with request.urlopen('http://eshop-checker.xyz/games.json', timeout=3) as f:
    # we only need the price of each game
    # each element in `data` looks like {'CA': 123, 'ZA': 234} <= {AREA: PRICE}
    data = map(lambda info: info['price'],
               json.loads(decompress(f.read()))['list'])

with request.urlopen('http://eshop-checker.xyz/beta/statics/conv_rate.json', timeout=3) as f:
    rate = json.loads(decompress(f.read()))['rates']

# 2 char country code to 3 char currency code
# https://www.nationsonline.org/oneworld/country_code_list.htm
# https://www.iban.com/currency-codes
country_to_currency_conversion = {'CA': 'CAD',
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
    normalized_price = iter(
        (area, lambda: price / rate[country_to_currency_conversion[area]])
        for area, price in game.items())
    min_ = min(normalized_price, key=lambda info: info[1]())
    country = min_[0]
    result[country] += 1

# print out 2 char country name
print(max(result, key=lambda country: result[country]))
print(result)
