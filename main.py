# TODO: especificar cada except.
# TODO: especificar cada import explicitamente
# TODO: analisar e modular rotinas repetidas.
# TODO: estatístisticas de uso de cada componente.
# TODO: feedback para caso de erros.
# TODO: melhoria e otimização de funções

# TODO: Implementação do parser de arquivos .eml (e-mail), integrando outras funções de inteligência, como blacklist
# TODO: Implementação do envio de gráficos do dnsdumpster
# TODO: Implementação da checagem de blacklist em IPs/Domains
# TODO: (Possível) Implementação da checagem de artefatos via VT
# TODO: Implementação da função de baixar samples via bazaar/malshare (NECESSÁRIO API!!!)
# TODO: inclusão da googlesearch para pesquisa em redes sociais, pastes e leaks
# TODO: pesquisa de links da deepweb
# TODO: cálculo dos dígitos verificadores cpf
# TODO: implementação pesquisa webhosting

# TODO: Melhorar saída do GEO-IP
# TODO: incluir cpf, subdomain e geoip nas opções de menu para o usuário

import telegram.ext
import logging
import whois
import datetime
import socket
import cpf
import os
import json
import pydnsbl
import ipaddress

from ipdb import set_trace

from dnsdumpster.DNSDumpsterAPI import DNSDumpsterAPI
from geolite2 import geolite2
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys


#logging.basicConfig(filename='log_intelmultibot.log', filemode='a', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)
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

comands_and_desc = {
    'help': 'show this help',
    'whois': 'gather information about a domain',
    'check_email': 'checks the validity of an e-mail address',   
}

help_msg = """
Hello, I am a bot that travels around the cyberworld and give you some Intelligence about something in the Internet!

====================================
List of commands:
====================================
"""

for k in comands_and_desc.keys():
    help_msg += "/{} - {}\n".format(k, comands_and_desc[k])

help_msg += "===================================="


# BUG: não consegue manipular dois objetos que tenham uma mesma propriedade em comum
def log_this(log_func, msg, attrs={}, callback=None):
    if type(attrs) is not dict:
        attrs = dict()
    log_msg = msg + ' | '
    info_dict = dict()

    for obj in attrs.keys():
        temp_dict = dict()
        if type(attrs[obj]) is list:
            for attr in attrs[obj]:
                temp_dict[attr] = getattr(obj, attr, None)
        else:
            temp_dict[attrs[obj]] = getattr(obj, attrs[obj], None)

        info_dict[type(obj).__name__] = temp_dict

    log_msg += str(info_dict) + '\n'
    log_func(log_msg)


def start(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=help_msg)
    log_this(logging.info, 'New user',
             {
                 update.effective_user: ['name', 'id', 'link']
             })


def help(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=help_msg)


def c_whois(update, context):
    log_this(logging.info, 'Whois command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    try:
        domain = context.args[0]
    except IndexError:
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
    log_this(logging.info, 'check_email command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    try:
        email = context.args[0]
    except IndexError:
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

    #TODO: melhorar a rotina abaixo, de aguardar o carregamento total da página
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
                                text='Connection to domain *{}* failed. Possibly the e-mail is not valid.'.format(
                                    email.split('@')[1]),
                                parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='An unknown error happened.',
                                parse_mode=telegram.ParseMode.MARKDOWN)


def c_check_cpf(update, context):
    log_this(logging.info, 'check_cpf command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    try:
        cpf_sent = context.args[0]
    except IndexError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide an cpf in format : 12345678901 or 123.456.789-01.')
        return

    info_cpf = cpf.checa_cpf(cpf_sent)
    if info_cpf is None:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='CPF is not valid. (not? please check the syntax and 0\'s)')
    else:
        msg = f'Valid CPF.\n{info_cpf[1][0]}º Região Fiscal\nPossíveis estados de emissão: {info_cpf[1][1]}'
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=msg)

    return

def c_subdomains(update, context):
    log_this(logging.info, 'subdomains command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    try:
        domain = context.args[0]
    except IndexError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide a domain.')
        return

    context.bot.sendMessage(chat_id=update.effective_chat.id, text='Wait a few seconds...')
    results = DNSDumpsterAPI().search(domain)

    if len(results) == 0:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=f'Results not found for {domain}')
        return

    json_results = json.dumps(results['dns_records'], sort_keys=True, indent=4)

    with open(f'results_{domain}_{update.effective_chat.id}.txt', 'w') as f:
        f.write(json_results)

    context.bot.send_document(chat_id=update.effective_chat.id, document=open(f'results_{domain}_{update.effective_chat.id}.txt', 'rb'), filename=f'results_{domain}.txt')
    os.remove(f'results_{domain}_{update.effective_chat.id}.txt')


