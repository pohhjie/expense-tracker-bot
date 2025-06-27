'''

Reference: 
1. python-telegram-bot: 
(https://github.com/python-telegram-bot/python-telegram-bot/wiki)
  a. Tutorial (/Extensions---Your-first-Bot)

Documentation (https://docs.python-telegram-bot.org/)
'''
# import asyncio    # Not in used.
import logging
from dotenv import dotenv_values
from telegram import Update
from telegram.ext import (
  filters, 
  ApplicationBuilder, 
  CommandHandler,
  ContextTypes, 
  MessageHandler
)

''' Setting up logging module. '''
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#async def main():
  #token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  # For references.
  #----------------------------------------------------------------------------
  #bot = telegram.Bot(token)
  #async with bot:
    # '''
    # A simple method for testing your bot's authentication token. Requires no 
    # parameters. Returns basic information about the bot in form of a User 
    # object.
    # '''  
    # #print(await bot.get_me())
    # '''
    # Method to receive incoming updates.
    # '''
    # # updates = (await bot.get_updates())
    # # print(updates)
    # '''
    # Method to send a direct message to a Telegram user.
    # '''
    # # await bot.send_message(text='Hello, world!', chat_id={user_id})
    # #   
  #----------------------------------------------------------------------------  

'''
This function will always be triggered when the user invoke the '/start' 
command on the Bot. It will receive 2 parameters:
1. update - which is an object that contains all the information and data 
coming from Telegram itself.
2. context - which is another object that contains information and data about
the status of the library itself (telegram.Bot, Application, job_queue, etc.)
'''
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text="I'm a bot, please talk to me!")

'''
This method is part of MessageHandler example which echo back all non-command 
messages it receives.
'''
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=update.message.text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text_caps = ' '.join(context.args).upper()
  await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=text_caps)

'''
Method that handles any unknown commands that the user requested.
'''
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text="Sorry, I didn't understand that command.")

if (__name__ == '__main__'):
  config = dotenv_values(".env")  # Load environment secrets & configuration.
  #asyncio.run(main())

  # Related docs: 
  # 1. (/telegram.ext.applicationbuilder.html#telegram-ext-applicationbuilder)
  # 2. (/telegram.ext.application.html#telegram.ext.Application)
  application = (ApplicationBuilder()
    .token(config['TELEGRAM_BOT_TOKEN'])
    .build())

  # Instantiate an event listener `CommandHandler` that listens to '\start'
  # command and hook it to the event trigger.
  start_handler = CommandHandler('start', start)
  application.add_handler(start_handler)
  
  # Another example of instantiate an event listener `MessageHandler` that
  # listens to any message and hook it to the event trigger.
  echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
  application.add_handler(echo_handler)

  # Example of assigning function to defined keywords.  
  caps_handler = CommandHandler('caps', caps)
  application.add_handler(caps_handler)

  # Method that handles unknown commands.
  unknown_handler = MessageHandler(filters.COMMAND, unknown)
  application.add_handler(unknown_handler)

  # Run the application
  # 3. (/telegram.ext.application.html#telegram.ext.Application.run_polling)
  application.run_polling()


