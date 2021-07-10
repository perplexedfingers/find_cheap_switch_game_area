import json
import concurrent.futures
from gzip import decompress
from urllib import request
# from collections import Counter

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
        data = [info['price'] for info in json.loads(decompress(f.read()))['list']
                if any(info['price'].values())]
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


def compute(data: dict, rate: dict) -> dict:
    # TODO use less passes
    result = {
        area: {'releases': 0, 'win': 0}
        for area in country_to_currency_conversion
    }

    for game in data:
        _price, _area = float('Inf'), None
        for area, price in filter(lambda g: g[1] != 0, game.items()):
            result[area]['releases'] += 1
            normalized_price = price / rate[country_to_currency_conversion[area]]
            if normalized_price < _price:
                _price, _area = normalized_price, area
        result[_area]['win'] += 1

    # total_game_count = len(data)
    # full_table = {
    #     area: [None] * total_game_count
    #     for area in country_to_currency_conversion
    # }
    # for i, game in enumerate(data):
    #     for area in filter(lambda area: area in game, country_to_currency_conversion):
    #         full_table[area][i] = game[area]
    # win_count = Counter(
    #     (min(((area, price[i] / rate[country_to_currency_conversion[area]])
    #           for area, price in full_table.items() if price[i]),
    #          key=lambda x: x[1])[0]
    #      for i in range(total_game_count))
    # )
    # result = {
    #     area: {
    #         'releases': len([x for x in full_table[area] if x]),
    #         'win': win_count[area]
    #     } for area in country_to_currency_conversion
    # }

    # result = {
    #     area: {'releases': 0, 'win': 0}
    #     for area in country_to_currency_conversion
    # }
    # for game in data:
    #     for country in game:
    #         result[country]['releases'] += 1

    #     normalized_price =\
    #         ((area, price / rate[country_to_currency_conversion[area]])
    #          for area, price in game.items())
    #     min_ = min(normalized_price, key=lambda info: info[1])
    #     country = min_[0]
    #     result[country]['win'] += 1
    return result


if __name__ == '__main__':
    data, rate = download_data()

    result = compute(data, rate)

    most_count = max(result, key=lambda country: result[country].get('win', 0))
    highest_rate = max(
        result, key=lambda country: result[country].get('win', 0) / result[country]['releases'])

    print('{country} has {count} games with good prices'
          .format(country=most_count, count=result[most_count]['win']))
    print('{country} has {percent}% of games with good prices'
          .format(country=highest_rate,
                  percent=round(result[highest_rate]['win'] / result[highest_rate]['releases'] * 100, 2)))
    print(result)
