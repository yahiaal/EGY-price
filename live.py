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
    link = "https://egcurrency.com/ar/currency/egp/exchange"
    resp = requests.get(link, headers=headers)
    encode = html.fromstring(resp.content)
    
    try:
        buyPriceInBlackmarket = encode.xpath("//tbody/tr[1]//td[@class='text-danger'][1]/text()")[0]
    except IndexError:
        try:
            buyPriceInBlackmarket = encode.xpath("//tbody/tr[1]//td[@class='text-success'][1]/text()")[0]
        except IndexError:
            buyPriceInBlackmarket = "غير متاح"
    
    try:
        sellPriceInBlackMarket = encode.xpath("//tbody/tr[1]//td[@class='text-danger'][2]/text()")[0]
    except IndexError:
        try:
            sellPriceInBlackMarket = encode.xpath("//tbody/tr[1]//td[@class='text-success'][2]/text()")[0]
        except IndexError:
            sellPriceInBlackMarket = "غير متاح"

    link2 = "https://egcurrency.com/ar/currency/usd-to-egp/exchange"
    resp2 = requests.get(link2, headers=headers)
    encode1 = html.fromstring(resp2.content)
    
    try:
        buyPriceInBank = encode1.xpath("//tbody/tr[3]/td[2]/text()")[0]
    except IndexError:
        buyPriceInBank = "غير متاح"
    
    try:
        sellPriceInBank = encode1.xpath("//tbody/tr[3]/td[3]/text()")[0]
    except IndexError:
        sellPriceInBank = "غير متاح"

    buyPriceDifferencePercentage = calculate_percentage_difference(buyPriceInBlackmarket, buyPriceInBank) if buyPriceInBlackmarket != "غير متاح" and buyPriceInBank != "غير متاح" else "غير متوفر"
    sellPriceDifferencePercentage = calculate_percentage_difference(sellPriceInBlackMarket, sellPriceInBank) if sellPriceInBlackMarket != "غير متاح" and sellPriceInBank != "غير متاح" else "غير متوفر"

    extraction_datetime = get_current_datetime(user_timezone)

    return {
        "buyPriceInBlackmarket": buyPriceInBlackmarket,
        "sellPriceInBlackMarket": sellPriceInBlackMarket,
        "buyPriceInBank": buyPriceInBank,
        "sellPriceInBank": sellPriceInBank,
        "buyPriceDifferencePercentage": buyPriceDifferencePercentage,
        "sellPriceDifferencePercentage": sellPriceDifferencePercentage,
        "extraction_datetime": extraction_datetime
    }

@app.route('/')
def home():
    rates = fetch_exchange_rates()
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
                        document.getElementById('buyPriceInBlackmarket').innerText = data.buyPriceInBlackmarket;
                        document.getElementById('sellPriceInBlackMarket').innerText = data.sellPriceInBlackMarket;
                        document.getElementById('buyPriceInBank').innerText = data.buyPriceInBank;
                        document.getElementById('sellPriceInBank').innerText = data.sellPriceInBank;
                        document.getElementById('buyPriceDifferencePercentage').innerText = "+" + data.buyPriceDifferencePercentage + "%";
                        document.getElementById('sellPriceDifferencePercentage').innerText = "+" + data.sellPriceDifferencePercentage + "%";
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
                <th>السعر (جنيه مصري لكل دولار أمريكي)</th>
                <th>الفرق النسبي (%)</th>
                <th>وقت الاستخراج</th>
            </tr>
            <tr>
                <td>سعر الشراء في السوق السوداء (جنيه/دولار)</td>
                <td id="buyPriceInBlackmarket">{{ rates.buyPriceInBlackmarket }}</td>
                <td id="buyPriceDifferencePercentage">+{{ rates.buyPriceDifferencePercentage }}%</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
            <tr>
                <td>سعر البيع في السوق السوداء (جنيه/دولار)</td>
                <td id="sellPriceInBlackMarket">{{ rates.sellPriceInBlackMarket }}</td>
                <td id="sellPriceDifferencePercentage">+{{ rates.sellPriceDifferencePercentage }}%</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
            <tr>
                <td>سعر الشراء في البنك (جنيه/دولار)</td>
                <td id="buyPriceInBank">{{ rates.buyPriceInBank }}</td>
                <td>-</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
            <tr>
                <td>سعر البيع في البنك (جنيه/دولار)</td>
                <td id="sellPriceInBank">{{ rates.sellPriceInBank }}</td>
                <td>-</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
        </table>
        <p style="text-align: center; font-size: 20px; font-weight: bold; color: purple; margin-top: 40px;"> تصميم و برمجة: Yahia Zakaria Almarafi</p>
        <p style="text-align: center; margin-top: 20px;"><a href="https://github.com/yahiaal/EGY-price/blob/main/live.py" style="font-size: 18px; font-weight: bold; color: navy; text-decoration: none;">Source Code</a></p>

    </body>
    </html>
    """
    return render_template_string(html_template, rates=rates)

@app.route('/api/rates')
def api_rates():
    user_timezone = request.args.get('timezone', 'UTC')
    rates = fetch_exchange_rates(user_timezone)
    return jsonify(rates)

if __name__ == '__main__':
    app.run(debug=True)
