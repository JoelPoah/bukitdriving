# python -m pip install --upgrade pip
# pip install python-telegram-bot
import asyncio
import logging
import json
import subprocess
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Constants to define conversation states
USERNAME, PASSWORD,SESSION = range(3)

USERS = json.load(open('user_data.json'))



TOKEN = "7478425020:AAFtYzoZ2pm4QMq6siIbHWz6nsv-xVYcaoo"
BOT_USERNAME = "@BBDC_SlotFinder_bot"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s executed /start", user.first_name)
    await update.message.reply_text(
        '''
What this bot does:
We are a team of individuals who will assist in booking your BBDC practical lessons slots based on your given schedule.

✅ Supported: Class 3/3A Practical lessons
❌ Not supported: FTT/BTT/TPDS/DS

Pricing:
1 credit will be deducted for every practical slot booked.
See /credits command for more information.

How to use:
1. Use /set_login command to update your BBDC username and password.
2. Add bot credits with /credits command.
3. Use the /choose_session command to select the practical sessions you are available for.
4. Use the /start_checking command to start checking for new slots. We will automatically do it for you and inform you if you got a slot. Use the /stop_checking command to stop checking for new slots.
5. The bot will notify you once a slot is found and booked for you.
6. Do not login to your BBDC account while the bot is running as it will interfere with the bot's operation. If you need to login, use the /stop_checking command to stop the bot first.

'''
    )
    return ConversationHandler.END


async def refresh_users(USERS):
    with open('user_data.json', 'w') as f:
        json.dump(USERS, f)
    
    USERS = json.load(open('user_data.json'))
    
    return USERS
        

async def set_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please enter your username"
    )
    return USERNAME

async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USERS[str(update.message.from_user.id)]['USERNAME'] = update.message.text
    await refresh_users()
    await update.message.reply_text(
        f"Please enter your password"
    )
    return PASSWORD

async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USERS[str(update.message.from_user.id)]['PASSWORD'] = update.message.text
    
    USERS = await refresh_users(USERS)
    await update.message.reply_text(
        f"This is your username:{USERS[str(update.message.from_user.id)]['USERNAME']} password: {USERS[str(update.message.from_user.id)]['PASSWORD']}"
    )
    return ConversationHandler.END

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    LOCATED_USER = USERS[str(update.message.from_user.id)]
    
    if LOCATED_USER:
        await update.message.reply_text(
            f"Your username is {LOCATED_USER['USERNAME']} and password is {LOCATED_USER['PASSWORD']} \n Your selected dates are {LOCATED_USER['DATES']}"
        )
    else:
        await update.message.reply_text(
            f"Please set your login credentials with /set_login"
        )
    
    return ConversationHandler.END

async def choose_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please type the dates where you are available for practical lessons for the current Month. \nIf you are free on the first 5 days this should be your reply:\n [1,2,3,4,5]",

        
    )
    return SESSION

async def confirm_session_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # convert the string to a list
    date_list = eval(update.message.text)
    
    if not isinstance(date_list, list):
        await update.message.reply_text(
            "Please do /choose_session and enter a valid list of dates"
        )
        return ConversationHandler.END
    
    USERS[str(update.message.from_user.id)]['DATES'] = date_list
    
    USERS = await refresh_users(USERS)
    
    await update.message.reply_text(
        f"You have chosen the following dates: {USERS[str(update.message.from_user.id)]['DATES']}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END



async def start_checking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Construct the command and arguments
        command = [
            'python', 'subbookingprocess.py',
            '--chatid', str(update.message.from_user.id),
            '--username', str(USERS[str(update.message.from_user.id)]['USERNAME']),
            '--password', str(USERS[str(update.message.from_user.id)]['PASSWORD']),
            '--dates', str(USERS[str(update.message.from_user.id)]['DATES'])
        ]
        
        # Log the command for debugging
        print(f"Running command: {' '.join(command)}")

        # Start the subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False, shell=False)
        
        # don't show output in console
        
        
        
        
        # process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Store the subprocess ID
        subprocess_id = process.pid
        print(f"Subprocess ID: {subprocess_id}")
        
        USERS[str(update.message.from_user.id)]['SUBPROCESS_ID'] = subprocess_id
        
        USERS= await refresh_users(USERS)

        # Wait for the process to complete and capture the output
        #stdout, stderr = process.communicate()

        # Log outputs for debugging
        #print(f"Script output: {stdout}")
        #if stderr:
        #    print(f"Script error output: {stderr}")

        # Send the output back to the user
        #if process.returncode == 0:
        #    await update.message.reply_text(f"Script output:\n{stdout}")
        #else:
        #    await update.message.reply_text(f"Script encountered an error:\n{stderr}")

    except Exception as e:
        await update.message.reply_text(f"Error running script: {e}")


async def stop_checking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        
        # Check if there is an active process for the user
        if user_id in USERS and 'SUBPROCESS_ID' in USERS[str(user_id)]:
            
            # Terminate the process
            # USERS[str(update.message.from_user.id)]['SUBPROCESS_ID'].kill()
            subprocess.Popen(['kill', '-9', str(USERS[str(update.message.from_user.id)]['SUBPROCESS_ID'])])
            #USERS[str(update.message.from_user.id)]['SUBPROCESS_ID'].terminate()
            print(f"Terminated subprocess with ID: {USERS[str(update.message.from_user.id)]['SUBPROCESS_ID']}")
            
            # Optionally, you can use process.kill() to forcefully kill the process
            # process.kill()
            # print(f"Killed subprocess with ID: {process.pid}")
            
            # Send confirmation message to the user
            await update.message.reply_text(f"Stopped the process with PID: {USERS[str(update.message.from_user.id)]['SUBPROCESS_ID'].pid}")
            
            # Remove the process from the dictionary
            USERS[str(update.message.from_user.id)]['SUBPROCESS_ID'] = None
        else:
            await update.message.reply_text("No active process found to stop.")
    
    except Exception as e:
        await update.message.reply_text(f"Error stopping process: {e}")

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
    
    start_command_handler = CommandHandler('start_checking', start_checking)
    kill_command_handler = CommandHandler('stop_checking', stop_checking)
    

    application.add_handler(start_handler)
    application.add_handler(profile_handler)
    application.add_handler(choose_session_handler)
    application.add_handler(start_command_handler)
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
