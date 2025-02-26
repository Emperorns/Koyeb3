import os
import json
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load configuration for Koyeb accounts
with open("config.json", "r") as f:
    config = json.load(f)
accounts = config.get("accounts", {})

# Get Telegram bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Koyeb Manager Bot!\nUse /accounts to list your accounts."
    )

# Command: /accounts - list available Koyeb accounts
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Linked Koyeb Accounts:\n"
    for account in accounts:
        text += f"• {account}\n"
    await update.message.reply_text(text)

# Command: /logs <account_name> <app_id>
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /logs <account_name> <app_id>")
        return
    account_name = context.args[0]
    app_id = context.args[1]
    api_key = accounts.get(account_name)
    if not api_key:
        await update.message.reply_text("Account not found.")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://api.koyeb.com/v1/apps/{app_id}/logs"  # Adjust endpoint as needed
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        await update.message.reply_text(f"Logs for {app_id}:\n{response.text}")
    else:
        await update.message.reply_text(f"Failed to fetch logs. Status: {response.status_code}")

# Command: /redeploy <account_name> <app_id>
async def redeploy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /redeploy <account_name> <app_id>")
        return
    account_name = context.args[0]
    app_id = context.args[1]
    api_key = accounts.get(account_name)
    if not api_key:
        await update.message.reply_text("Account not found.")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://api.koyeb.com/v1/apps/{app_id}/redeploy"  # Adjust endpoint as needed
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        await update.message.reply_text(f"Redeployment triggered for {app_id}.")
    else:
        await update.message.reply_text(f"Failed to redeploy. Status: {response.status_code}")

# Command: /stop <account_name> <app_id>
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /stop <account_name> <app_id>")
        return
    account_name = context.args[0]
    app_id = context.args[1]
    api_key = accounts.get(account_name)
    if not api_key:
        await update.message.reply_text("Account not found.")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://api.koyeb.com/v1/apps/{app_id}/stop"  # Adjust endpoint as needed
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        await update.message.reply_text(f"Stopped {app_id}.")
    else:
        await update.message.reply_text(f"Failed to stop. Status: {response.status_code}")

# Command: /restart <account_name> <app_id>
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /restart <account_name> <app_id>")
        return
    account_name = context.args[0]
    app_id = context.args[1]
    api_key = accounts.get(account_name)
    if not api_key:
        await update.message.reply_text("Account not found.")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://api.koyeb.com/v1/apps/{app_id}/restart"  # Adjust endpoint as needed
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        await update.message.reply_text(f"Restarted {app_id}.")
    else:
        await update.message.reply_text(f"Failed to restart. Status: {response.status_code}")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("accounts", list_accounts))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CommandHandler("redeploy", redeploy))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("restart", restart))

    # Start polling updates from Telegram
    application.run_polling()

if __name__ == '__main__':
    main()
