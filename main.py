import telebot
from telebot import types
import sqlite3

# Инициализация бота
TOKEN = 'Insert your token here.'
bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('pizza_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Инициализация меню
def init_menu():
    menu = {
        "Маргарита": {"Маленькая": 250, "Средняя": 400, "Большая": 550},
        "Пепперони": {"Маленькая": 300, "Средняя": 450, "Большая": 600},
        "4 сыра": {"Маленькая": 350, "Средняя": 500, "Большая": 650}
    }
    cursor.execute("DELETE FROM menu")  # Очистка таблицы перед заполнением
    for pizza, sizes in menu.items():
        for size, price in sizes.items():
            cursor.execute("INSERT INTO menu (pizza_name, size, price) VALUES (?, ?, ?)", (pizza, size, price))
    conn.commit()

# Инициализация меню при запуске
init_menu()

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    # Получаем имя пользователя
    user_name = message.from_user.first_name

    # Приветственное сообщение с именем пользователя
    welcome_message = f"Привет, {user_name}! Добро пожаловать в бота пиццерии! 🍕\nВведите /open_menu, чтобы увидеть меню."

    # Отправляем приветственное сообщение
    bot.send_message(message.chat.id, welcome_message)

    # Отправляем фотографию
    with open("pizza_welcome.jpg", "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption="Вот наш повар который будет готовить для вас! 🍕")

# Команда /open_menu
@bot.message_handler(commands=['open_menu'])
def open_menu(message):
    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()
    menu_text = "\U0001F355 Меню:\n"
    for item in menu_items:
        menu_text += f"\n{item[1]} ({item[2]}): {item[3]} ₽\n"
    bot.send_message(message.chat.id, menu_text)

# Команда /order_pizza
@bot.message_handler(commands=['order_pizza'])
def order_pizza(message):
    cursor.execute("SELECT DISTINCT pizza_name FROM menu")
    pizzas = cursor.fetchall()
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for pizza in pizzas:
        markup.add(types.KeyboardButton(pizza[0]))
    msg = bot.send_message(message.chat.id, "Выберите пиццу:", reply_markup=markup)
    bot.register_next_step_handler(msg, choose_size)

def choose_size(message):
    pizza = message.text
    cursor.execute("SELECT size FROM menu WHERE pizza_name = ?", (pizza,))
    sizes = cursor.fetchall()
    if not sizes:
        bot.send_message(message.chat.id, "Извините, такой пиццы нет в меню. Попробуйте снова: /order_pizza")
        return

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for size in sizes:
        markup.add(types.KeyboardButton(size[0]))
    msg = bot.send_message(message.chat.id, f"Вы выбрали {pizza}. Теперь выберите размер:", reply_markup=markup)
    bot.register_next_step_handler(msg, confirm_order, pizza)

def confirm_order(message, pizza):
    size = message.text
    cursor.execute("SELECT price FROM menu WHERE pizza_name = ? AND size = ?", (pizza, size))
    price = cursor.fetchone()
    if not price:
        bot.send_message(message.chat.id, "Извините, такого размера нет. Попробуйте снова: /order_pizza")
        return

    user_id = message.chat.id
    cursor.execute("INSERT INTO orders (user_id, pizza_name, size, price) VALUES (?, ?, ?, ?)", (user_id, pizza, size, price[0]))
    conn.commit()
    bot.send_message(message.chat.id, f"Заказ добавлен: {pizza} ({size}) - {price[0]} ₽")

# Команда /edit_order
@bot.message_handler(commands=['edit_order'])
def edit_order(message):
    user_id = message.chat.id
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    user_orders = cursor.fetchall()
    if not user_orders:
        bot.send_message(message.chat.id, "У вас нет активных заказов. Введите /order_pizza, чтобы сделать новый заказ.")
        return

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for i, order in enumerate(user_orders):
        markup.add(types.KeyboardButton(f"{i + 1}. {order[2]} ({order[3]}) - {order[4]} ₽"))
    msg = bot.send_message(message.chat.id, "Выберите номер заказа для изменения:", reply_markup=markup)
    bot.register_next_step_handler(msg, edit_order_step)

def edit_order_step(message):
    try:
        order_index = int(message.text.split('.')[0]) - 1
        user_id = message.chat.id
        cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
        user_orders = cursor.fetchall()
        if order_index < 0 or order_index >= len(user_orders):
            raise ValueError

        order = user_orders[order_index]
        bot.send_message(message.chat.id, f"Изменяем заказ: {order[2]} ({order[3]}) - {order[4]} ₽")

        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        cursor.execute("SELECT DISTINCT pizza_name FROM menu")
        pizzas = cursor.fetchall()
        for pizza in pizzas:
            markup.add(types.KeyboardButton(pizza[0]))
        msg = bot.send_message(message.chat.id, "Выберите новую пиццу:", reply_markup=markup)
        bot.register_next_step_handler(msg, edit_order_choose_pizza, order_index)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный ввод. Попробуйте снова: /edit_order")

def edit_order_choose_pizza(message, order_index):
    pizza = message.text
    cursor.execute("SELECT size FROM menu WHERE pizza_name = ?", (pizza,))
    sizes = cursor.fetchall()
    if not sizes:
        bot.send_message(message.chat.id, "Извините, такой пиццы нет в меню. Попробуйте снова: /edit_order")
        return

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for size in sizes:
        markup.add(types.KeyboardButton(size[0]))
    msg = bot.send_message(message.chat.id, f"Вы выбрали {pizza}. Теперь выберите размер:", reply_markup=markup)
    bot.register_next_step_handler(msg, edit_order_confirm, order_index, pizza)

def edit_order_confirm(message, order_index, pizza):
    size = message.text
    cursor.execute("SELECT price FROM menu WHERE pizza_name = ? AND size = ?", (pizza, size))
    price = cursor.fetchone()
    if not price:
        bot.send_message(message.chat.id, "Извините, такого размера нет. Попробуйте снова: /edit_order")
        return

    user_id = message.chat.id
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    user_orders = cursor.fetchall()
    order_id = user_orders[order_index][0]
    cursor.execute("UPDATE orders SET pizza_name = ?, size = ?, price = ? WHERE id = ?", (pizza, size, price[0], order_id))
    conn.commit()
    bot.send_message(message.chat.id, f"Заказ изменён: {pizza} ({size}) - {price[0]} ₽")

# Команда /delete_order
@bot.message_handler(commands=['delete_order'])
def delete_order(message):
    user_id = message.chat.id
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    user_orders = cursor.fetchall()
    if not user_orders:
        bot.send_message(message.chat.id, "У вас нет активных заказов.")
        return

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for i, order in enumerate(user_orders):
        markup.add(types.KeyboardButton(f"{i + 1}. {order[2]} ({order[3]}) - {order[4]} ₽"))
    msg = bot.send_message(message.chat.id, "Выберите номер заказа для удаления:", reply_markup=markup)
    bot.register_next_step_handler(msg, delete_order_step)

def delete_order_step(message):
    try:
        order_index = int(message.text.split('.')[0]) - 1
        user_id = message.chat.id
        cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
        user_orders = cursor.fetchall()
        if order_index < 0 or order_index >= len(user_orders):
            raise ValueError

        order_id = user_orders[order_index][0]
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Заказ удалён.")
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный ввод. Попробуйте снова: /delete_order")

# Команда /show_orders
@bot.message_handler(commands=['show_orders'])
def show_orders(message):
    user_id = message.chat.id
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    user_orders = cursor.fetchall()
    if not user_orders:
        bot.send_message(message.chat.id, "У вас нет активных заказов.")
        return

    order_text = "Ваши заказы:\n"
    for i, order in enumerate(user_orders):
        order_text += f"{i + 1}. {order[2]} ({order[3]}) - {order[4]} ₽\n"
    bot.send_message(message.chat.id, order_text)

# Запуск бота
bot.polling(none_stop=True)