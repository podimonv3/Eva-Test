# 🤖 Eva-Test Telegram Bot

![Eva Bot Banner](Mine%20Project.png)

A clean and optimized Python Telegram bot repository, fully configured for seamless deployment on the Koyeb platform.

## 🚀 Features

- **Koyeb Ready:** Includes a built-in `Web Server` to prevent the app from shutting down due to health check timeouts on Koyeb.
- **Docker Support:** Pre-configured `Dockerfile` ensures smooth build and execution across cloud platforms.
- **Clean Structure:** Optimized repository with legacy Heroku configuration files removed for better efficiency.

## 🛠️ Environment Variables

Before deploying the bot on Koyeb, make sure to set up the following environment variables in your app settings:

| Variable | Description |
| :--- | :--- |
| `API_ID` | Your Telegram API ID (Get it from my.telegram.org) |
| `API_HASH` | Your Telegram API HASH (Get it from my.telegram.org) |
| `BOT_TOKEN` | Your Telegram Bot Token (Get it from @BotFather) |
| `ADMINS` | Telegram User IDs of the bot administrators |

## 📦 How to Deploy on Koyeb

1. **Fork** this repository to your GitHub account.
2. Go to the **Koyeb Console** and create a new Web Service.
3. Connect your GitHub account and select this repository.
4. Set the builder type to **Docker**.
5. Add the required **Environment Variables** listed above.
6. Click **Deploy**.

## 📄 License

GNU General Public License v2.0
