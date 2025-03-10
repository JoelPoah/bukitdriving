import asyncio
import logging
import json
import os
import signal
import subprocess
import httpx
import psutil
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters, ContextTypes,PreCheckoutQueryHandler

# Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)

# logger = logging.getLogger(__name__)

# Constants to define conversation states
USERNAME, PASSWORD, SESSION = range(3)

# Load users from JSON file
def load_users():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

USERS = load_users()

TOKEN = "7478425020:AAEHGNgDqa590x2xq6bHjMwgorv2F2Nc-D4"
# TOKEN = '5912342398:AAF6t0WAuaCpksTr8a15kpPOwbCGa0IEG04'
BOT_USERNAME = "@BBDC_SlotFinder_bot"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    # logger.info("User %s executed /start", user.first_name)
    await update.message.reply_text(
        '''
What this bot does:
Booking your BBDC practical lessons slots based on your given schedule. Even Next Day Slots are guaranteed!

✅ Supported: Class 3/3A Practical lessons
❌ Not supported: FTT/BTT/TPDS/DS

Pricing:
1 credit will be deducted for every practical slot booked.
See /credits command for more information.

How to use:
1. Use /set_login command to update your BBDC username and password.
2. Add bot credits with /credits command. PM @JoelPP for better rates.
3. Use the /choose_session command to select the practical sessions you are available for.
4. Use the /start_checking command to start checking for new slots. We will automatically do it for you and inform you if you got a slot. Use the /stop_checking command to stop checking for new slots.
5. The bot will notify you once a slot is found and booked for you.
6. Do not login to your BBDC account while the bot is running as it will interfere with the bot's operation. If you need to login, use the /stop_checking command to stop the bot first.

'''
    )
    return ConversationHandler.END


async def refresh_users():
    with open('user_data.json', 'w') as f:
        json.dump(USERS, f, indent=4)


async def set_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please enter your username"
    )
    return USERNAME

async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in USERS:
        USERS[user_id] = {}
    USERS[user_id]['USERNAME'] = update.message.text
    await refresh_users()
    await update.message.reply_text(
        "Please enter your password"
    )
    return PASSWORD

async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    USERS[user_id]['PASSWORD'] = update.message.text
    await refresh_users()
    await update.message.reply_text(
        f"This is your username: {USERS[user_id]['USERNAME']} password: {USERS[user_id]['PASSWORD']}"
    )
    return ConversationHandler.END

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    LOCATED_USER = USERS.get(user_id)
    
    if LOCATED_USER:
        await update.message.reply_text(
            f"Your username is {LOCATED_USER['USERNAME']} and password is {LOCATED_USER['PASSWORD']} \nYour selected dates are {LOCATED_USER.get('DATES', 'Not set')}\nYour current credits are {LOCATED_USER.get('CREDITS', 0)}"
        )
    else:
        await update.message.reply_text(
            "Please set your login credentials with /set_login"
        )
    
    return ConversationHandler.END

async def choose_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please type the dates where you are available for practical lessons for the current month. \nIf you are free on the first 5 days this should be your reply:\n [1,2,3,4,5]",
    )
    return SESSION

