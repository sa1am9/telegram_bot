from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather
from datetime import date, timedelta, datetime
import telebot
subs = open('subscribers', 'r').read()
subs = subs.replace("[", "")
subs = subs.replace(']', '')
subs = subs.replace("\"", '')
subs = subs.replace('\'', '')
subs = list(subs.split(', '))
API_KEY = '57e88dda7e68e88594baa4b5cd091bf2'
darksky = DarkSky(API_KEY)
if subs == ['']:
    subs = list()
token = ""
bot = telebot.TeleBot(token)


def hourly(latitude, longitude):
    result = ''
    forecast = darksky.get_forecast(
        latitude, longitude,
        extend=False,  # default `False`
        lang=languages.UKRAINIAN,  # default `ENGLISH`
        units=units.AUTO,  # default `auto`
        exclude=[weather.MINUTELY, weather.ALERTS]  # default `[]`
    )
    for _ in range(24):
        dnow = datetime.now()
        data = forecast.hourly.data[i]
        if (data.time.day > dnow.date().day) or (data.time.month > dnow.date().month) or (data.time.year > dnow.date().year):
            if data.time.hour != 0:
                break
        result += 'Час: ' + str(data.time.time().hour) + ":00\n" + data.summary + "\nтемпература: " + str(data.temperature) + '\nвидима температура: ' + str(data.apparent_temperature) + '\n---------------------\n'
    return(result)


for i in range(int(len(subs)/3)):
        bot.send_message(int(subs[i*3]), text=hourly(float(i*3+1),float(i*3+2)))
