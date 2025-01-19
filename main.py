import os
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Load the .env file
load_dotenv()

# Access the environment variable
TOKEN: Final = os.getenv('TELEGRAM_TOKEN')

# Load the data from data.json
with open('data.json', 'r') as f:
    items = json.load(f)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data

    if user_message == '/start':
        await update.message.reply_text(f'Enter the customer name to start a new order with Dollar.')
        user_data['expecting'] = 'customer_name'
        user_data['orders'] = []
    elif user_data.get('expecting') == 'customer_name':
        await update.message.reply_text(f'Starting order for {user_message}\nEnter items in format: ITEMCODE QUANTITY')
        user_data['expecting'] = 'item_code'
        user_data['customer_name'] = user_message
    elif user_data.get('expecting') == 'item_code':
        if user_message.lower() == 'done':
            # Print the bill
            current_date = datetime.now().strftime("%m/%d")
            bill = f"{current_date}\n#\n{user_data['customer_name']} - D\n\n"
            total = 0
            for order in user_data['orders']:
                bill += f"{order['quantity']} P #{order['id']} - {order['name']} = ${order['price'] * order['quantity']}\n"
                total += order['price'] * order['quantity']
            bill += f"\nTotal: ${total}\n\nAddress:\n\nPaid:\n"
            await update.message.reply_text(bill)
            user_data.clear()  # Clear the order data
        else:
            user_message = user_message.upper().split()
            if len(user_message) != 2:
                item_code = user_message[0]
                quantity = 1
            else:
                item_code, quantity = user_message
                quantity = int(quantity)
            item = next((item for item in items if item['id'] == item_code), None)
            if item:
                total_price = item['price'] * quantity
                await update.message.reply_text(f'{quantity} P #{item["id"]} - {item["name"]} = ${total_price}')
                user_data['orders'].append({'id': item_code, 'name': item['name'], 'price': item['price'], 'quantity': quantity})
            else:
                await update.message.reply_text(f'Item code {item_code} not found.')
            user_data['expecting'] = 'item_code'  # Continue expecting item codes
    else:
        await update.message.reply_text(f'Unexpected message: {user_message}')

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Register the message handler
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()