'''

Reference: 
1. python-telegram-bot: 
(https://github.com/python-telegram-bot/python-telegram-bot/wiki)
  a. Tutorial (/Extensions---Your-first-Bot)

Documentation (https://docs.python-telegram-bot.org/)
'''
# import asyncio    # Not in used.
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta
from db import DatabaseManager
from dotenv import dotenv_values
from string_utils import parse_expense_text_strict

from telegram import (
  InlineKeyboardButton,
  InlineKeyboardMarkup,  
  Update
)
from telegram.ext import (
  filters, 
  ApplicationBuilder,
  CallbackQueryHandler,   
  CommandHandler,
  ContextTypes, 
  MessageHandler
)

''' Setting up logging module. '''
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

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
  db_manager.init_db()

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


async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 
    Handles messages starting with /new for expense parsing and recording.
    """
    user_id = update.effective_user.id
    raw_text = update.message.text
    parsed_data = parse_expense_text_strict(raw_text)

    # Check if parsing was successful and an amount was found
    if parsed_data and parsed_data["amount"] is not None:
        amount = parsed_data["amount"]
        description = parsed_data["description"]
        category = parsed_data["category"] # This comes from the string_utils parser (currently "Uncategorized")
        
        # Convert datetime object to ISO 8601 string format
        current_date_str = datetime.now().isoformat()

        logger.info(f"User {user_id} - Parsed: Amount={amount},"
          f"Desc='{description}', Cat='{category}'")

        if db_manager:
          try:
              # Insert expense into the database
              expense_id = db_manager.insert_expense(user_id, amount, 
                description, category, current_date_str)
              
              # Construct text to record down user's purchase.
              reply_text = (
                  f"Expense recorded successfully!\n"
                  f"Amount: {amount:.2f}\n" # Format amount to 2 decimal places
                  f"Description: {description if description else 'N/A'}\n"
                  f"Category: {category}\n"
                  f"Date: {current_date_str.split('T')[0]}\n" # Display only the date part to the user
                  f"ID: {expense_id}"
              )
              await update.message.reply_text(reply_text)

          except Exception as e:
            logger.error(f"Error inserting expense for user {user_id}: {e}")
            await update.message.reply_text("An error occurred while saving your expense. Please try again.")
        else:
          logger.error("Database manager not initialized. Cannot record expense.")
          await update.message.reply_text("Sorry, the bot's database is not ready. Please try again later.")
    else:
      logger.info(f"Failed to parse strict expense for user {user_id} from text: '{raw_text}'")
      await update.message.reply_text(
          "I couldn't understand that. Please use the exact format: `/new <amount> for <description>`\n"
          "For example: `/new 15.75 for coffee at Starbucks`"
      )
  
# async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   text_caps = ' '.join(context.args).upper()
#   await context.bot.send_message(
#     chat_id=update.effective_chat.id,
#     text=text_caps)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Sends a message with three inline buttons attached."""

  msg = ("Which month's expense summary would you like to see?"
    "(Records are only available for the past 3 months.)")
  
  current_date = datetime.now().replace(day=1)
  last_month = current_date - relativedelta(months=1)
  two_month = current_date - relativedelta(months=2)

  keyboard = [
    [
      InlineKeyboardButton(current_date.strftime('%b %Y'), callback_data=current_date.strftime('%Y-%m')),
      InlineKeyboardButton(last_month.strftime('%b %Y'), callback_data=last_month.strftime('%Y-%m')),
      InlineKeyboardButton(two_month.strftime('%b %Y'), callback_data=two_month.strftime('%Y-%m')),        
    ],
    [InlineKeyboardButton("Cancel", callback_data="0")],
  ]

  reply_markup = InlineKeyboardMarkup(keyboard)

  await update.message.reply_text(msg, reply_markup=reply_markup)


