from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters , CallbackContext
import  json, io, requests, os
from dotenv import load_dotenv
from web_scrapping import get_latest_sarkari_jobs

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
    await update.message.reply_text("Hello! I am your bot. My Owner is @sunil_sen sir and I am here to assist you.\n\n Type **new jobs**  or **sarkari result**to get the latest job openings.")

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
            
    else:
        await update.message.reply_text("Type 'new jobs' to get job listings.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    if "sarkari result" in user_message:
        update.message.reply_text("Fetching Sarkari Results... please wait.")
        jobs = get_latest_sarkari_jobs()
        update.message.reply_text(jobs)
    else:
        update.message.reply_text("Type 'sarkari result' to get the latest jobs.")

# Main function to start the bot
if __name__ == '__main__':
    #TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    fetch_jobs()  # Fetch jobs at startup
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_jobs))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
    app.idle()
