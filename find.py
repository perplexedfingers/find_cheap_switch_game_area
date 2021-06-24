import json
from collections import defaultdict
from gzip import decompress
from urllib import request

# 2 char country code to 3 char currency code
# https://www.nationsonline.org/oneworld/country_code_list.htm
# https://www.iban.com/currency-codes
country_to_currency_conversion = {
    'CA': 'CAD',
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


def download_game_data() -> dict:
    # we only need the price of each game
    # each element in `data` looks like {'CA': 123, 'ZA': 234} <= {AREA: PRICE}
    with request.urlopen('http://eshop-checker.xyz/games.json', timeout=3) as f:
        data = map(lambda info: info['price'],
                   json.loads(decompress(f.read()))['list'])
    return data


def download_currency_rate() -> dict:
    with request.urlopen('http://eshop-checker.xyz/beta/statics/conv_rate.json', timeout=3) as f:
        rate = json.loads(decompress(f.read()))['rates']
    return rate


def main() -> defaultdict:
    result = defaultdict(dict)
    data = download_game_data()
    rate = download_currency_rate()
    for game in data:
        for country in game:
            result[country]['count'] = result[country].get('count', 0) + 1

        normalized_price =\
            ((area, price / rate[country_to_currency_conversion[area]])
             for area, price in game.items())
        min_ = min(normalized_price, key=lambda info: info[1])
        country = min_[0]
        result[country]['win'] = result[country].get('win', 0) + 1
    return result


if __name__ == '__main__':
    result = main()

    most_count = max(result, key=lambda country: result[country].get('win', 0))
    print('{country} has {count} games with good prices'
          .format(country=most_count, count=result[most_count]['win']))

    most_rate = max(result, key=lambda country: result[country].get('win', 0) / result[country]['count'])
    print('{country} has {percent}% of games with good prices'
          .format(country=most_rate, percent=round(result[most_rate]['win'] / result[most_rate]['count'] * 100, 2)))

    print(result)