async def summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """
  Parses the CallbackQuery from an inline keyboard button press (e.g., from a month selection)
  and updates the message text with the selected option. It then retrieves and displays
  the expense summary for the selected month.
  """
  query = update.callback_query
  user_id = update.effective_user.id

  # CallbackQueries need to be answered, even if no notification to the
  # user is needed. Some clients may have trouble otherwise.
  # See https://core.telegram.org/bots/api#callbackquery
  # This sends a "loading" or "acknowledged" state to the Telegram client.
  await query.answer()

  # Edit the original message to show the selected option, providing immediate feedback.
  await query.edit_message_text(text=f"Selected option: {query.data}")

  # Check if the user has selected the 'cancel' option (assuming '0' is the cancel data).
  if query.data == '0':
      await query.message.reply_text("Expense summary request cancelled.")
      return # Exit the function if cancelled

  # Proceed only if the database manager is initialized.
  if db_manager:
    try:
      reply_text = ''
      # Retrieve expenses from the database for the specified user and date range (month).
      # query.data is expected to contain the month/date information for filtering.
      expenses = db_manager.get_expenses_by_user_and_date(user_id, query.data)

      # Check if any expenses were found for the selected period.
      if len(expenses) < 1:
        reply_text = 'No expenses found for the selected period.'
      else:
        # Initialize a list to build the reply message line by line.
        # Include a header indicating the number of expenses found.
        reply_lines = [f"{len(expenses)} expense(s) found!\n"]

        index = 1
        total = 0.0
        # Iterate through each expense to format it and calculate the total.
        for expense in expenses:
            # Format each expense into a readable string.
            # Use 'N/A' for description if it's empty.
            # Format amount to two decimal places.
            # Convert ISO formatted date string back to datetime object for custom formatting.
            line = (
                f"#{str(index)}) {expense['description'] if expense['description'] else 'N/A'} for ${expense['amount']:.2f}\n"
                f"Category: {expense['category']}\n"
                f"Date: {datetime.fromisoformat(expense['date']).strftime('%d %b %Y, %I:%M %p')}\n"
            )
            reply_lines.append(line)
            index = index + 1
            total = total + expense['amount']

        # Add the total expenditure line to the reply.
        reply_lines.append(f"Total expenditure: ${total:.2f}")
        # Join all lines to form the final reply text.
        reply_text = "\n".join(reply_lines)

      # Send the formatted expense summary message to the user.
      await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text
      )

    except Exception as e:
      # Log any errors that occur during database interaction or message sending.
      logger.error(f"Error fetching or processing summary for user {user_id}: {e}")
      # Inform the user about the error.
      await query.message.reply_text("An error occurred while fetching your summary. Please try again.")
  
  else:
    # Log if the database manager was not initialized.
    logger.error("Database manager not initialized. Cannot retrieve expense summary.")
    # Inform the user that the database is not ready.
    await query.message.reply_text("Sorry, the bot's database is not ready. Please try again later.")  


'''
Method that handles any unknown commands that the user requested.
'''
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text="Sorry, I didn't understand that command.")




if (__name__ == '__main__'):
  config = dotenv_values(".env")  # Load environment secrets & configuration.

  # Related docs: 
  # 1. (/telegram.ext.applicationbuilder.html#telegram-ext-applicationbuilder)
  # 2. (/telegram.ext.application.html#telegram.ext.Application)
  application = (ApplicationBuilder()
    .token(config['TELEGRAM_BOT_TOKEN'])
    .build())

  # Initialise db.
  db_manager = DatabaseManager(config['DB_CONNECTION_NAME'])

  # Instantiate an event listener `CommandHandler` that listens to '\start'
  # command and hook it to the event trigger.
  application.add_handler(CommandHandler('start', start))
  
  # Method to add expenses.
  application.add_handler(CommandHandler('new', new))
  application.add_handler(CommandHandler('summary', summary))
  application.add_handler(CallbackQueryHandler(summary_callback))

  # Another example of instantiate an event listener `MessageHandler` that
  # listens to any message and hook it to the event trigger.
  # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
  # application.add_handler(echo_handler)

  # Example of assigning function to defined keywords.  
  # caps_handler = CommandHandler('caps', caps)
  # application.add_handler(caps_handler)
  


  # Method that handles unknown commands.
  unknown_handler = MessageHandler(filters.COMMAND, unknown)
  application.add_handler(unknown_handler)



  # Run the application
  # 3. (/telegram.ext.application.html#telegram.ext.Application.run_polling)
  application.run_polling()
  
  # Close the connection.
  db_manager.close()