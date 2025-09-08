import json
import requests
from decimal import Decimal


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


def get_he_price():
    url = "https://api.hive-engine.com/rpc/contracts"
    tokens = ["SWAP.HIVE:LEO", "SWAP.HIVE:SWAP.ETH"]
    token_prices = []
    for token in tokens:
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
        token_prices.append(token_price)
    return token_prices


def get_maya_price(quantity):
    amount = Decimal(quantity)
    token_amount = int(amount * (10**8))
    url = (
        f"https://mayanode.mayachain.info/mayachain/quote/swap?"
        f"from_asset=ARB.LEO-0X93864D81175095DD93360FFA2A529B8642F76A6E"
        f"&to_asset=ARB.ETH"
        f"&amount={token_amount}"
        f"&destination=0x1EdF9F4d2e98A2eb5DFeeC7f07c2e8b6C3FFaA4E"
        f"&streaming_interval=3"
        f"&streaming_quantity=0"
        f"&liquidity_tolerance_bps=100"
        f"&affiliate_bps=45&affiliate=wr"
    )
    maya_price = get_response("GET", url)
    return maya_price


def get_price(token):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies=usd"
    price = get_response("GET", url)
    return price["hive"]["usd"]


def compare_prices():
    token = "hive"
    price = get_price(token)

    token_amount = 100 / price

    he_price = get_he_price()
    leo_price = he_price[0]["result"][0]["basePrice"]
    eth_price = he_price[1]["result"][0]["quotePrice"]

    leo = token_amount * float(leo_price) * 0.99 * 0.895

    maya_price = get_maya_price(leo)

    eth_quantity = int(maya_price["expected_amount_out"]) / (10**8)

    new_token_amount = eth_quantity * 0.99 * 0.999 * float(eth_price)
    print(new_token_amount)

    if new_token_amount * 1.05 > token_amount:
        print("Let's go!")
    else:
        print("Nothing to see here")


if __name__ == "__main__":
    compare_prices()
