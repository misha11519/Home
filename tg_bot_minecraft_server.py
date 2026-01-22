from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"

user_settings = {}

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_settings:
        user_settings[user_id] = {
            "version": "не выбрана",
            "loader": "не выбран",
            "max_players": "20",
            "difficulty": "normal",
            "gamemode": "survival",
            "pvp": "true",
            "online_mode": "true"
        }
    
    keyboard = [
        [InlineKeyboardButton("Выбор действия", callback_data="action_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 Главное меню\n\nДобро пожаловать!",
        reply_markup=reply_markup
    )

async def action_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔨 Создание сервера", callback_data="create_server")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    current_settings = user_settings.get(user_id, {})
    
    version = current_settings.get("version", "не выбрана")
    loader = current_settings.get("loader", "не выбран")
    
    keyboard = [
        [InlineKeyboardButton(f"Версия: {version}", callback_data="set_version")],
        [InlineKeyboardButton(f"Загрузчик: {loader}", callback_data="set_loader")],
        [InlineKeyboardButton("📝 Настройки server.properties", callback_data="server_properties")],
        [InlineKeyboardButton("💾 Сохранить настройки", callback_data="save_settings")],
        [InlineKeyboardButton("🔙 Назад", callback_data="action_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ Настройки сервера\n\nВыберите параметр для изменения:",
        reply_markup=reply_markup
    )

async def version_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1.20.4", callback_data="version_1.20.4")],
        [InlineKeyboardButton("1.20.1", callback_data="version_1.20.1")],
        [InlineKeyboardButton("1.19.4", callback_data="version_1.19.4")],
        [InlineKeyboardButton("1.19.2", callback_data="version_1.19.2")],
        [InlineKeyboardButton("1.18.2", callback_data="version_1.18.2")],
        [InlineKeyboardButton("1.16.5", callback_data="version_1.16.5")],
        [InlineKeyboardButton("1.12.2", callback_data="version_1.12.2")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите версию Minecraft:",
        reply_markup=reply_markup
    )

async def loader_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Vanilla", callback_data="loader_vanilla")],
        [InlineKeyboardButton("Forge", callback_data="loader_forge")],
        [InlineKeyboardButton("Fabric", callback_data="loader_fabric")],
        [InlineKeyboardButton("Paper", callback_data="loader_paper")],
        [InlineKeyboardButton("Spigot", callback_data="loader_spigot")],
        [InlineKeyboardButton("Purpur", callback_data="loader_purpur")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите загрузчик сервера:",
        reply_markup=reply_markup
    )

async def server_properties_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    current = user_settings.get(user_id, {})
    
    max_players = current.get("max_players", "20")
    difficulty = current.get("difficulty", "normal")
    gamemode = current.get("gamemode", "survival")
    pvp = current.get("pvp", "true")
    online_mode = current.get("online_mode", "true")
    
    keyboard = [
        [InlineKeyboardButton(f"Max Players: {max_players}", callback_data="set_max_players")],
        [InlineKeyboardButton(f"Difficulty: {difficulty}", callback_data="set_difficulty")],
        [InlineKeyboardButton(f"Gamemode: {gamemode}", callback_data="set_gamemode")],
        [InlineKeyboardButton(f"PVP: {pvp}", callback_data="set_pvp")],
        [InlineKeyboardButton(f"Online Mode: {online_mode}", callback_data="set_online_mode")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📝 Настройки server.properties\n\nВыберите параметр:",
        reply_markup=reply_markup
    )

async def max_players_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("10", callback_data="maxplayers_10")],
        [InlineKeyboardButton("20", callback_data="maxplayers_20")],
        [InlineKeyboardButton("50", callback_data="maxplayers_50")],
        [InlineKeyboardButton("100", callback_data="maxplayers_100")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Максимальное количество игроков:",
        reply_markup=reply_markup
    )

async def difficulty_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Peaceful", callback_data="difficulty_peaceful")],
        [InlineKeyboardButton("Easy", callback_data="difficulty_easy")],
        [InlineKeyboardButton("Normal", callback_data="difficulty_normal")],
        [InlineKeyboardButton("Hard", callback_data="difficulty_hard")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите сложность:",
        reply_markup=reply_markup
    )

async def gamemode_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Survival", callback_data="gamemode_survival")],
        [InlineKeyboardButton("Creative", callback_data="gamemode_creative")],
        [InlineKeyboardButton("Adventure", callback_data="gamemode_adventure")],
        [InlineKeyboardButton("Spectator", callback_data="gamemode_spectator")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите режим игры:",
        reply_markup=reply_markup
    )

async def pvp_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Включен", callback_data="pvp_true")],
        [InlineKeyboardButton("Выключен", callback_data="pvp_false")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "PVP режим:",
        reply_markup=reply_markup
    )

async def online_mode_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Включен", callback_data="onlinemode_true")],
        [InlineKeyboardButton("Выключен", callback_data="onlinemode_false")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Online Mode (лицензия):",
        reply_markup=reply_markup
    )

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("Выбор действия", callback_data="action_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎮 Главное меню\n\nДобро пожаловать!",
            reply_markup=reply_markup
        )
    
    elif query.data == "action_menu":
        await action_menu(query, context)
    
    elif query.data == "create_server":
        await query.answer("⚠️ Функция в разработке", show_alert=True)
    
    elif query.data == "settings":
        await settings_menu(query, context)
    
    elif query.data == "set_version":
        await version_menu(query, context)
    
    elif query.data == "set_loader":
        await loader_menu(query, context)
    
    elif query.data == "server_properties":
        await server_properties_menu(query, context)
    
    elif query.data == "set_max_players":
        await max_players_menu(query, context)
    
    elif query.data == "set_difficulty":
        await difficulty_menu(query, context)
    
    elif query.data == "set_gamemode":
        await gamemode_menu(query, context)
    
    elif query.data == "set_pvp":
        await pvp_menu(query, context)
    
    elif query.data == "set_online_mode":
        await online_mode_menu(query, context)
    
    elif query.data.startswith("version_"):
        version = query.data.replace("version_", "")
        user_settings[user_id]["version"] = version
        await settings_menu(query, context)
    
    elif query.data.startswith("loader_"):
        loader = query.data.replace("loader_", "").capitalize()
        user_settings[user_id]["loader"] = loader
        await settings_menu(query, context)
    
    elif query.data.startswith("maxplayers_"):
        max_players = query.data.replace("maxplayers_", "")
        user_settings[user_id]["max_players"] = max_players
        await server_properties_menu(query, context)
    
    elif query.data.startswith("difficulty_"):
        difficulty = query.data.replace("difficulty_", "")
        user_settings[user_id]["difficulty"] = difficulty
        await server_properties_menu(query, context)
    
    elif query.data.startswith("gamemode_"):
        gamemode = query.data.replace("gamemode_", "")
        user_settings[user_id]["gamemode"] = gamemode
        await server_properties_menu(query, context)
    
    elif query.data.startswith("pvp_"):
        pvp = query.data.replace("pvp_", "")
        user_settings[user_id]["pvp"] = pvp
        await server_properties_menu(query, context)
    
    elif query.data.startswith("onlinemode_"):
        online_mode = query.data.replace("onlinemode_", "")
        user_settings[user_id]["online_mode"] = online_mode
        await server_properties_menu(query, context)
    
    elif query.data == "save_settings":
        current = user_settings.get(user_id, {})
        settings_text = (
            f"✅ Настройки сохранены!\n\n"
            f"📋 Основные параметры:\n"
            f"Версия: {current.get('version', 'не выбрана')}\n"
            f"Загрузчик: {current.get('loader', 'не выбран')}\n\n"
            f"📝 Server.properties:\n"
            f"Max Players: {current.get('max_players', '20')}\n"
            f"Difficulty: {current.get('difficulty', 'normal')}\n"
            f"Gamemode: {current.get('gamemode', 'survival')}\n"
            f"PVP: {current.get('pvp', 'true')}\n"
            f"Online Mode: {current.get('online_mode', 'true')}\n"
            f"EULA: true (всегда)"
        )
        
        keyboard = [
            [InlineKeyboardButton("Выбор действия", callback_data="action_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(settings_text, reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
