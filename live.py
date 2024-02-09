from flask import Flask, render_template_string, jsonify, request
import requests
from lxml import html
from datetime import datetime
import pytz

app = Flask(__name__)

def calculate_percentage_difference(higher_value, lower_value):
    difference = float(higher_value) - float(lower_value)
    percentage_difference = (difference / float(lower_value)) * 100
    return round(percentage_difference, 2)

def get_current_datetime(user_timezone='UTC'):
    now_utc = datetime.now(pytz.timezone('UTC'))
    user_time = now_utc.astimezone(pytz.timezone(user_timezone))
    return user_time.strftime("%Y-%m-%d %H:%M:%S")

def fetch_exchange_rates(user_timezone='UTC'):
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # USD Prices
    link_usd = "https://egcurrency.com/ar/currency/egp/exchange"
    resp_usd = requests.get(link_usd, headers=headers)
    encode_usd = html.fromstring(resp_usd.content)

    # Fetching USD prices
    buyPriceInBlackmarketUSD, sellPriceInBlackMarketUSD, buyPriceInBankUSD, sellPriceInBankUSD = fetch_usd_prices(encode_usd)

    # EUR Prices
    link_eur = "https://egcurrency.com/ar/currency/eur-to-egp/cbe"
    resp_eur = requests.get(link_eur, headers=headers)
    encode_eur = html.fromstring(resp_eur.content)

    # Fetching EUR prices
    buyPriceInBlackmarketEUR, sellPriceInBlackMarketEUR, buyPriceInBankEUR, sellPriceInBankEUR = fetch_eur_prices(encode_eur)

    # Calculating differences
    buyPriceDifferencePercentageUSD = calculate_percentage_difference(buyPriceInBlackmarketUSD, buyPriceInBankUSD) if buyPriceInBlackmarketUSD != "غير متاح" and buyPriceInBankUSD != "غير متاح" else "غير متوفر"
    sellPriceDifferencePercentageUSD = calculate_percentage_difference(sellPriceInBlackMarketUSD, sellPriceInBankUSD) if sellPriceInBlackMarketUSD != "غير متاح" and sellPriceInBankUSD != "غير متاح" else "غير متوفر"

    buyPriceDifferencePercentageEUR = calculate_percentage_difference(buyPriceInBlackmarketEUR, buyPriceInBankEUR) if buyPriceInBlackmarketEUR != "غير متاح" and buyPriceInBankEUR != "غير متاح" else "غير متوفر"
    sellPriceDifferencePercentageEUR = calculate_percentage_difference(sellPriceInBlackMarketEUR, sellPriceInBankEUR) if sellPriceInBlackMarketEUR != "غير متاح" and sellPriceInBankEUR != "غير متاح" else "غير متوفر"

    extraction_datetime = get_current_datetime(user_timezone)

    return {
        "buyPriceInBlackmarketUSD": buyPriceInBlackmarketUSD,
        "sellPriceInBlackMarketUSD": sellPriceInBlackMarketUSD,
        "buyPriceInBankUSD": buyPriceInBankUSD,
        "sellPriceInBankUSD": sellPriceInBankUSD,
        "buyPriceDifferencePercentageUSD": buyPriceDifferencePercentageUSD,
        "sellPriceDifferencePercentageUSD": sellPriceDifferencePercentageUSD,
        "buyPriceInBlackmarketEUR": buyPriceInBlackmarketEUR,
        "sellPriceInBlackMarketEUR": sellPriceInBlackMarketEUR,
        "buyPriceInBankEUR": buyPriceInBankEUR,
        "sellPriceInBankEUR": sellPriceInBankEUR,
        "buyPriceDifferencePercentageEUR": buyPriceDifferencePercentageEUR,
        "sellPriceDifferencePercentageEUR": sellPriceDifferencePercentageEUR,
        "extraction_datetime": extraction_datetime
    }

