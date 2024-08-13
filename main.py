import telebot
from telebot import types
from config import token
import sqlite3

# Подключение к базе данных с клиентами
db = sqlite3.connect("database.db", check_same_thread=False)

# Иницилизация базы данных и создание таблицы Users
cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
                name TEXT,
                adress TEXT,
                amount TEXT,
                big_cash INTEGER,
                cash INTEGER
    )
''')

# Иницилизыция телеграм бота
bot = telebot.TeleBot(token)

# Обработчик команды Start
@bot.message_handler(commands=['start'])


# Создание функции с начальными кнопкаим и отправкой приветствия
def Start(message):

    # Подключение клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    new_customer = types.KeyboardButton(text='новый заказчик')
    customer = types.KeyboardButton(text='старый заказчик')
    markup.add(new_customer, customer)
    
    bot.send_message(message.chat.id, text='привет, это бот который поможет тебе вспомнить прайс по работе.', reply_markup=markup)

    # Переход к функции Customer_input с ожиданием сообщения от пользователя
    bot.register_next_step_handler(message, Customer_Input) 


# Создание функции с обработчиком клавиатуры из функции Start
def Customer_Input(message):

    if message.text == 'новый заказчик' or message.text == 'заполнить заново' or message.text == 'редактировать':
        bot.send_message(message.chat.id, text='введите как зовут заказчика')
        bot.register_next_step_handler(message, Adress)

    elif message.text == 'старый заказчик':
        bot.send_message(message.chat.id, text='введите адрес или имя вашего заказчика')
        bot.register_next_step_handler(message, Old_Customer)

    else:
        bot.send_message(message.chat.id, text='пожалуйста воспользуйтесь кнопками')

        # Переход к Функции Old_Customer без ожидания сообщения от пользователя 
        Old_Customer(message)


# Создание функции с действиями происходящими после нажатия кнопки "Старый заказчик" на клавиатуре из команды Start
def Old_Customer(message):

    # Выбор нужной анкеты заказчика в базе данных
    cursor.execute('SELECT * FROM Users WHERE name=? OR adress=?', (message.text, message.text))
    user = cursor.fetchone()

    # Создание клавиатуры после выбора необходимой анкеты в базе данных
    if user:
        name, adress, amount, big_cash, cash = user

        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        backup = types.KeyboardButton(text='вернуться в главное меню')
        delit = types.KeyboardButton(text='удалить анкету')
        change = types.KeyboardButton(text ='заполнить заново')
        markup1.add(backup, delit, change)
        
        # Отправка данных о заказчике 
        bot.send_message(message.chat.id, text=f'информация о заказчике:\nимя - {name}\nадрес - {adress}\nобъем работы - {amount}\nприбыль с учетом чаевых - {big_cash}\nприбыль - {cash}', reply_markup=markup1)
        bot.register_next_step_handler(message, Old_Customer_menu)

    else:
        bot.send_message(message.chat.id, text='К сожалению, заказчика с таким именем или адресом не найдено. Попробуйте еще раз.')

        # Переход к фукции Start без ожидания сообщения от пользователя
        Start(message)


# Создание функции с обработчиком клавиатуры из функции Old_Customer
def Old_Customer_menu(message):

    if message.text == 'вернуться в главное меню':
        # Переход к фукции Start без ожидания сообщения от пользователя
        Start(message)

    elif message.text == 'удалить анкету':

        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes = types.KeyboardButton(text='да')
        no = types.KeyboardButton(text='нет')
        markup1.add(yes, no)

        bot.send_message(message.chat.id, text = 'вы точно хотите удалить заказчка?', reply_markup=markup1)

        # Переход к функции True_Delite с ожиданием сообщения от пользователя
        bot.register_next_step_handler(message, True_Delite)

    elif message.text == 'заполнить заново':
        cursor.execute('DELETE from Users WHERE name = name')

        # Переход к фукции Customer_Input без ожидания сообщения от пользователя
        Customer_Input(message)


# Создание функции с обработчиком клавиатуры из функции Old_Customer_menu
def True_Delite(message):

    if message.text == 'да':
        bot.send_message(message.chat.id, text = 'анкета удалена')
        cursor.execute('DELETE from Users WHERE name = name')

        # Переход к фукции Start без ожидания сообщения от пользователя
        Start(message)

    elif message.text == 'нет':
        bot.send_message(message.chat.id, text = 'анкета не будет удалена')

        # Переход к фукции Start без ожидания сообщения от пользователя
        Start(message)

    else:
        bot.send_message(message.chat.id, text='пожалуйста воспользуйтесь кнопками')

        # Переход к фукции Start без ожидания сообщения от пользователя
        Start(message)


# Создание функции для получения данных о заказчике
def Adress(message):

    global name

    bot.send_message(message.chat.id, text='введите адрес заказчика')
    name = message.text

    
    # Переход к функции New_Customer с ожиданием сообщения от пользователя
    bot.register_next_step_handler(message, name, New_Customer)


# Создание функции для получения данных о заказчике
def New_Customer(message):

    global adress

    bot.send_message(message.chat.id, text='введите объем в сотках')
    adress = message.text

    # Переход к функции New_Customer_Bigcash с ожиданием сообщения от пользователя
    bot.register_next_step_handler(message, New_Customer_Bigcash)


# Создание функции для получения данных о заказчике
def New_Customer_Bigcash(message):

    global amount

    bot.send_message(message.chat.id, text='введите сколько вам заплатили с учетом чаевых')
    amount = message.text

    # Переход к функции New_Customer_Cash с ожиданием сообщения от пользователя
    bot.register_next_step_handler(message, New_Customer_Cash)


# Создание функции для получения данных о заказчике
def New_Customer_Cash(message):

    global big_cash

    big_cash = message.text
    bot.send_message(message.chat.id, text='введите сколько вам должны заплатить исходя из объема')

    # Переход к функции New_Customer_Cash_Finish с ожиданием сообщения от пользователя
    bot.register_next_step_handler(message, New_Customer_Cash_Finish)


# Создание функции с действиями происходящими после заполнения анкеты. 
# Создание клавиатуры для подтверждения правильности введённых данных
def New_Customer_Cash_Finish(message):

    global cash

    cash = message.text
    markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    new_customer = types.KeyboardButton(text='всё верно')
    customer = types.KeyboardButton(text='заполнить заново')

    markup1.add(new_customer, customer)
    
    bot.send_message(message.chat.id, text=f'анкета заполнена, проверьте правильность введенных данных\nимя - {name}\nадрес - {adress}\nобъем работы - {amount}\nприбыль с учетом чаевых - {big_cash}\nприбыль - {cash}', reply_markup=markup1)

    # Переход к функции True_Customer_Anket с ожиданием сообщения от пользователя
    bot.register_next_step_handler(message, True_Customer_Anket)


# Создание функции для записи полученных данных о заказчике в базу данных
def True_Customer_Anket(message):

    if message.text == 'всё верно':
        cursor.execute('INSERT INTO Users (name, adress, amount, big_cash, cash) VALUES (?, ?, ?, ?, ?)', (name, adress, amount, big_cash, cash))
        db.commit()

        # Переход к фукции Start без ожидания сообщения от пользователя
        Start(message)  

    elif message.text == 'заполнить заново':

        # Переход к фукции Customer_Input без ожидания сообщения от пользователя
        Customer_Input(message)

    else:
        bot.send_message(message.chat.id, text='пожалуйста воспользуйтесь кнопками')

        # Переход к фукции True_Customer_Anket без ожидания сообщения от пользователя
        True_Customer_Anket(message)


# Инициализация бота
bot.polling()