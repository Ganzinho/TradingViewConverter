import requests, config, os

DISCORD_LOGS_URL = os.environ.get('DISCORD_LOGS_URL', config.DISCORD_LOGS_URL)

DISCORD_ERR_URL = os.environ.get('DISCORD_ERR_URL', config.DISCORD_ERR_URL)

DISCORD_AVATAR_URL = os.environ.get('DISCORD_AVATAR_URL', config.DISCORD_AVATAR_URL)

DISCORD_STUDY_URL = os.environ.get('DISCORD_STUDY_URL', config.DISCORD_STUDY_URL)

DISCORD_STUDY_AVATAR_URL = os.environ.get('DISCORD_STUDY_AVATAR_URL', config.DISCORD_STUDY_AVATAR_URL)

TOKEN = "INSERT_YOUR_TELEGRAM_TOKEN"

CHAT_ID = "995013600"

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

paramsTelegram = {
                "chat_id": CHAT_ID,
                "text": ""
                }

logs_format = {
	"username": "logs",
	"avatar_url": DISCORD_AVATAR_URL,
	"content": ""
}

study_format = {
	"username": "Tradingview Alert",
	"avatar_url": DISCORD_STUDY_AVATAR_URL,
	"content": ""
}

def logs(message, error=False, log_to_discord=True):
    print(message)
    if log_to_discord:
        try:
            json_logs = logs_format
            json_logs['content'] = message
            requests.post(DISCORD_LOGS_URL, json=json_logs)
            if error:
                requests.post(DISCORD_ERR_URL, json=json_logs)
        except:
            pass


def telegramlogs(message):
    
    print(message)
    
    try:
        json_logs = paramsTelegram
        json_logs['text'] = message
        
        r = requests.post(TELEGRAM_API, params = json_logs)
        
        print(r)
        
    except:
        print(Exception)
