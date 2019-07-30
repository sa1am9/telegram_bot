from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather
from datetime import date, timedelta, datetime
import schedule

token = ""
types = telebot.types
bot = telebot.TeleBot(token)
API_KEY = '57e88dda7e68e88594baa4b5cd091bf2'
darksky = DarkSky(API_KEY)
locate = [0, 0]
subs = open('subscribers', 'r').read()
subs = subs.replace("[", "")
subs = subs.replace(']', '')
subs = subs.replace("\"", '')
subs = subs.replace('\'', '')
subs = subs.replace('\\', '')
subs = subs.replace('n', '')
subs = list(subs.split(', '))
if subs == ['']:
    subs = list()
index = 0


def hourly(city):
    result = ''
    latitude = city[0]
    longitude = city[1]
    forecast = darksky.get_forecast(
        latitude, longitude,
        extend=False,  # default `False`
        lang=languages.UKRAINIAN,  # default `ENGLISH`
        units=units.AUTO,  # default `auto`
        exclude=[]  # default `[]`
    )
    for i in range(24):
        dnow = datetime.now()
        data = forecast.hourly.data[i]
        if (data.time.day > dnow.date().day) or (data.time.month > dnow.date().month) or (data.time.year > dnow.date().year):
            if data.time.hour != 0:
                break

        if data.time.hour >= dnow.hour:
            result += 'Час: ' + str(data.time.time().hour) + ':00\n' + data.summary + '\nтемпература: ' + str(data.temperature) + '\nвидима температура: ' + str(data.apparent_temperature) + '\n' + '-' * 50 + '\n'
    return (result)


def mailing(subs):
    print('working')
    for s in subs:
        bot.send_message(hourly([s[1], s[2]]))


def daily(city):
    result = ''
    latitude = city[0]
    longitude = city[1]
    forecast = darksky.get_forecast(
        latitude, longitude,
        extend=False,  # default `False`
        lang=languages.UKRAINIAN,  # default `ENGLISH`
        units=units.AUTO,  # default `auto`
        exclude=[]  # default `[]`
    )
    for i in range(7):
        data = forecast.daily.data[i]
        result += 'День: ' + str(data.time.strftime('%a')) + '\n' + data.summary + '\nмакcимальна температура: ' + str(data.temperature_high) + "C\nбуде о: " + str(data.temperature_high_time.hour) + ':00\nмінімальна температура: ' + str(data.temperature_low) + "С\nбуде о: " + str(data.temperature_low_time.hour) + ':00\n--------------------------------------------\n'
    return(result)


@bot.message_handler(commands=["geo", 'start'])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Відіслати мізце розташування", request_location=True)
    keyboard.add(button_geo)
    button_geo = types.KeyboardButton(text="Прогноз на день")
    keyboard.add(button_geo)
    button_geo = types.KeyboardButton(text="Прогноз на тиждень")
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, text='Відішліть геопозицію, будь ласка', reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        print(type(message.chat.id))
        if str(message.chat.id) in subs:
            indx = subs.index(str(message.chat.id))
            for i in range(3):
                subs.pop(indx)
        subs.append(str(message.chat.id))
        subs.append(str(message.location.latitude))
        subs.append(str(message.location.longitude))
        open('subscribers', 'w').write(str(subs))
        print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="На день", callback_data="test")
        keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text="На тиждень", callback_data="daily")
        keyboard.add(callback_button)
        bot.send_message(message.chat.id, "Натисни, щоб отримати прогноз погоди", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "test":
            bot.send_message(call.from_user.id, text=hourly(locate))
            try:
                bot.delete_message(call.from_user.id, call.message.message_id)
            except:
                pass
        if call.data == 'daily':
            bot.send_message(call.from_user.id, text=daily(locate))
            bot.delete_message(call.from_user.id, call.message.message_id)


@bot.message_handler(content_types=["text"])
def text(message):
    # Если сообщение из чата с ботом
    try:
        if message.text == 'Прогноз на день':
            bot.send_message(message.chat.id, text=hourly([subs[subs.index(str(message.chat.id))+1], subs[subs.index(str(message.chat.id))+2]]))
        if message.text == 'Прогноз на тиждень':
            bot.send_message(message.chat.id, text=daily([subs[subs.index(str(message.chat.id))+1], subs[subs.index(str(message.chat.id))+2]]))
    except:
        bot.send_message(message.chat.id, 'Спочатку відішліть геопозицію')


while 1:
    bot.polling(interval=2, none_stop=True, timeout=20)
