import json
import requests
from decimal import Decimal
import configparser
import os

'''
config = configparser.ConfigParser()
config.read("config.ini")
user_id = config["DEFAULT"].get("user_id")
'''

# Get credentias from Secrets
USER_ID = os.getenv("USER_ID")
if not USER_ID:
    raise ValueError("USER_ID not found")


def get_response(method, url, json=None):
    try:
        if method == "GET":
            response = requests.get(url)
        else:  # POST
            response = requests.post(url, json=json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP error: {e}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {}


def get_he_price(token):
    url = "https://api.hive-engine.com/rpc/contracts"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "find",
        "params": {
            "contract": "marketpools",
            "table": "pools",
            "query": {"tokenPair": token},
            "limit": 1,
        },
    }
    token_price = get_response("POST", url, json=payload)

    return token_price["result"][0]["basePrice"]


def get_maya_price(quantity):
    amount = Decimal(quantity)
    token_amount = int(amount * (10**8))
    url = (
        f"https://mayanode.mayachain.info/mayachain/quote/swap?"
        f"from_asset=ARB.ETH"
        f"&to_asset=ARB.LEO-0X93864D81175095DD93360FFA2A529B8642F76A6E"
        f"&amount={token_amount}"
        f"&destination=0x1EdF9F4d2e98A2eb5DFeeC7f07c2e8b6C3FFaA4E"
        f"&streaming_interval=3"
        f"&streaming_quantity=0"
        f"&liquidity_tolerance_bps=100"
        f"&affiliate_bps=45&affiliate=wr"
    )
    maya_price = get_response("GET", url)
    return maya_price


def get_prices(tokens):
    prices = {}
    for token in tokens:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies=usd"
        price = get_response("GET", url)
        prices[token] = price[token]["usd"]

    return prices


def notification(content):
    webhook_url = "https://discord.com/api/webhooks/1359216089023906063/9PLtNmPUoSwm8UUStyxZzpxVjALWFdKcULtRF3kBJVBzBsVywnXZ4OmvInk8Tt5IhQdW"
    message = {
        "content": f"{content}! <@{USER_ID}>",
        "allowed_mentions": {"users": [USER_ID]},
    }
    response = get_response("POST", webhook_url, json=message)
    if response.status_code == 204:
        print("Notifica inviata con successo!")
    else:
        print("Errore nell'invio della notifica:", response.status_code)


def compare_prices():
    tokens = ["hive", "ethereum"]
    prices = get_prices(tokens)
    one_hundred_dollars = {token: 100 / float(price) for token, price in prices.items()}

    leo_price = get_he_price("SWAP.HIVE:LEO")
    he_leo_amount = one_hundred_dollars['hive'] * float(leo_price) * 0.99

    print(he_leo_amount)

    maya_price = get_maya_price(one_hundred_dollars['ethereum'])
    arb_leo_amount = int(maya_price["expected_amount_out"]) / (10**8)
    
    print(arb_leo_amount)

    threshold = 1.12

    if he_leo_amount > arb_leo_amount * threshold:
        print("HIVE --> LEO --> ARB.LEO --> ETH")
        notification(f"Buy LEO on H-E, Sell LEO on ARB")
    elif arb_leo_amount > he_leo_amount * threshold:
        print("ETH --> ARB.LEO --> LEO --> HIVE")
        notification(f"Buy LEO on ARB, Sell LEO on H-E")
    else:
        print("Nothing to see here")


if __name__ == "__main__":
    compare_prices()
