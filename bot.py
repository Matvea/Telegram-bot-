import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types 

user_states = {}

bot = telebot.TeleBot(token='6782250498:AAE2YNwVrF_ZFKZOw5SC48V-f1t3E9bbHkY')  

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message)

def show_main_menu(message, is_start=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cryptocurrency_prices = types.KeyboardButton("Цены криптовалют 💸")
    cryptocurrency_news = types.KeyboardButton("Новости криптовалют 🗞")
    markup.add(cryptocurrency_prices, cryptocurrency_news)

    if is_start:
        bot.send_message(message.chat.id, text="Привет, {0.first_name}!".format(message.from_user), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="Выберите действие", reply_markup=markup)

# Обработчик нажатия на кнопку "Цены криптовалют"
@bot.message_handler(func=lambda message: message.text == "Цены криптовалют 💸")
def handle_price_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    currency_buttons = ['RUB', 'USD']
    for currency in currency_buttons:
        markup.add(types.KeyboardButton(currency))
    back = types.KeyboardButton("Назад")
    markup.add(back)
    bot.send_message(message.chat.id, text="Выберите валюту, в которой хотите узнать цену криптовалюты", reply_markup=markup)

# Обработчик выбора валюты
@bot.message_handler(func=lambda message: message.text in ['RUB', 'USD'])
def handle_currency_button(message):
    currency = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    crypto_buttons = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'TON']
    for crypto in crypto_buttons:
        markup.add(types.KeyboardButton(crypto))
    back = types.KeyboardButton("Назад")
    markup.add(back)
    bot.send_message(message.chat.id, text="Выберите криптовалюту", reply_markup=markup)

    bot.register_next_step_handler(message, lambda m: handle_crypto_selection(m, currency))

def handle_crypto_selection(message, currency):
    if message.text == "Назад":
        handle_price_button(message) 
        return

    crypto = message.text
    price = get_crypto_price(currency, crypto)
    response_text = f"Цена криптовалюты {crypto} в валюте {currency}: {price}"
    bot.send_message(message.chat.id, text=response_text)

    show_main_menu(message, is_start=False)


# Функция для получения цены криптовалюты в выбранной валюте
def get_crypto_price(currency, crypto):
    url = f"https://crypto.ru/{crypto}-{currency}/"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find('div', class_="coin__aside") 
        if price_element:
            return price_element.text.strip()
        else:
            return "Цена не найдена"
    except requests.exceptions.RequestException as e:
        return f"Ошибка при получении данных: {e}"

# Обработчик нажатия на кнопку "Новости криптовалют"
@bot.message_handler(func=lambda message: message.text == "Новости криптовалют 🗞")
def handle_news_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    crypto_buttons = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'TON']
    for crypto in crypto_buttons:
        markup.add(types.KeyboardButton(crypto))
    back = types.KeyboardButton("Назад")
    markup.add(back)
    bot.send_message(message.chat.id, text="Выберите криптовалюту, о которой хотите узнать новость", reply_markup=markup)

    bot.register_next_step_handler(message, handle_news_selection)

def handle_news_selection(message):
    if message.text == "Назад":
        show_main_menu(message, is_start=False) 
        return

    crypto = message.text 
    news_list = get_crypto_news(crypto)

    if news_list:
        response_text = f"Новости для {crypto}:\n"
        for title, link in news_list:
            response_text += f"{title}\n{link}\n"
        bot.send_message(message.chat.id, text=response_text)
    else:
        bot.send_message(message.chat.id, text="Новости не найдены.")

    show_main_menu(message, is_start=False)

# Функция для получения новости криптовалюты
def get_crypto_news(crypto):
    url = f"https://ru.investing.com/search/?tab=news&q={crypto}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_elements = soup.find_all("div", class_="articleItem") 
        news_list = []

        for news in news_elements[:3]: 
            title_element = news.find("a", class_="title")  
            if title_element:
                title = title_element.text.strip()
                link = title_element['href']  
                if not link.startswith('http'):
                    link = f"https://ru.investing.com{link}" 
                news_list.append((title, link))

        return news_list if news_list else []  

    except requests.exceptions.RequestException as e:
        return f"Ошибка при получении данных: {e}"

# Обработчик нажатия на кнопку "Назад"
@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back_button(message):
    show_main_menu(message, is_start=False)

# Запуск бота
bot.polling(none_stop=True)
