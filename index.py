from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import  json, io, requests, os
TOKEN = os.getenv("BOT_TOKEN")

# job_list = [
#     "🧑‍💻 Software Engineer - TCS, Mumbai\nApply: https://www.tcs.com/careers",
#     "📱 Android Developer - Infosys, Bangalore\nApply: https://www.infosys.com/careers",
#     "🕸️ Web Developer - Wipro, Pune\nApply: https://www.wipro.com/careers"
# ] title location link com
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
    await update.message.reply_text("Hello! I am your bot. My Owner is @sunil_sen sir and I am here to assist you.\n\n Type **new jobs** to get the latest job openings.")

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

# Main function to start the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token("TOKEN").build()

    fetch_jobs()  # Fetch jobs at startup
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_jobs))

    print("Bot is running...")
    app.run_polling()
