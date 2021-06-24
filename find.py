import json
import concurrent.futures
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


def download_data() -> (dict, dict):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(download_game_data): 'data',
            executor.submit(download_currency_rate): 'rate'
        }
        for future in concurrent.futures.as_completed(futures):
            type_ = futures[future]
            if type_ == 'data':
                data = future.result()
            elif type_ == 'rate':
                rate = future.result()
    return data, rate


def main() -> dict:
    result = {
        area: {'releases': 0, 'win': 0}
        for area in country_to_currency_conversion
    }
    data, rate = download_data()
    for game in data:
        for country in game:
            result[country]['releases'] += 1

        normalized_price =\
            ((area, price / rate[country_to_currency_conversion[area]])
             for area, price in game.items())
        min_ = min(normalized_price, key=lambda info: info[1])
        country = min_[0]
        result[country]['win'] += 1
    return result


if __name__ == '__main__':
    result = main()

    most_count = max(result, key=lambda country: result[country].get('win', 0))
    print('{country} has {count} games with good prices'
          .format(country=most_count, count=result[most_count]['win']))

    highest_rate = max(
        result, key=lambda country: result[country].get('win', 0) / result[country]['releases'])
    print('{country} has {percent}% of games with good prices'
          .format(country=highest_rate,
                  percent=round(result[highest_rate]['win'] / result[highest_rate]['releases'] * 100, 2)))

    print(result)