def fetch_usd_prices(encode):
    try:
        buyPriceInBlackmarket = encode.xpath("//tbody//a[@href='/ar/currency/usd-to-egp/exchange']/ancestor::td/following-sibling::td[1]/text()")[0]
    except IndexError:
        buyPriceInBlackmarket = "غير متاح"
    
    try:
        sellPriceInBlackMarket = encode.xpath("//tbody//a[@href='/ar/currency/usd-to-egp/exchange']/ancestor::td/following-sibling::td[2]/text()")[0]
    except IndexError:
        sellPriceInBlackMarket = "غير متاح"

    link2 = "https://egcurrency.com/ar/currency/usd-to-egp/exchange"
    resp2 = requests.get(link2)
    encode1 = html.fromstring(resp2.content)
    
    try:
        buyPriceInBank = encode1.xpath("//tbody/tr[3]/td[2]/text()")[0]
    except IndexError:
        buyPriceInBank = "غير متاح"
    
    try:
        sellPriceInBank = encode1.xpath("//tbody/tr[3]/td[3]/text()")[0]
    except IndexError:
        sellPriceInBank = "غير متاح"

    return buyPriceInBlackmarket, sellPriceInBlackMarket, buyPriceInBank, sellPriceInBank

def fetch_eur_prices(encode):
    try:
        buyPriceInBlackmarketEUR = encode.xpath("//tbody//tr[1]//td[2]/text()")[0]
    except IndexError:
        buyPriceInBlackmarketEUR = "غير متاح"
    
    try:
        sellPriceInBlackMarketEUR = encode.xpath("//tbody//tr[1]//td[3]/text()")[0]
    except IndexError:
        sellPriceInBlackMarketEUR = "غير متاح"

    try:
        buyPriceInBankEUR = encode.xpath("//tbody/tr[6]//td[2]/text()")[0]
    except IndexError:
        buyPriceInBankEUR = "غير متاح"
    
    try:
        sellPriceInBankEUR = encode.xpath("//tbody/tr[6]//td[3]/text()")[0]
    except IndexError:
        sellPriceInBankEUR = "غير متاح"

    return buyPriceInBlackmarketEUR, sellPriceInBlackMarketEUR, buyPriceInBankEUR, sellPriceInBankEUR

