🍕 Pizza Bot - Telegram Bot for Ordering Pizza
This repository contains the code for a Telegram bot designed for ordering pizza. 
The bot allows users to browse the menu, select a pizza and size, place orders, and edit or delete them. All data is stored in an SQLite database.

✨ Features
Pizza Menu: Users can view available pizzas and their prices.
Order Placement: Users can select a pizza, choose a size, and place an order.
Order Editing: Users can modify their selected pizza or size.
Order Deletion: Users can delete their orders.
Order History: Users can view a list of their active orders.
Personalized Greeting: The bot greets users by name and sends a photo.

🛠 Technologies
Python: The primary programming language.
Telebot: A library for interacting with the Telegram API.
SQLite3: A database for storing the menu and orders.
Git: Version control system.

🚀 Getting Started
Prerequisites
Python 3.7 or higher.
A Telegram bot token from BotFather.

📂 Project Structure
Copy
pizza-bot/
├── main.py              # Main bot script
├── pizza_bot.db         # SQLite database file
├── pizza_welcome.jpg    # Welcome photo for the bot
├── README.md            # Project documentation
└── requirements.txt     # List of dependencies

📝 Usage
Start the bot by sending /start in Telegram.
Use /open_menu to view the pizza menu.
Use /order_pizza to place an order.
Use /edit_order to modify an existing order.
Use /delete_order to remove an order.
Use /show_orders to view your active orders.
