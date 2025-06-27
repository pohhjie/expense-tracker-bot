# 💰 Expense Tracker Bot (🚧Work in Progress!)

### Dated: 2025.06.27

This is a personal proof-of-concept project where I'm exploring how to build a smart Telegram bot for tracking daily expenses. The idea is simple: send a message with your expense (like "30.50 for groceries"), and the bot tries to figure out the amount, description, and even suggests a category  using machine learning models (powered by HuggingFace). All your data stays safe and sound in a local SQLite database on your machine.

## ✨ Proposed Features
- Intelligent Expense Parsing: Automatically extracts amount and description from natural language input (e.g., "30.50 for groceries", "coffee 4.20").
- AI-Powered Categorization: Integrates with Hugging Face models to suggest expense categories (e.g., Food, Transport, Utilities).
- Secure Local Storage: All expense data is stored privately in a SQLite database, ensuring your financial information remains on your local machine.
- User-Specific Tracking: Supports multiple users, tracking expenses individually based on their Telegram User ID.
- Simple Interface: Interact directly through Telegram messages, making expense logging quick and intuitive.
- Basic Expense Summaries: (Future Feature Idea: Add commands to view daily/weekly/monthly summaries.)
- Interactive Controls: (Future Feature Idea: Add inline keyboards or custom keyboards for common actions/categories.)

## 🚀 Technologies Used
1. Python 3.10.x: The core programming language for the bot logic.
2. `python-dotenv`: Keeping those sensitive API keys out of the code.
3. `sqlite3` (Built-in Python): For a simple, file-based database.

## ⚙️ Installation & Setup
Detailed setup instructions will be added once the MVP is complete.

## 📄 License
This project is licensed under the MIT License - see the `LICENSE` file for full details.