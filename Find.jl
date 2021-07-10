import HTTP
import JSON
import CodecZlib
import TranscodingStreams


const country_to_currency_conversion = Base.ImmutableDict(
    "CA" => "CAD",
    "MX" => "MXN",
    "US" => "USD",
    "DK" => "DKK",
    "EE" => "EUR",
    "FI" => "EUR",
    "IE" => "EUR",
    "LV" => "EUR",
    "LT" => "EUR",
    "NO" => "NOK",
    "SE" => "SEK",
    "GB" => "GBP",
    "HR" => "EUR",
    "CY" => "EUR",
    "GR" => "EUR",
    "IT" => "EUR",
    "MT" => "EUR",
    "PT" => "EUR",
    "SI" => "EUR",
    "ES" => "EUR",
    "BG" => "EUR",
    "CZ" => "CZK",
    "HU" => "EUR",
    "PL" => "PLN",
    "RO" => "EUR",
    "RU" => "RUB",
    "SK" => "EUR",
    "AT" => "EUR",
    "BE" => "EUR",
    "FR" => "EUR",
    "DE" => "EUR",
    "LU" => "EUR",
    "NL" => "EUR",
    "CH" => "CHF",
    "AU" => "AUD",
    "NZ" => "NZD",
    "ZA" => "ZAR",
    "JP" => "JPY",
)


function download_decompressed_gzip_json(url::String)::Dict
    r = HTTP.get(url)
    decompressed = transcode(CodecZlib.GzipDecompressor, r.body)
    JSON.parse(String(decompressed))
end


function download_game_data()::Vector{Dict{String,Any}}
    url = "http://eshop-checker.xyz/games.json"
    result = download_decompressed_gzip_json(url)
    [info["price"] for info in result["list"] if any(x -> x !== 0, values(info["price"]))]
end

function download_currency_rate()::Dict{String,Any}
    url = "http://eshop-checker.xyz/beta/statics/conv_rate.json"
    result = download_decompressed_gzip_json(url)
    result["rates"]
end

function compute(data::Vector{Dict{String,Any}}, rate::Dict{String,Any})
    release_count = Dict([(area, 0) for area in Base.keys(country_to_currency_conversion)])
    price_count = Dict([(area, 0) for area in Base.keys(country_to_currency_conversion)])
    for game in data
        _price, _country = Inf, missing
        for (country, price) in filter(a -> a[1] !== 0, pairs(game))
            release_count[country] += 1
            normalized_price = price / rate[country_to_currency_conversion[country]]
            if normalized_price < _price
                _price, _country = normalized_price, country
            end
        end
        price_count[_country] += 1
    end
    release_count, price_count
end

function download_all()
    t_data = @async download_game_data()
    t_rate = @async download_currency_rate()
    fetch(t_data), fetch(t_rate)
end

function main()
    data, rate = download_all()

    release_count, price_count = compute(data, rate)

    most_count, c_country = findmax(price_count)
    most_rate, r_country = findmax(Dict([(area, price_win / get(release_count, area, Inf)) for (area, price_win) in price_count]))

    println("$c_country has $most_count games with good prices")
    println("$r_country has $(round(most_rate * 100, digits=2))% of games with good prices")
    println(release_count, price_count)
end
