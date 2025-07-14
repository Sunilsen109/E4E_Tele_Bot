from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup , ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters , CallbackContext
import  json, io, requests, os
from dotenv import load_dotenv
from web_scrapping import get_latest_sarkari_jobs
import asyncio

SEEN_JOBS_FILE = "seen_jobs.json"
USERS_FILE = "users.json"


def load_seen_jobs() -> set:
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return set()
            return set(json.loads(content))
    return set()

def save_seen_jobs(seen_jobs: set):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen_jobs), f , indent=2) 

seen_jobs = load_seen_jobs()


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)



load_dotenv()  # loads .env file
TOKEN = os.getenv("BOT_TOKEN")

# # Define a simple /start command
job_list = []  # Initialize an empty list to store job listings
def fetch_jobs(limit: int = 10) -> list[dict]:
    response = requests.post(
        "https://jooble.org/api/bba03e70-0111-48d7-be08-b93b17abb83b",
        json={"keywords": "developer", "location": "India"}
    )
    data = response.json()
    # If the API returns {"jobs": [...]}, extract that list
    if isinstance(data, dict) and "jobs" in data:
        data = data["jobs"]

    # At this point `data` should be a list
    return data[:limit]
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    full_name = update.effective_user.full_name

    users = load_users()


    if chat_id not in users or users[chat_id].get("phone", "") == "":
        users[chat_id] = {"name": full_name, "phone": ""}
        save_users(users)
        await update.message.reply_text(
            f"Hi {full_name}!\nPlease send your **10-digit mobile number** to get updates."
        )
    else:
        await update.message.reply_text("You're already registered ✅")
    await update.message.reply_text(f"Hi {full_name}! Please reply with your mobile number for updates.")
    
    keyboard = [["📰 Sarkari Result", "💼 New Jobs"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text( "Hello! I am your bot. My owner is @sunil_sen sir and I am here to assist you.\n\n"
        "Choose an option below 👇",
        reply_markup=reply_markup
    )

async def new_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = fetch_jobs(10)
    if 'new jobs' in update.message.text.lower():
            # Example: send each job with an 'Apply' button
        for job in jobs:
            title    = job.get("title", "Untitled role")
            company  = job.get("company", "Unknown company")
            location = job.get("location", "India")
            url      = job.get("url") or job.get("link") or "#"

            text = f"*{title}* – {company} ({location})"
            keyboard = [[InlineKeyboardButton("Apply Link 🔗", url=url)]]
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=False
            )
            await asyncio.sleep(0.5)
    if "sarkari result" in update.message.text.lower():
        await update.message.reply_text("Fetching Sarkari Results... please wait.")
        jobs = get_latest_sarkari_jobs()
        await update.message.reply_text(jobs)
    else:
        await update.message.reply_text("Type 'sarkari result' or 'new jobs' to get the latest jobs.")
            
    

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()

    users = load_users()

    # Save phone if it's a valid number (e.g., 10+ digits)
    if chat_id in users and users[chat_id]["phone"] == "":
        if text.isdigit() and len(text) >= 10:
            users[chat_id]["phone"] = text
            save_users(users)
            await update.message.reply_text("✅ Mobile number saved! You'll now get job alerts.")
        else:
            await update.message.reply_text("❌ Please send a valid mobile number.")
        return

    
    
    if "sarkari result" in user_message:
        update.message.reply_text("Fetching Sarkari Results... please wait.")
        jobs = get_latest_sarkari_jobs()
        await update.message.reply_text(jobs)
    else:
        await update.message.reply_text("Type 'sarkari result' to get the latest jobs.")




async def notify_new_sarkari_jobs():
    await asyncio.sleep(10)  # wait for bot to start

    while True:
        print("Checking for new Sarkari jobs...")
        users = load_users()
        jobs_text = get_latest_sarkari_jobs()
        jobs_list = jobs_text.split("\n")

        new_jobs = [job for job in jobs_list if job not in seen_jobs]
        #Testing Purpose
        
        # for chat_id in users:
        #     try:
        #         await app.bot.send_message(chat_id=int(chat_id), text=f"🆕 Sunil this is testing msg from you code << chill")
        #     except Exception as e:
        #         print(f"Failed to message {chat_id}: {e}")
        if new_jobs:
            for job in new_jobs:
                seen_jobs.add(job)
                save_seen_jobs(seen_jobs)
                for chat_id in users:
                    try:
                        await app.bot.send_message(chat_id=int(chat_id), text=f"🆕 New Alert For Job: {job}")
                    except Exception as e:
                        print(f"Failed to message {chat_id}: {e}")

        await asyncio.sleep(3600)  # 1 hours it will check


# Main function to start the bot
if __name__ == '__main__':
    #TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).read_timeout(30).connect_timeout(30).build()

    fetch_jobs()  # Fetch jobs at startup
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_jobs))
    
    # Add background job
    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(notify_new_sarkari_jobs()), interval=3600, first=5)


    print("Bot is running...")
    app.run_polling()

