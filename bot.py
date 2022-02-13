from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import settings


logging.basicConfig(filename='bot.log', format='%(asctime)s %(message)s', datefmt='%d-%b-%Y %H:%M', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {
        'username': settings.PROXY_USERNAME,
        'password': settings.PROXY_PASSWORD
    }
}


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info("Бот стартовал")

    mybot.start_polling()
    mybot.idle()


def greet_user(update, context):
    print('Вызван /start')
    print(f'user info: {update}')
    update.message.reply_text('Привет, пользователь! Ты вызвал команду /start')


def talk_to_me(update, context):
    user_text = update.message.text 
    print(f'Повторяю: {user_text}')
    update.message.reply_text(user_text)


if __name__ == "__main__":
    main()

       