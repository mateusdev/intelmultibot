# TODO: especificar cada except.
# TODO: analisar e modular rotinas repetidas.
# TODO: implementar logging.
# TODO: estatístisticas de uso de cada componente.
# TODO: função de log genérica. (permitir a utilização de a = b if b is not None else c)

import telegram.ext
import logging
import whois
import datetime
import socket
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)
logging.info('Starting the process...')

# -------------------------- FOR SELENIUM ----------------------------------- #
options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)
# --------------------------------------------------------------------------- #

logging.info('Process started!')

token = '1104333045:AAFYKy78IaEMmTr3jMhTOfsFIde-U_BRJ_E'

bot = telegram.Bot(token=token)
updater = telegram.ext.Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

help_msg = """
Hello, I am a bot that travels around the cyberworld and give you some Intelligence about something in the Internet!

====================================
List of commands:
====================================
/help - show this help
/whois <domain> - gather information about a domain
/check_email <email> - checks the validity of an e-mail address
====================================
"""

def start(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=help_msg)
    logging.info('user: {} id: {} link: {} - has started the bot.'.format(
        update.effective_user.name,
        update.effective_user.id,
        update.effective_user.link
    ))

def help(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=help_msg)

def c_whois(update, context):
    try:
        domain = context.args[0]
    except:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide a domain.')
        return
    context.bot.sendMessage(chat_id=update.effective_chat.id, text='Wait a few seconds...')

    try:
        w = whois.whois(domain)
        info_dict = dict(w)
    except whois.parser.PywhoisError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='*Error:* domain *{}* not found'.format(context.args[0]),
                                parse_mode=telegram.ParseMode.MARKDOWN)
        return
    except socket.timeout:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='Error: a timeout has occurred')
        return

    reply = ''
    for k in info_dict.keys():
        if info_dict[k] is not None:
            reply += '<b><u>{}</u></b> : \n'.format(k)
            type_info = type(info_dict[k])

            if type_info is list:
                for info in info_dict[k]:
                    if type(info) is datetime.datetime:
                        reply += '{}\n'.format(info.strftime('%m/%d/%Y, %H:%M:%S'))
                    else:
                        reply += '{}\n'.format(str(info))

            elif type_info is datetime.datetime:
                reply += '{}\n'.format(info_dict[k].strftime('%m/%d/%Y, %H:%M:%S'))
            else:
                reply += '{}\n'.format(str(info_dict[k]))

    if reply == '':
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='*Error:* domain *{}* not found'.format(context.args[0]),
                                parse_mode=telegram.ParseMode.MARKDOWN)
        return

    context.bot.sendMessage(chat_id=update.effective_chat.id, text=reply, parse_mode=telegram.ParseMode.HTML)

def c_check_email(update, context):
    try:
        email = context.args[0]
    except:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide an e-mail address.')
        return

    context.bot.sendMessage(chat_id=update.effective_chat.id, text='Wait a few seconds...')

    global browser
    browser.get('https://validateemailaddress.org/')

    try:
        bt = browser.find_element_by_id('accept')
        bt.click()
    except:
        pass

    text_field = browser.find_element_by_name('email')
    text_field.clear()
    text_field.send_keys(email)
    text_field.send_keys(Keys.RETURN)

    response = None
    while not response:
        try:
            response = browser.find_element_by_xpath("//tbody/tr[2]/td/div[last()]").text
        except:
            browser.implicitly_wait(1)

    if 'Syntax is not correct' in response:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='E-mail syntax is incorrect: *{}*'.format(email),
                                parse_mode=telegram.ParseMode.MARKDOWN)
    elif 'No MX' in response:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='MX records of *{}* not found.'.format(email.split('@')[1]),
                                parse_mode=telegram.ParseMode.MARKDOWN)
    elif 'is not valid' in response:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='E-mail *{}* is not valid.'.format(email),
                                parse_mode=telegram.ParseMode.MARKDOWN)
    elif 'is valid' in response:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='E-mail *{}* is valid.'.format(email),
                                parse_mode=telegram.ParseMode.MARKDOWN)
    elif 'Connecting to' in response:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='Connection to domain *{}* failed. Possibly the e-mail is not valid.'.format(email.split('@')[1]),
                                parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='An unknown error happened.',
                                parse_mode=telegram.ParseMode.MARKDOWN)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    logging.info('user: {} id: {} link: {} - has typed an unknown command to bot: {}'.format(
        update.effective_user.name,
        update.effective_user.id,
        update.effective_user.link,
        update.message.text
    ))

# --------------------------------- HANDLES E DISPATCHERS ---------------------------------------------- #

start_handle = telegram.ext.CommandHandler('start', start)
help_handle = telegram.ext.CommandHandler('help', help)
whois_handle = telegram.ext.CommandHandler('whois', c_whois)
check_email_handle = telegram.ext.CommandHandler('check_email', c_check_email)
unknown_handler = telegram.ext.MessageHandler(telegram.ext.Filters.command, unknown)

dispatcher.add_handler(start_handle)
dispatcher.add_handler(help_handle)
dispatcher.add_handler(whois_handle)
dispatcher.add_handler(check_email_handle)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
