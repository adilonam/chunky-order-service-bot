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
    user_data = context.user_data

    if user_message in ['/sc' , '/su' , '/sd']:
        user_data.clear()
        if user_message == '/sc':
            shop = 'Chunky'
        elif user_message == '/su':
            shop = 'Uno'
        elif user_message == '/sd':
            shop = 'Dollar'
        await update.message.reply_text(f'Enter the customer name to start a new order with {shop}.')
        user_data['expecting'] = 'customer_name'
        user_data['orders'] = []
        user_data['shop'] = shop
    elif user_message == '/cancel':
        user_data.clear()
        await update.message.reply_text('Orders cancelled.')
    elif user_data.get('expecting') == 'customer_name':
        await update.message.reply_text(f'Starting order for {user_message}\nEnter items as: ITEMCODE QUANTITY (bulk entries supported across multiple lines).\nType "clo" to cancel last order.\nType "done" to finish the order.\nAny time type "/cancel" to cancel all orders.')
        user_data['expecting'] = 'item_code'
        user_data['customer_name'] = user_message
    elif user_data.get('expecting') == 'item_code':
        if user_message.lower() == 'done':
            # Print the bill
            current_date = datetime.now().strftime("%m/%d")
            bill = f"{current_date}\n#\n{user_data['customer_name']} - {user_data['shop'][0]}\n\n"
            total = 0
            for order in user_data['orders']:
                bill += f"{order['quantity']} P #{order['id']} - {order['name']} = ${order['price'] * order['quantity']}\n"
                total += order['price'] * order['quantity']
            bill += f"\nTotal: ${total}\n\nAddress:\n\nPaid:\n"
            await update.message.reply_text(bill)
            
        elif user_message.lower() == 'clo':
            if user_data['orders']:
                user_data['orders'].pop()
                await update.message.reply_text('Last order cancelled.')
            else:
                await update.message.reply_text('No orders to cancel.')
        else:
            user_messages = user_message.upper().split('\n')
            for user_message in user_messages:
                user_message = user_message.split()
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