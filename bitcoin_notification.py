import logging
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

IFTTT_WEBHOOK_KEY = os.getenv("IFTTT_WEBHOOK_KEY")
COIN_MARKETCAP_API_KEY = os.getenv("COIN_MARKETCAP_API_KEY")

if (IFTTT_WEBHOOK_KEY or COIN_MARKETCAP_API_KEY) is None:
    raise Exception("You need to setup environment variables. Check env.example or the README.md for more info")


BITCOIN_PRICE_THRESHOLD = 50000 # you can set this to any value
BITCOIN_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
IFTTT_WEBHOOK_URL = 'https://maker.ifttt.com/trigger/{}/with/key/'+IFTTT_WEBHOOK_KEY

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def get_latest_bitcoin_price():
    """
    You can obtain COINMARKETCAP_API_KEY FROM https://coinmarketcap.com/
    """
    response = requests.get(BITCOIN_API_URL, headers={"X-CMC_PRO_API_KEY": COIN_MARKETCAP_API_KEY})
    response_json = response.json()
    logging.info('Latest Bitcoin price fetched successfully')
    logging.info("PRICE = " +str(response_json['data'][0]['quote']['USD']['price']))
    return float(response_json['data'][0]['quote']['USD']['price']) # Convert the price to a floating point number

def post_ifttt_webhook(event, value):
    # logging.info('typeof value')
    # print(value)
    # currency_string = "{:,.2f}".format(value)
    data = {'value1': value} # The payload that will be sent to IFTTT service
    logging.info(data)
    ifttt_event_url = IFTTT_WEBHOOK_URL.format(event)  # Inserts our desired event
    logging.info('Webhook sent for event, '+ event);
    requests.post(ifttt_event_url, json=data) # Sends a HTTP POST request to the webhook URL

def format_bitcoin_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        date = bitcoin_price['date'].strftime('%d.%m.%Y %H:%M') # Formats the date into a string: '24.02.2018 15:09'
        price = bitcoin_price['price']
        # <b> (bold) tag creates bolded text
        row = '{}: $<b>{}</b>'.format(date, price)  # 24.02.2018 15:09: $<b>10123.4</b>
        rows.append(row)
    # Use a <br> (break) tag to create a new line
    return '<br>'.join(rows)  # Join the rows delimited by <br> tag: row1<br>row2<br>row3

def main():
    bitcoin_history = []
    logging.info("Application running")
    while True:
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if price >= BITCOIN_PRICE_THRESHOLD:
            post_ifttt_webhook("bitcoin_price_emergency", price)

        # Send a Telegram notification
        if len(bitcoin_history) == 5: # Once we have 2 items in our bitcoin_history send an update
            post_ifttt_webhook("bitcoin_price_update", format_bitcoin_history(bitcoin_history))
            # Reset the history
            bitcoin_history = []

        time.sleep(5 * 60) # Sleep for 5 minutes

if __name__ == '__main__':
    main()