def c_geoip(update, context):
    log_this(logging.info, 'geoip command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    try:
        ip_sent = context.args[0]
        ipaddress.IPv4Address(ip_sent)
    except ipaddress.AddressValueError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide an IP address.')
        return

    reader = geolite2.reader()
    results = reader.get(ip_sent)

    if results is None:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='No GEO-IP information found in my database :(')
        return

    results_formatted = ''

    #results_formatted = json.dumps(results, indent=4)
    if results.get('continent'):
        results_formatted += 'Continent: '
        results_formatted += str(results['continent']['code']) + ' - '
        results_formatted += str(results['continent']['names']['en']) + '\n'
    if results.get('country'):
        results_formatted += 'Country: '
        results_formatted += str(results['country']['iso_code']) + ' - '
        results_formatted += str(results['country']['names']['en']) + '\n'
    if results.get('subdivisions'):
        results_formatted += 'State/Province: '
        results_formatted += str(results['subdivisions'][0]['iso_code']) + ' - '
        results_formatted += str(results['subdivisions'][0]['names']['en']) + '\n'
    if results.get('city'):
        results_formatted += 'City: '
        results_formatted += str(results['city']['names']['en']) + '\n'
    if results.get('postal'):
        results_formatted += 'Postal: '
        results_formatted += str(results['postal']['code']) + '\n'

    if results.get('location', None):
        if results['location'].get('time_zone'):
            results_formatted += "Timezone: "
            results_formatted += results['location']['time_zone'] + '\n'
        results_formatted += "\n==================================\n"
        results_formatted += f"https://maps.google.com/?q={results['location']['latitude']},{results['location']['longitude']}"


    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=results_formatted)


def c_check_blacklist(update, context):
    checker = None
    log_this(logging.info, 'check_blacklist command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    
    try:
        domain_or_ip = context.args[0]
        ipaddress.IPv4Address(domain_or_ip)
        checker = pydnsbl.DNSBLIpChecker()
    except ipaddress.AddressValueError:
        checker = pydnsbl.DNSBLDomainChecker()
    except IndexError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide a domain/IP address.')
        return

    context.bot.sendMessage(chat_id=update.effective_chat.id, text='Wait a few seconds...')
    
    try:
        results = checker.check(domain_or_ip)
    except ValueError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide a domain/IP address.')
        return
    
    if not results.blacklisted:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=f'{results.addr} is not blacklisted in any {len(results.providers)} providers.')
        return
    
    text = f"{results.addr} is blacklisted in {len(results.detected_by)}/{len(results.providers)} providers.\n"
    text += "\nDETECTED BY: REASON\n======================\n"
    
    for prov in results.detected_by.keys():
        text += prov + " : " + ",".join(results.detected_by[prov]) + "\n"

    context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=text)

    return

def c_get_digits(update, context):
    log_this(logging.info, 'get_digits command triggered',
             {
                 update.effective_user: ['name', 'id', 'link'],
                 update.message: ['text']
             })
    try:
        cpf_sent = context.args[0]
    except ipaddress.AddressValueError:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide a cpf without the verification digits.')
        return

    digits = cpf.digit_verifier(cpf_sent)
    if digits is None:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text='You must provide a cpf without the verification digits.')
        return
        
    cpf_sent = cpf.formata_cpf(cpf_sent)
    cpf_sent = cpf_sent * 100 + digits

    text = 'The verification numbers are {:02}'.format(digits)
    text += '\nCPF: {:011}'.format(cpf_sent)

    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=text)


# ------------------------------------- ERRORS HANDLES --------------------------------------------------- #

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    log_this(logging.warning, 'An unknown command has been passed to bot', {
        update.effective_user: ['name', 'id', 'link'],
        update.message: ['text']
    })

def error_callback(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text='An unexpected error occurred.')
    
    try:
        raise context.error
    except Exception as e:
        log_this(logging.error, 'Exception not handled => {}: {}'.format(type(e).__name__, e), {
            update.effective_user: ['name', 'id', 'link'],
            update.message: ['text']
        })

# --------------------------------- HANDLES E DISPATCHERS ---------------------------------------------- #

start_handle = telegram.ext.CommandHandler('start', start)
help_handle = telegram.ext.CommandHandler('help', help)
whois_handle = telegram.ext.CommandHandler('whois', c_whois)
check_email_handle = telegram.ext.CommandHandler('check_email', c_check_email)
check_cpf_handle = telegram.ext.CommandHandler('check_cpf', c_check_cpf)
check_subdomains = telegram.ext.CommandHandler('subdomains', c_subdomains)
geoip_handle = telegram.ext.CommandHandler('geoip', c_geoip)
check_blacklist = telegram.ext.CommandHandler('check_bl', c_check_blacklist)
get_digits = telegram.ext.CommandHandler('get_digits', c_get_digits)
unknown_handler = telegram.ext.MessageHandler(telegram.ext.Filters.command, unknown)

dispatcher.add_handler(start_handle)
dispatcher.add_handler(help_handle)
dispatcher.add_handler(whois_handle)
dispatcher.add_handler(check_email_handle)
dispatcher.add_handler(check_cpf_handle)
dispatcher.add_handler(check_subdomains)
dispatcher.add_handler(geoip_handle)
dispatcher.add_handler(check_blacklist)
dispatcher.add_handler(get_digits)
dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
