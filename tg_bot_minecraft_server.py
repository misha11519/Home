from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение при /start"""
    keyboard = [[InlineKeyboardButton("⚙️ Настройки сервера", callback_data="show_settings")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 Добро пожаловать в Minecraft Server Bot!\n\n"
        "Этот бот поможет настроить и получить готовые Minecraft сервера по твоим параметрам.\n\n"
        "Нажми кнопку ниже чтобы начать настройку:",
        reply_markup=reply_markup
    )

async def settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню настроек Minecraft сервера"""
    keyboard = [
        [InlineKeyboardButton("Легкий", callback_data="level_easy")],
        [InlineKeyboardButton("Средний", callback_data="level_medium")],
        [InlineKeyboardButton("Сложный", callback_data="level_hard")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ Настройки Minecraft сервера:\nВыберите сложность:",
        reply_markup=reply_markup
    )

async def handle_settings(update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор настроек"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_settings":
        await settings_menu(query, context)
    elif query.data.startswith("level_"):
        level = query.data.split("_")[1]
        context.user_data["server_level"] = level
        await query.edit_message_text(
            f"✅ Установлена сложность: {level.title()}\n\n"
            f"🎮 Настройки сохранены!\n"
            f"Дальше можно добавить другие параметры..."
        )
    elif query.data == "save_config":
        config = context.user_data.get("server_level", "не выбрана")
        await query.edit_message_text(
            f"💾 Конфигурация сохранена!\n"
            f"Сложность: {config}\n"
            f"✅ В будущем бот сгенерирует сервер по этим настройкам."
        )
    elif query.data == "back_to_start":
        keyboard = [[InlineKeyboardButton("⚙️ Настройки сервера", callback_data="show_settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎮 Главное меню\n\nВыберите действие:",
            reply_markup=reply_markup
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settings", start))
    app.add_handler(CallbackQueryHandler(handle_settings))
    app.run_polling()

if __name__ == "__main__":
    main()
