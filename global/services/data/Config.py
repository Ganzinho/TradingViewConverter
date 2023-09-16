from enum import Enum

class AccountEnum(Enum):
    SUBACCOUNT = "SUBACCOUNT"
    LEVERAGE = "LEVERAGE"
    RISK = "RISK"


class APIEnum(Enum):
    API_KEY = "API_KEY"
    API_SECRET = "API_SECRET"
    PASSPHRASE = "PASSPHRASE"

class Config:
    def __init__(self, apikey, apisecret, subaccount, leverage = None, risk = None, passphrase = None):
        self.subaccount = subaccount
        self.leverage = leverage
        self.risk = risk
        self.apikey = apikey
        self.apisecret = apisecret
        self.passphrase = passphrase