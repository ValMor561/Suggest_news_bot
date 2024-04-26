import configparser
from distutils.util import strtobool

#Чтение конфигурационного файла
def get_config(filename):
    config = configparser.ConfigParser()
    config.read(filename, encoding="utf-8")

    return config

config = get_config('config.ini')

#Глобальные переменные всех параметров
BOT_TOKEN = config['DEFAULT']['bot_token']
CHANELL_ID = config['DEFAULT']['channel_id']
ADMINS_CHANNEL = config['DEFAULT']['admins_channel']
FOOTER_TEXT = config['POST']['footer_text']
FOOTER_LINK = config['POST']['footer_link']
HOST=config['BD']['host']
DATABASE=config['BD']['database']
USER=config['BD']['user']
PASSWORD=config['BD']['password']
