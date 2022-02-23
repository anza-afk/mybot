import telegram
import logging
import settings
import ephem
from datetime import date, datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from difflib import get_close_matches

from csv_to_list import get_city_list, get_random_city

logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s %(message)s',
    datefmt='%d-%b-%Y %H:%M',
    level=logging.INFO
)

planets_list = [p for _0, _1, p in ephem._libastro.builtin_planets()]
cities_lst = []

PROXY = {
    'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {
        'username': settings.PROXY_USERNAME,
        'password': settings.PROXY_PASSWORD,
    },
}
CITIES = get_city_list('city.csv')
GAME_STATE = {}


def main():
    """Main fuction."""
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', constel_planet, pass_args=True))
    dp.add_handler(CommandHandler('wordcount', game_wordcount, pass_args=True))
    dp.add_handler(CommandHandler('next_full_moon', next_moon_date, pass_args=True))
    dp.add_handler(CommandHandler('cities', game_cities, pass_args=True))
    dp.add_handler(CommandHandler('calc', calculator, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Beep! Beep! Bot activated!')

    mybot.start_polling()
    mybot.idle()


def greet_user(update: telegram.Update, context) -> None:
    """Reaction to '/start' command."""
    if update.message and update.message.text:
        logging.info('Used /start')
        logging.info(f'user info: {update}')
        update.message.reply_text('Hello, user! You used the /start command.')


def calculator (update: telegram.Update, context) -> None:
    """Simple calc."""
    if update.message and update.message.text:
        user_expression = update.message.text.replace('/calc', '').strip()
        try:
            res = eval(user_expression)
        except ZeroDivisionError:
            res = 'На 0 делить нельзя.'
        update.message.reply_text(res)


def constel_planet(update: telegram.Update, context) -> None:
    if update.message and update.message.text:
        rough_text = update.message.text.split()[1].capitalize()
        if rough_text in planets_list:
            planet = ephem.__dict__[rough_text]
            planet_cons = ephem.constellation(planet(date.today()))
            logging.info(
                f"Return constellations for {rough_text} for ({date.today()})"
            )
            update.message.reply_text(
                f'{rough_text} in {planet_cons[0]},{planet_cons[1]} today',
            )
        else:
            update.message.reply_text(
                f'"{rough_text}" does not belong to the celestial bodies known to me. Check if the input is correct.',  # noqa: E501 long answer to user
            )
            cm = get_close_matches(rough_text, planets_list)
            if len(cm) > 0:
                update.message.reply_text(
                    f'Perhaps you meant "/planet {cm[0]}"?',
                )


def next_moon_date(update: telegram.Update, context) -> None:
    if update.message and update.message.text:
        if update.message.text.replace('/next_full_moon', '').strip():
            rough_date = update.message.text.replace('/next_full_moon ', '')
            in_date = ''
            for symbol in rough_date:
                if symbol.isnumeric():
                    in_date += symbol
                else:
                    in_date += '-'
            while '--' in in_date:
                in_date = in_date.replace('--', '-')
            in_date = datetime.strptime(in_date, '%d-%m-%Y')
        else:
            in_date = date.today()
        update.message.reply_text(ephem.next_full_moon(in_date))


def game_cities(update: telegram.Update, context) -> None:
    """Game 'cities' main function."""
    user_id = update['message']['chat']['id']
    if update.message and update.message.text:
        if user_id not in GAME_STATE:
            GAME_STATE[user_id] = CITIES.copy()
        user_city = update.message.text.split()[1].lower()
        if user_city not in GAME_STATE[user_id]:
            update.message.reply_text(f'{user_city} уже был, либо я его не знаю.')
        else:
            GAME_STATE[user_id].remove(user_city)
            bot_city = get_random_city(CITIES, user_city[-1].lower())
            update.message.reply_text(f'{bot_city}, Ваш ход.')
            GAME_STATE[user_id].remove(bot_city)


def game_wordcount(update: telegram.Update, context) -> None:
    """Word count function."""
    if update.message and update.message.text:
        if len(update.message.text.split()) > 1:
            count_words = len(update.message.text.split()[1:])
            wr = 'word' if count_words == 1 else 'words'
            logging.info(f'Returning {count_words}')
            update.message.reply_text(f'{count_words} {wr}.')
        elif len(update.message.text.split()) == 1:
            update.message.reply_text('Do you forgot to add any words?')


def talk_to_me(update: telegram.Update, context) -> None:
    """Parrot function."""
    if update.message and update.message.text:
        user_text = update.message.text
        logging.debug(f'Repeating: {user_text}')
        update.message.reply_text(user_text)


if __name__ == '__main__':
    main()
