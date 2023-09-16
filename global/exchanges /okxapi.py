import logbot
import hmac
import hashlib
import base64
from requests import Request, Session, Response
from datetime import datetime


class Okx():
    def __init__(self, var: dict):
        self.ENDPOINT = 'https://www.okx.com/'
        self.session = Session()
        
        self.subaccount_name = var['subaccount_name']
        self.leverage = var['leverage']
        self.risk = var['risk']
        self.api_key = var['api_key']
        self.api_secret = var['api_secret']
        self.passphrase = var['passphrase']
        
    # =============== SIGN, POST AND REQUEST ===============

    def _request(self, method: str, path: str, **kwargs):
        request = Request(method, self.ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self.session.send(request.prepare())
        print(self._proccess_response(response))
        return self._proccess_response(response)
    
    def _sign_request(self, request: Request):
        
        #compute timestamp
        current_timestamp = datetime.utcnow()
        ts = current_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        #prepare payload
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode('utf-8')
        if prepared.body:
            signature_payload += prepared.body
         
        #prepare signature   
        hashed = hmac.new(self.api_secret.encode('utf-8'), signature_payload, hashlib.sha256)
        signature = base64.b64encode(hashed.digest()).decode()

        #add headers
        request.headers['OK-ACCESS-KEY'] = self.api_key
        request.headers['OK-ACCESS-SIGN'] = signature
        request.headers['OK-ACCESS-TIMESTAMP'] = ts
        request.headers['OK-ACCESS-PASSPHRASE'] = self.passphrase
        
        if self.subaccount_name:
            request.headers['OKX-SUBACCOUNT'] = self.subaccount_name
            
    def _proccess_response(self, response: Response):
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            return data
        
    def _try_request(self, method: str, path: str, params = None, body=None):
        try:
            if params or body:
                req = self._request(method, path, params = params, json=body)
            else:
                req = self._request(method, path)
        except Exception as e:
            logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
            return {
                "success": False,
                "error": str(e)[1:-1]
            }
        if not req['code']:
            logbot.logs('>>> /!\ {}'.format(req['error']), True)
            return {
                    "success": False,
                    "error": req['error']
                }
        else: 
            req['success'] = True
            
        return req
    
    
# ================= ORDERS ======================

    def entry_position(self, payload: dict, ticker):
        
        orders = []
        
        side = 'buy'
        if payload['action'] == 'sell':
            side = 'sell'
            
        tdMode = payload['tdMode']
        posSide = payload['posSide']
        stopLoss = payload["stopLoss"]
        takeProfit = payload["takeProfit"]
        trailingstop = payload['trailing_stop']
        
            
        #open the trailingstop

        if 'type' in payload.keys():
            order_type = payload['type'] #market or limit
        else:
            order_type = 'market' #default
        
        if order_type != 'market' and order_type != 'limit':
                return {
                        "success" : False,
                        "error" : f"order type '{order_type}' is unknown"
                    }
    # 0/ get the size
        params = {
            "instId": ticker,
            "tdMode": tdMode
        }
        print(params)
        r = self._try_request('GET', 'api/v5/account/max-size', params)
        
        size = 0
        if side == 'buy':
            size = r['data'][0]['maxBuy']
        else:
            size = r['data'][0]['maxSell']
        logbot.logs('>>> Max size buy : {}'.format(size))
        
        exe_price = None if order_type == "market" else payload['price']
        order_payload = {
                "instId": ticker,
                "tdMode": tdMode,
                "side": side,
                "posSide": posSide,
                "ordType": order_type,
                "slTriggerPx": stopLoss,
                "slOrdPx": "-1",
                "tpTriggerPx": takeProfit,
                "tpOrdPx": "-1",
                "px": exe_price,
                "sz": size
            }
    
        r = self._try_request('POST', 'api/v5/trade/order', body = order_payload)

        
        logbot.logs(f">>> Order {order_type} posted with success. \n"
                    "Amount: {size} \n"
                    "Pair: {ticker} \n"
                    "Price: {exe_price}")
        
        # Add trailing Stop 
        if trailingstop == 'true':
            
            trailingstop_value = payload['trailing%']
            
            self.trailig_order(payload, ticker, size, trailingstop_value)
            
        if r['code'] != 0:
            logbot.logs(f">>> Order not executed. Check logs: {r}") #can be improved. Add the message returned by Okx
            r['orders'] = orders
            return r
        
        orders.append(r['result'])
        return {
            "success": True,
            "orders": orders
        }
        
    def trailig_order(self, payload: dict, ticker, size, trailingstop):
        
        orders = []
        side = 'buy'
        if payload['action'] == 'sell':
            side = 'buy'
        else:
            side = 'sell'
            
        tdMode = payload['tdMode']
        posSide = payload['posSide']
       
        order_payload = {
                "instId": ticker,
                "tdMode": tdMode,
                "side":side,
                "posSide": posSide,
                "ordType":"move_order_stop",
                "sz":size,
                "callbackRatio":trailingstop,
            }

        r = self._try_request('POST', 'api/v5/trade/order-algo', body = order_payload)
        
        logbot.logs(f">>> TrailingStop setted: {trailingstop}%")
        
        if r['code'] != 0:
            r['orders'] = orders
            logbot.logs(f">>> Order not executed. Check logs: {r}") #can be improved. Add the message returned by Okx
            return r
        orders.append(r['result'])
        logbot.logs(f">>> TrailingStop setted: {trailingstop}%")
        
        return {
            "success": True,
            "orders": orders
        }
        
    # Exit Order
    def exit_position(self, payload: dict, ticker):
         
        orders = []
            
        mgnMode = payload['tdMode']
        posSide = payload['posSide']
        
        # Get the last order position Side
        if posSide == 'flat':
            posSide = payload['pre_posSide']
        
        close_order_payload = {
            "instId": ticker,
            "mgnMode": mgnMode,
            "posSide": posSide
            
        }
    
        r = self._try_request('POST', "api/v5/trade/close-position", body = close_order_payload) 
        
        if r['code'] != 0:
            r['orders'] = orders
            return r
        orders.append(r['result'])
        
        logbot.logs(f">>> A {posSide} Order is closed with success.")
        
        
        return {
            "success": True,
            "orders": orders
        }
           
        
        
        
        
    
        