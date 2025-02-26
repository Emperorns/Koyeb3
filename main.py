import os
import json
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {"accounts": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Load configuration and accounts
config = load_config()
accounts = config.get("accounts", {})

# Get Telegram Bot token from env variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Command: /start - Show available actions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Welcome to the Koyeb Manager Bot!\n"
        "Available commands:\n"
        "/start - Show available actions\n"
        "/accounts - List linked Koyeb accounts\n"
        "/apps - List deployed apps in each account\n"
        "/logs <account_name> <app_id> - Fetch logs for a specific app\n"
        "/redeploy <account_name> <app_id> - Trigger redeployment\n"
        "/stop <account_name> <app_id> - Stop an app\n"
        "/restart <account_name> <app_id> - Restart an app\n"
        "/add_account <api_key> - Link a new Koyeb account"
    )
    await update.message.reply_text(text)

# Command: /accounts - List all linked Koyeb accounts
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not accounts:
        await update.message.reply_text("No accounts linked.")
        return
    text = "Linked Koyeb Accounts:\n"
    for name in accounts:
        text += f"• {name}\n"
    await update.message.reply_text(text)

# Command: /apps - List deployed apps in each account
async def list_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not accounts:
        await update.message.reply_text("No accounts linked.")
        return
    response_text = ""
    for account_name, api_key in accounts.items():
        headers = {"Authorization": f"Bearer {api_key}"}
        # The endpoint below is an example; adjust it to the proper Koyeb API endpoint if needed.
        url = "https://api.koyeb.com/v1/apps"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            apps_data = resp.json()
            response_text += f"Apps in {account_name}:\n"
            # Assuming the response contains an "apps" list with app details
            apps = apps_data.get("apps", [])
            if not apps:
                response_text += "  No apps found.\n"
            else:
                for app in apps:
                    name = app.get("name", "Unnamed")
                    app_id = app.get("id", "N/A")
                    response_text += f"  • {name} (ID: {app_id})\n"
        else:
            response_text += f"Failed to fetch apps for {account_name} (Status {resp.status_code}).\n"
    await update.message.reply_text(response_text)

# Command: /logs <account_name> <app_id>
async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    url = f"https://api.koyeb.com/v1/apps/{app_id}/logs"  # Adjust endpoint if needed
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        await update.message.reply_text(f"Logs for {app_id}:\n{resp.text}")
    else:
        await update.message.reply_text(f"Failed to fetch logs (Status {resp.status_code}).")

# Command: /redeploy <account_name> <app_id>
async def redeploy_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    url = f"https://api.koyeb.com/v1/apps/{app_id}/redeploy"  # Adjust endpoint if needed
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        await update.message.reply_text(f"Redeployment triggered for {app_id}.")
    else:
        await update.message.reply_text(f"Failed to redeploy (Status {resp.status_code}).")

# Command: /stop <account_name> <app_id>
async def stop_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    url = f"https://api.koyeb.com/v1/apps/{app_id}/stop"  # Adjust endpoint if needed
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        await update.message.reply_text(f"Stopped {app_id}.")
    else:
        await update.message.reply_text(f"Failed to stop (Status {resp.status_code}).")

# Command: /restart <account_name> <app_id>
async def restart_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    url = f"https://api.koyeb.com/v1/apps/{app_id}/restart"  # Adjust endpoint if needed
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        await update.message.reply_text(f"Restarted {app_id}.")
    else:
        await update.message.reply_text(f"Failed to restart (Status {resp.status_code}).")

# Command: /add_account <api_key> - Link a new Koyeb account
async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /add_account <api_key>")
        return
    new_api_key = context.args[0]
    # Generate a new account name (e.g., account3, account4, etc.)
    new_account_name = f"account{len(accounts) + 1}"
    accounts[new_account_name] = new_api_key
    config["accounts"] = accounts
    save_config(config)
    await update.message.reply_text(f"New account added as '{new_account_name}'.")

def main():
    # Create the Application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers for each command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("accounts", list_accounts))
    application.add_handler(CommandHandler("apps", list_apps))
    application.add_handler(CommandHandler("logs", get_logs))
    application.add_handler(CommandHandler("redeploy", redeploy_app))
    application.add_handler(CommandHandler("stop", stop_app))
    application.add_handler(CommandHandler("restart", restart_app))
    application.add_handler(CommandHandler("add_account", add_account))

    # Webhook settings – ensure these environment variables are set in Koyeb
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g., "https://yourdomain.com"
    PORT = int(os.environ.get("PORT", "8443"))
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL environment variable not set")

    # We use the bot token as the webhook path for security
    webhook_path = TELEGRAM_BOT_TOKEN

    # Start the webhook server
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=f"{WEBHOOK_URL}/{webhook_path}"
    )

if __name__ == '__main__':
    main()
