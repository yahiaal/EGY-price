from flask import Flask, render_template_string, jsonify
import requests
from lxml import html
from datetime import datetime

app = Flask(__name__)

def calculate_percentage_difference(higher_value, lower_value):
    difference = float(higher_value) - float(lower_value)
    percentage_difference = (difference / float(lower_value)) * 100
    return round(percentage_difference, 2)

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def fetch_exchange_rates():
    link = "https://egcurrency.com/ar/currency/egp/exchange"
    resp = requests.get(link)
    encode = html.fromstring(resp.content)
    buyPriceInBlackmarket = encode.xpath("//tbody/tr[1]//td[@class='text-danger'][1]/text()")[0]
    sellPriceInBlackMarket = encode.xpath("//tbody/tr[1]//td[@class='text-danger'][2]/text()")[0]

    link2 = "https://egcurrency.com/ar/currency/usd-to-egp/exchange"
    resp2 = requests.get(link2)
    encode1 = html.fromstring(resp2.content)
    buyPriceInBank = encode1.xpath("//tbody/tr[3]/td[2]/text()")[0]
    sellPriceInBank = encode1.xpath("//tbody/tr[3]/td[3]/text()")[0]

    buyPriceDifferencePercentage = calculate_percentage_difference(buyPriceInBlackmarket, buyPriceInBank)
    sellPriceDifferencePercentage = calculate_percentage_difference(sellPriceInBlackMarket, sellPriceInBank)

    extraction_datetime = get_current_datetime()

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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>EGP Exchange Rates</title>
        <style>
            body {
                font-family: Arial, sans-serif;
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
                text-align: left;
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
            /* Button styling */
            button {
                display: block;
                margin: 20px auto;
                padding: 10px 20px;
                font-size: 16px;
                color: #fff;
                background-color: #4CAF50; /* Button color */
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #45a049; /* Button hover effect */
            }
            /* Success message styling */
            .success-message {
                color: #4CAF50;
                text-align: center;
                display: none; /* Hide by default */
                margin-top: 20px;
            }
        </style>
        <script>
            function refreshRates() {
                fetch('/api/rates')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('buyPriceInBlackmarket').innerText = data.buyPriceInBlackmarket;
                        document.getElementById('sellPriceInBlackMarket').innerText = data.sellPriceInBlackMarket;
                        document.getElementById('buyPriceInBank').innerText = data.buyPriceInBank;
                        document.getElementById('sellPriceInBank').innerText = data.sellPriceInBank;
                        document.getElementById('buyPriceDifferencePercentage').innerText = "+" + data.buyPriceDifferencePercentage + "%";
                        document.getElementById('sellPriceDifferencePercentage').innerText = "+" + data.sellPriceDifferencePercentage + "%";
                        
                        // Update all extraction_datetime placeholders
                        var datetimeElements = document.getElementsByClassName('extraction-datetime');
                        for(var i = 0; i < datetimeElements.length; i++) {
                            datetimeElements[i].innerText = data.extraction_datetime;
                        }
                        
                        // Show success message
                        var successMessage = document.getElementById('successMessage');
                        successMessage.style.display = 'block';
                        setTimeout(function() { successMessage.style.display = 'none'; }, 3000); // Hide after 3 seconds
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }
        </script>
    </head>
    <body>
        <h1>EGP Exchange Rates</h1>
        <button onclick="refreshRates()">Refresh Rates</button>
        <div class="success-message" id="successMessage">Data refreshed successfully!</div>
        <table>
            <tr>
                <th>Description</th>
                <th>Rate (EGP per USD)</th>
                <th>Difference (%)</th>
                <th>Extraction Time</th>
            </tr>
            <tr>
                <td>Buy price in Black Market (EGP/USD)</td>
                <td id="buyPriceInBlackmarket">{{ rates.buyPriceInBlackmarket }}</td>
                <td id="buyPriceDifferencePercentage">+{{ rates.buyPriceDifferencePercentage }}%</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
            <tr>
                <td>Sell Price in Black Market (EGP/USD)</td>
                <td id="sellPriceInBlackMarket">{{ rates.sellPriceInBlackMarket }}</td>
                <td id="sellPriceDifferencePercentage">+{{ rates.sellPriceDifferencePercentage }}%</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
            <tr>
                <td>Buy Price in Bank (EGP/USD)</td>
                <td id="buyPriceInBank">{{ rates.buyPriceInBank }}</td>
                <td>-</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
            <tr>
                <td>Sell Price in Bank (EGP/USD)</td>
                <td id="sellPriceInBank">{{ rates.sellPriceInBank }}</td>
                <td>-</td>
                <td class="extraction-datetime">{{ rates.extraction_datetime }}</td>
            </tr>
        </table>
        <p>Coded by: MO-Gambul</p>
    </body>
    </html>
    """
    return render_template_string(html_template, rates=rates)

@app.route('/api/rates')
def api_rates():
    rates = fetch_exchange_rates()
    return jsonify(rates)

if __name__ == '__main__':
    app.run(debug=True)