@app.route('/')
def home():
    rates = fetch_exchange_rates()
    # Adjust your HTML template here to include EUR rates similarly to how USD rates are included.
    html_template = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>أسعار صرف الجنيه المصري</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            direction: rtl;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }
        h1 {
            color: #333;
            text-align: center;
            padding: 20px 0;
        }
        table {
            width: 80%;
            margin: 20px auto;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ccc;
            text-align: right;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
        p {
            text-align: center;
            color: #666;
        }
        button {
            display: block;
            margin: 20px auto;
            padding: 10px 20px;
            font-size: 16px;
            color: #fff;
            background-color: #4CAF50;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #45a049;
        }
        .success-message {
            color: #4CAF50;
            text-align: center;
            display: none;
            margin-top: 20px;
        }
    </style>
    <script>
        function refreshRates() {
            const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            fetch(`/api/rates?timezone=${encodeURIComponent(userTimeZone)}`)
                .then(response => response.json())
                .then(data => {
                    // Update USD rates
                    document.getElementById('buyPriceInBlackmarketUSD').innerText = data.buyPriceInBlackmarketUSD;
                    document.getElementById('sellPriceInBlackMarketUSD').innerText = data.sellPriceInBlackMarketUSD;
                    document.getElementById('buyPriceInBankUSD').innerText = data.buyPriceInBankUSD;
                    document.getElementById('sellPriceInBankUSD').innerText = data.sellPriceInBankUSD;
                    document.getElementById('buyPriceDifferencePercentageUSD').innerText = "+" + data.buyPriceDifferencePercentageUSD + "%";
                    document.getElementById('sellPriceDifferencePercentageUSD').innerText = "+" + data.sellPriceDifferencePercentageUSD + "%";
                    
                    // Update EUR rates
                    document.getElementById('buyPriceInBlackmarketEUR').innerText = data.buyPriceInBlackmarketEUR;
                    document.getElementById('sellPriceInBlackMarketEUR').innerText = data.sellPriceInBlackMarketEUR;
                    document.getElementById('buyPriceInBankEUR').innerText = data.buyPriceInBankEUR;
                    document.getElementById('sellPriceInBankEUR').innerText = data.sellPriceInBankEUR;
                    document.getElementById('buyPriceDifferencePercentageEUR').innerText = "+" + data.buyPriceDifferencePercentageEUR + "%";
                    document.getElementById('sellPriceDifferencePercentageEUR').innerText = "+" + data.sellPriceDifferencePercentageEUR + "%";
                    
                    var datetimeElements = document.getElementsByClassName('extraction-datetime');
                    for(var i = 0; i < datetimeElements.length; i++) {
                        datetimeElements[i].innerText = data.extraction_datetime;
                    }
                    var successMessage = document.getElementById('successMessage');
                    successMessage.style.display = 'block';
                    setTimeout(function() { successMessage.style.display = 'none'; }, 3000);
                })
                .catch(error => console.error('Error fetching data:', error));
        }
        window.onload = function() {
            refreshRates();
        };
    </script>
</head>
<body>
    <h1>أسعار صرف الجنيه المصري</h1>
    <button onclick="refreshRates()">تحديث الأسعار</button>
    <div class="success-message" id="successMessage">تم تحديث البيانات بنجاح!</div>
    <table>
        <tr>
            <th>الوصف</th>
            <th>السعر (جنيه مصري لكل دولار/يورو)</th>
            <th>الفرق النسبي (%)</th>
            <th>وقت الاستخراج</th>
        </tr>
        <tr>
            <td>سعر الشراء في السوق السوداء (دولار)</td>
            <td id="buyPriceInBlackmarketUSD">{{ rates.buyPriceInBlackmarketUSD }}</td>
            <td id="buyPriceDifferencePercentageUSD">+{{ rates.buyPriceDifferencePercentageUSD }}%</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <tr>
            <td>سعر البيع في السوق السوداء (دولار)</td>
            <td id="sellPriceInBlackMarketUSD">{{ rates.sellPriceInBlackMarketUSD }}</td>
            <td id="sellPriceDifferencePercentageUSD">+{{ rates.sellPriceDifferencePercentageUSD }}%</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <tr>
            <td>سعر الشراء في البنك (دولار)</td>
            <td id="buyPriceInBankUSD">{{ rates.buyPriceInBankUSD }}</td>
            <td>-</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <tr>
            <td>سعر البيع في البنك (دولار)</td>
            <td id="sellPriceInBankUSD">{{ rates.sellPriceInBankUSD }}</td>
            <td>-</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <!-- EUR Rates -->
        <tr>
            <td>سعر الشراء في السوق السوداء (يورو)</td>
            <td id="buyPriceInBlackmarketEUR">{{ rates.buyPriceInBlackmarketEUR }}</td>
            <td id="buyPriceDifferencePercentageEUR">+{{ rates.buyPriceDifferencePercentageEUR }}%</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <tr>
            <td>سعر البيع في السوق السوداء (يورو)</td>
            <td id="sellPriceInBlackMarketEUR">{{ rates.sellPriceInBlackMarketEUR }}</td>
            <td id="sellPriceDifferencePercentageEUR">+{{ rates.sellPriceDifferencePercentageEUR }}%</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <tr>
            <td>سعر الشراء في البنك (يورو)</td>
            <td id="buyPriceInBankEUR">{{ rates.buyPriceInBankEUR }}</td>
            <td>-</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
        <tr>
            <td>سعر البيع في البنك (يورو)</td>
            <td id="sellPriceInBankEUR">{{ rates.sellPriceInBankEUR }}</td>
            <td>-</td>
            <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
        </tr>
    </table>
    <p style="text-align: center; font-size: 20px; font-weight: bold; color: purple; margin-top: 40px;"> تصميم و برمجة: Yahia Zakaria Almarafi</p>
    <p style="text-align: center; margin-top: 20px;"><a href="https://github.com/yahiaal/EGY-price/blob/main/live.py" style="font-size: 18px; font-weight: bold; color: navy; text-decoration: none;" target="_blank">Source Code</a></p>
</body>
</html>
    """
    # You need to adjust the rendering part here to pass EUR rates to the template.
    return render_template_string(html_template, rates=rates)

@app.route('/api/rates')
def api_rates():
    user_timezone = request.args.get('timezone', 'UTC')
    rates = fetch_exchange_rates(user_timezone)
    return jsonify(rates)

if __name__ == '__main__':
    app.run(debug=True)
