from ..discord import logbot
import json, os
from ..data import Config
import mapConfig
from ..resources import properties

'''
subaccount_name = 'SUBACCOUNT_NAME'
leverage = 1.0
risk = 1.0 / 100
api_key = 'API_KEY'
api_secret = 'API_SECRET'


# ================== SET GLOBAL VARIABLES ==================


def global_var(payload):
    global subaccount_name
    global leverage
    global risk
    global api_key
    global api_secret
    global passphrase

    API_KEY = "API_KEY"

    okxConfig = APIkey.APIkey(
        os.environ.get(API_KEY, OkxConfig.API_SECRET)
    )

    subaccount_name = payload['subaccount']

    if subaccount_name == 'Testing':
        leverage = os.environ.get('LEVERAGE_TESTING', OkxConfig.LEVERAGE_TESTING)
        leverage = float(leverage)

        risk = os.environ.get('RISK_TESTING', config.RISK_TESTING)
        risk = float(risk) / 100

        api_key = os.environ.get('API_KEY_TESTING', config.API_KEY_TESTING)

        api_secret = os.environ.get('API_SECRET_TESTING', config.API_SECRET_TESTING)
        logbot.logs('Testing exchange activated')

    elif subaccount_name == 'MYBYBITACCOUNT':
        leverage = os.environ.get('LEVERAGE_MYBYBITACCOUNT', config.LEVERAGE_MYBYBITACCOUNT)
        leverage = float(leverage)

        risk = os.environ.get('RISK_MYBYBITACCOUNT', config.RISK_MYBYBITACCOUNT)
        risk = float(risk) / 100

        api_key = os.environ.get('API_KEY_MYBYBITACCOUNT', config.API_KEY_MYBYBITACCOUNT)

        api_secret = os.environ.get('API_SECRET_MYBYBITACCOUNT', config.API_SECRET_MYBYBITACCOUNT)

        logbot.logs('ByBit exchange activated')

    elif subaccount_name == 'OKX':
        leverage = os.environ.get('LEVERAGE_OKX', config.LEVERAGE_OKX)
        leverage = float(leverage)

        risk = os.environ.get('RISK_OKX', config.RISK_OKX)
        risk = float(risk) / 100

        api_key = os.environ.get('API_KEY_OKX', config.API_KEY_OKX)

        api_secret = os.environ.get('API_SECRET_OKX', config.API_SECRET_OKX)

        passphrase = os.environ.get('PASSPHRASE_OKX', config.PASSPHRASE_OKX)

        logbot.logs('OKX exchange activated')

    else:
        logbot.logs(">>> /!\ Subaccount name not found", True)
        return {
            "success": False,
            "error": "subaccount name not found"
        }

    return {
        "success": True
    }
'''

# ================== MAIN ==================


def order(payload: dict):

    exchange = payload['exchange']

    file = os.path.join(properties.EXCHANGE_DIRECTORY, exchange)
    config = mapConfig.map(file)

    init_var = {
        'subaccount_name': config.subaccount.name,
        'leverage': config.leverage,
        'risk': config.risk,
        'api_key': config.apikey,
        'api_secret': config.apisecret,
        'passphrase': config.passphrase
    }


    #Todo: make it generic
    exchange_api = None
    try:
        if exchange.upper() == 'BYBIT':
            exchange_api = ByBit(init_var)
        elif exchange.upper() == 'OKX':
            exchange_api = Okx(init_var)
    except Exception as e:
        logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
        return {
            "success": False,
            "error": str(e)
        }

    logbot.logs('>>> Exchange : {}'.format(exchange))
    logbot.logs('>>> Subaccount : {}'.format(subaccount_name))

    # FIND THE APPROPRIATE TICKER IN DICTIONNARY

    ticker = ""
    if exchange.upper() == 'BYBIT':
        ticker = payload['ticker']
    else:
        with open('../data/tickers.json') as json_file:
            tickers = json.load(json_file)
            try:
                ticker = tickers[exchange.lower()][payload['ticker']]
            except Exception as e:
                logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
                return {
                    "success": False,
                    "error": str(e)
                }
    logbot.logs(">>> Ticker '{}' found".format(ticker))

    #   ALERT MESSAGE CONDITIONS
    if payload['message'] == 'entry':
        logbot.logs(">>> Order message : 'entry'")
        orders = exchange_api.entry_position(payload, ticker)
        return orders

    elif payload['message'] == 'exit':
        logbot.logs(">>> Order message : 'exit'")
        exit_res = exchange_api.exit_position(payload, ticker)
        return exit_res

    else:
        logbot.logs(f">>> Order message : '{payload['message']}'")

    return {
        "message": payload['message']
    }
