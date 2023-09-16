from ..data import Config, AccountEnum, APIEnum


#Function that, take a class and map the attributes that we need
def map(apiFile) -> Config:
    try:
        with open(apiFile) as file:
            config_data = {}
            exec(file.read(), config_data)

        config = Config(
                passphrase=config_data.get(APIEnum.PASSPHRASE.value, None),
                apisecret=config_data.get(APIEnum.API_SECRET.value, None),
                apikey=config_data.get(APIEnum.API_KEY.value, None),
                subaccount = config_data.get(AccountEnum.SUBACCOUNT.value, None),
                leverage = config_data.get(AccountEnum.SUBACCOUNT.value, None),
                risk = config_data.get(AccountEnum.SUBACCOUNT.value, None)
            )

        return config

    except Exception as e:

        print(f"Error while mapping config exchange file {e}")



