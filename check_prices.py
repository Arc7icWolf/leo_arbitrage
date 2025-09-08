import json
import requests


def get_response(method, url, json=None):
    try:
        if method == "GET":
            response = requests.get(url)
        else: # POST
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
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "find",
        "params": {
            "contract": "marketpools",
            "table": "pools",
            "query": {"tokenPair": "SWAP.HIVE:LEO"},
            "limit": 1,
        },
    }
    pool_price = get_response("POST", url, json=payload)
    return pool_price


def get_maya_price():
    url = (
      "https://mayanode.mayachain.info/mayachain/quote/swap?"
      "from_asset=ARB.ETH"
      "&to_asset=ARB.LEO-0X93864D81175095DD93360FFA2A529B8642F76A6E"
      "&amount=2330000"
      "&destination=0x1EdF9F4d2e98A2eb5DFeeC7f07c2e8b6C3FFaA4E"
      "&streaming_interval=3"
      "&streaming_quantity=0"
      "&liquidity_tolerance_bps=100"
      "&affiliate_bps=45&affiliate=wr"
    )
    maya_price = get_response("GET", url)
    return maya_price


def compare_prices():
    he_price = get_he_price()
    print(he_price)
    maya_price = get_maya_price()
    print(maya_price)


if __name__ == "__main__":
    compare_prices()