async def confirm_session_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_list = json.loads(update.message.text)
        if not isinstance(date_list, list):
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Please do /choose_session and enter a valid list of dates"
        )
        return ConversationHandler.END

    user_id = str(update.message.from_user.id)
    USERS[user_id]['DATES'] = date_list
    await refresh_users()
    
    await update.message.reply_text(
        f"You have chosen the following dates: {USERS[user_id]['DATES']}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def start_checking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.message.from_user.id)
        user_data = USERS.get(user_id)
        
        if not user_data:
            await update.message.reply_text("Please set your login credentials with /set_login")
            return
        
        if 'DATES' not in user_data:
            await update.message.reply_text("Please choose your available dates with /choose_session")
            return
        if 'CREDITS' not in user_data or user_data['CREDITS'] < 1:
            await update.message.reply_text("Please add credits with /credits")
            return
        
        command = [
            'python', 'interval_script.py',
            '--chatid', user_id,
            '--username', user_data['USERNAME'],
            '--password', user_data['PASSWORD'],
            '--dates', json.dumps(user_data['DATES'])
        ]
        
        #creationflags = subprocess.CREATE_NEW_CONSOLE
        process = subprocess.Popen(command,creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,start_new_session=True)
        
        
        USERS[user_id]['SUBPROCESS_ID'] = process.pid
        await refresh_users()
        
        await update.message.reply_text("Process started successfully.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def check_booking_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text("Currently not implemented. /stop_checking to stop the bot and login to your account to check your booking history.")
    
    return ConversationHandler.END

async def stop_checking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.message.from_user.id)
        
        if 'SUBPROCESS_ID' in USERS[user_id]:
            
            subprocess_id = USERS[user_id]['SUBPROCESS_ID']
            
            
            try:
                parent = psutil.Process(subprocess_id)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except psutil.NoSuchProcess:
                print(f"No process with PID {subprocess_id} was found.")
            except psutil.AccessDenied:
                print(f"Permission denied to kill process with PID {subprocess_id}.")
            # os.kill(USERS[user_id]['SUBPROCESS_ID'], signal.SIGTERM) 
            # or signal.SIGKILL for a forceful kill
            # kill the other processes that were spawned by the main process
            
            # subprocess.Popen(['kill', '-9', str(USERS[user_id]['SUBPROCESS_ID'])])
            USERS[user_id]['SUBPROCESS_ID'] = None
            await refresh_users()
            await update.message.reply_text(f"Stopped the process for user {user_id}")
        else:
            await update.message.reply_text("No active process found to stop.")
    
    except Exception as e:
        await update.message.reply_text(f"Error stopping process: {e}")
        
async def add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = [{"label":"Credits","amount":1000}] # amount is in the smallest currency unit (e.g., cents)
    await update.message.reply_invoice(
        title="Add Credits",
        description="Add credits to your account for booking slots.",
        # provider_token='284685063:TEST:ZmU1ODA4OGJlOGQx',
        provider_token='350862534:LIVE:Njk2NzU2NzQ3MjA0',
        currency="SGD",
        prices=prices,
        payload="add_credits"
    )

async def pre_checkout_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
    
    return ConversationHandler.END


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    USERS[user_id]['CREDITS'] = USERS.get(user_id, {}).get('CREDITS', 0) + 1
    await refresh_users()
    await update.message.reply_text("Payment successful! 1 credits have been added to your account.")

    



    
def main():
    application = Application.builder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start_command)
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set_login', set_login)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_password)],
        },
        fallbacks=[],
    )
    
    profile_handler = CommandHandler('profile', profile_command)
    
    choose_session_handler = ConversationHandler(
        entry_points=[CommandHandler('choose_session', choose_session_command)],
        states={
            SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_session_chosen)],
        },
        fallbacks=[],
    )
    
    
    
    error_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: update.message.reply_text("Invalid command."))
    
    
    start_command_handler = CommandHandler('start_checking', start_checking)
    stop_command_handler = CommandHandler('stop_checking', stop_checking)
    check_booking_history_handler = CommandHandler('booking_history', check_booking_history)
    credits_command_handler = CommandHandler('credits', add_credits_command)
    
    pre_checkout_handler = PreCheckoutQueryHandler(pre_checkout_query_handler)
    
    successful_payment_handlers = MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler)
    
    
    application.add_handler(start_handler)
    application.add_handler(profile_handler)
    application.add_handler(choose_session_handler)
    application.add_handler(start_command_handler)
    application.add_handler(stop_command_handler)
    application.add_handler(conv_handler)
    application.add_handler(check_booking_history_handler)
    application.add_handler(credits_command_handler)
    application.add_handler(pre_checkout_handler)
    application.add_handler(successful_payment_handlers)
    application.add_error_handler(error_handler)
    
    
    application.run_polling(timeout=60, bootstrap_retries=3)


if __name__ == '__main__':
    main()