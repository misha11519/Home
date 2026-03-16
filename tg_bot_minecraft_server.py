import os
import zipfile
import logging
import aiohttp
import asyncio
import tempfile
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

logging.disable(logging.CRITICAL)

TOKEN = "BOT_TOKEN

user_settings = {}
user_states = {}
user_creating_server = {}
user_menu_message = {}

PRESETS = {
    "preset_vanilla_survival": {
        "name": "🌿 Ванильное выживание",
        "desc": "Классический сервер выживания",
        "settings": {
            "version": "1.20.1", "loader": "Fabric", "ram": "2048",
            "max_players": "20", "difficulty": "normal", "gamemode": "survival",
            "pvp": "true", "online_mode": "true", "port": "25565",
            "view_distance": "10", "simulation_distance": "10",
            "spawn_protection": "16", "allow_nether": "true",
            "allow_flight": "false", "command_blocks": "false",
            "spawn_monsters": "true", "spawn_animals": "true",
            "spawn_npcs": "true", "generate_structures": "true",
            "level_type": "minecraft:normal", "seed": "",
            "motd": "Vanilla Survival Server", "max_tick_time": "60000",
            "op_permission_level": "4", "entity_broadcast_range": "100",
            "player_idle_timeout": "0", "hardcore": "false",
            "whitelist": "false", "max_world_size": "29999984"
        }
    },
    "preset_hardcore": {
        "name": "💀 Хардкор",
        "desc": "Режим хардкора - одна жизнь",
        "settings": {
            "version": "1.20.1", "loader": "Fabric", "ram": "2048",
            "max_players": "10", "difficulty": "hard", "gamemode": "survival",
            "pvp": "true", "online_mode": "true", "port": "25565",
            "view_distance": "10", "simulation_distance": "10",
            "spawn_protection": "0", "allow_nether": "true",
            "allow_flight": "false", "command_blocks": "false",
            "spawn_monsters": "true", "spawn_animals": "true",
            "spawn_npcs": "true", "generate_structures": "true",
            "level_type": "minecraft:normal", "seed": "",
            "motd": "Hardcore Server - One Life!", "max_tick_time": "60000",
            "op_permission_level": "4", "entity_broadcast_range": "100",
            "player_idle_timeout": "0", "hardcore": "true",
            "whitelist": "true", "max_world_size": "29999984"
        }
    },
    "preset_creative": {
        "name": "🎨 Творческий",
        "desc": "Сервер для строительства в творческом режиме",
        "settings": {
            "version": "1.20.1", "loader": "Fabric", "ram": "2048",
            "max_players": "50", "difficulty": "peaceful", "gamemode": "creative",
            "pvp": "false", "online_mode": "true", "port": "25565",
            "view_distance": "16", "simulation_distance": "12",
            "spawn_protection": "0", "allow_nether": "true",
            "allow_flight": "true", "command_blocks": "true",
            "spawn_monsters": "false", "spawn_animals": "true",
            "spawn_npcs": "true", "generate_structures": "true",
            "level_type": "minecraft:flat", "seed": "",
            "motd": "Creative Build Server", "max_tick_time": "60000",
            "op_permission_level": "4", "entity_broadcast_range": "100",
            "player_idle_timeout": "0", "hardcore": "false",
            "whitelist": "false", "max_world_size": "29999984"
        }
    },
    "preset_minigames": {
        "name": "🎮 Мини-игры",
        "desc": "Сервер для мини-игр и PvP",
        "settings": {
            "version": "1.20.1", "loader": "Fabric", "ram": "4096",
            "max_players": "100", "difficulty": "normal", "gamemode": "adventure",
            "pvp": "true", "online_mode": "true", "port": "25565",
            "view_distance": "8", "simulation_distance": "6",
            "spawn_protection": "16", "allow_nether": "false",
            "allow_flight": "true", "command_blocks": "true",
            "spawn_monsters": "false", "spawn_animals": "false",
            "spawn_npcs": "false", "generate_structures": "false",
            "level_type": "minecraft:flat", "seed": "",
            "motd": "MiniGames Server", "max_tick_time": "60000",
            "op_permission_level": "4", "entity_broadcast_range": "80",
            "player_idle_timeout": "30", "hardcore": "false",
            "whitelist": "false", "max_world_size": "29999984"
        }
    },
    "preset_modded_forge": {
        "name": "⚙️ Моды (Forge)",
        "desc": "Сервер для модпаков на Forge",
        "settings": {
            "version": "1.20.1", "loader": "Forge", "ram": "6144",
            "max_players": "20", "difficulty": "normal", "gamemode": "survival",
            "pvp": "true", "online_mode": "false", "port": "25565",
            "view_distance": "8", "simulation_distance": "6",
            "spawn_protection": "0", "allow_nether": "true",
            "allow_flight": "true", "command_blocks": "true",
            "spawn_monsters": "true", "spawn_animals": "true",
            "spawn_npcs": "true", "generate_structures": "true",
            "level_type": "minecraft:normal", "seed": "",
            "motd": "Modded Forge Server", "max_tick_time": "-1",
            "op_permission_level": "4", "entity_broadcast_range": "100",
            "player_idle_timeout": "0", "hardcore": "false",
            "whitelist": "false", "max_world_size": "29999984"
        }
    },
    "preset_old_school": {
        "name": "🕹️ Олдскул 1.12.2",
        "desc": "Классический сервер на старой версии",
        "settings": {
            "version": "1.12.2", "loader": "Forge", "ram": "1024",
            "max_players": "20", "difficulty": "normal", "gamemode": "survival",
            "pvp": "true", "online_mode": "true", "port": "25565",
            "view_distance": "10", "simulation_distance": "10",
            "spawn_protection": "16", "allow_nether": "true",
            "allow_flight": "false", "command_blocks": "false",
            "spawn_monsters": "true", "spawn_animals": "true",
            "spawn_npcs": "true", "generate_structures": "true",
            "level_type": "minecraft:normal", "seed": "",
            "motd": "Old School 1.12.2", "max_tick_time": "60000",
            "op_permission_level": "4", "entity_broadcast_range": "100",
            "player_idle_timeout": "0", "hardcore": "false",
            "whitelist": "false", "max_world_size": "29999984"
        }
    }
}

def parse_version(version_str):
    try:
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except:
        return (1, 0, 0)

def is_fabric_supported(version):
    return parse_version(version) >= (1, 14, 0)

def get_java_for_version(mc_version):
    parsed = parse_version(mc_version)
    if parsed >= (1, 21, 0):
        return 21, "Java 21"
    elif parsed >= (1, 18, 0):
        return 17, "Java 17"
    elif parsed >= (1, 17, 0):
        return 16, "Java 16"
    else:
        return 8, "Java 8"

async def download_with_retry(session, url, progress_callback=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                total_size = int(response.headers.get('Content-Length', 0))
                if total_size > 0 and progress_callback:
                    await progress_callback(f"⏳ Загрузка {total_size // (1024*1024)}MB...")
                downloaded = 0
                chunks = []
                chunk_size = 1024 * 1024
                last_progress = 0
                async for chunk in response.content.iter_chunked(chunk_size):
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    if total_size > 0 and progress_callback:
                        progress = int((downloaded / total_size) * 100)
                        if progress >= last_progress + 10:
                            await progress_callback(f"⏳ {progress}% ({downloaded // (1024*1024)}/{total_size // (1024*1024)}MB)")
                            last_progress = progress
                return b''.join(chunks)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            if attempt < max_retries - 1:
                if progress_callback:
                    await progress_callback(f"⚠️ Повтор {attempt+2}/{max_retries}...")
                await asyncio.sleep(3)
                continue
            else:
                raise Exception(f"Не удалось загрузить после {max_retries} попыток")
    raise Exception("Не удалось загрузить файл")

async def get_server_jar(loader, version, progress_callback=None):
    try:
        if not loader:
            loader = "fabric"
        if not version:
            version = "1.20.1"
        loader = loader.lower()
        timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=900)
        connector = aiohttp.TCPConnector(limit=1, limit_per_host=1, ttl_dns_cache=300, force_close=False)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            if loader == "fabric":
                if not is_fabric_supported(version):
                    raise Exception(
                        f"❌ Fabric не поддерживает версию {version}\n\n"
                        f"💡 Fabric работает только начиная с версии 1.14\n\n"
                        f"Используйте Forge для версий ниже 1.14"
                    )
                if progress_callback:
                    await progress_callback("⏳ Поиск Fabric...")
                async with session.get("https://meta.fabricmc.net/v2/versions/loader") as lr:
                    if lr.status == 200:
                        loaders = await lr.json()
                        if loaders:
                            loader_version = loaders[0]['version']
                            async with session.get("https://meta.fabricmc.net/v2/versions/installer") as ir:
                                if ir.status == 200:
                                    installers = await ir.json()
                                    if installers:
                                        installer_version = installers[0]['version']
                                        url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
                                        jar_data = await download_with_retry(session, url, progress_callback)
                                        return jar_data, f"fabric-server-{version}.jar"
                raise Exception(f"Fabric не поддерживает {version}")
            elif loader == "forge":
                if progress_callback:
                    await progress_callback("⏳ Поиск Forge...")
                async with session.get("https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        promos = data.get('promos', {})
                        forge_version = promos.get(f"{version}-latest") or promos.get(f"{version}-recommended")
                        if forge_version:
                            major = int(version.split('.')[1]) if len(version.split('.')) > 1 else 0
                            full_version = f"{version}-{forge_version}"
                            if 7 <= major <= 12:
                                url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{full_version}/forge-{full_version}-universal.jar"
                                try:
                                    jar_data = await download_with_retry(session, url, progress_callback)
                                    return jar_data, f"forge-{version}-universal.jar"
                                except:
                                    if version == "1.7.10":
                                        fvd = f"{version}-{forge_version}-{version}"
                                        url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{fvd}/forge-{fvd}-universal.jar"
                                        jar_data = await download_with_retry(session, url, progress_callback)
                                        return jar_data, f"forge-{version}-universal.jar"
                            else:
                                url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{full_version}/forge-{full_version}-installer.jar"
                                if progress_callback:
                                    await progress_callback("⚠️ Forge 1.13+ требует запуска installer")
                                jar_data = await download_with_retry(session, url, progress_callback)
                                return jar_data, f"forge-{version}-installer.jar"
                        raise Exception(f"Forge не поддерживает {version}")
    except Exception as e:
        raise Exception(str(e))
    return None, None

def generate_server_properties(settings):
    return f"""eula=true
enable-jmx-monitoring=false
rcon.port=25575
level-seed={settings.get('seed', '')}
gamemode={settings.get('gamemode', 'survival')}
enable-command-block={settings.get('command_blocks', 'false')}
enable-query=false
generator-settings={{}}
enforce-secure-profile=true
level-name=world
motd={settings.get('motd', 'A Minecraft Server')}
query.port=25565
pvp={settings.get('pvp', 'true')}
generate-structures={settings.get('generate_structures', 'true')}
max-chained-neighbor-updates=1000000
difficulty={settings.get('difficulty', 'normal')}
network-compression-threshold=256
max-tick-time={settings.get('max_tick_time', '60000')}
require-resource-pack=false
use-native-transport=true
max-players={settings.get('max_players', '20')}
online-mode={settings.get('online_mode', 'true')}
enable-status=true
allow-flight={settings.get('allow_flight', 'false')}
initial-disabled-packs=
broadcast-rcon-to-ops=true
view-distance={settings.get('view_distance', '10')}
server-ip=
resource-pack-prompt=
allow-nether={settings.get('allow_nether', 'true')}
server-port={settings.get('port', '25565')}
enable-rcon=false
sync-chunk-writes=true
op-permission-level={settings.get('op_permission_level', '4')}
prevent-proxy-connections=false
hide-online-players=false
resource-pack=
entity-broadcast-range-percentage={settings.get('entity_broadcast_range', '100')}
simulation-distance={settings.get('simulation_distance', '10')}
rcon.password=
player-idle-timeout={settings.get('player_idle_timeout', '0')}
force-gamemode=false
rate-limit=0
hardcore={settings.get('hardcore', 'false')}
white-list={settings.get('whitelist', 'false')}
broadcast-console-to-ops=true
spawn-npcs={settings.get('spawn_npcs', 'true')}
spawn-animals={settings.get('spawn_animals', 'true')}
function-permission-level=2
initial-enabled-packs=vanilla
level-type={settings.get('level_type', 'minecraft:normal')}
text-filtering-config=
spawn-monsters={settings.get('spawn_monsters', 'true')}
enforce-whitelist=false
spawn-protection={settings.get('spawn_protection', '16')}
resource-pack-sha1=
max-world-size={settings.get('max_world_size', '29999984')}
"""

def generate_start_script(jar_name, ram):
    start_sh = f"#!/bin/bash\njava -Xms{ram}M -Xmx{ram}M -XX:+UseG1GC -jar {jar_name} nogui"
    start_bat = f"@echo off\njava -Xms{ram}M -Xmx{ram}M -XX:+UseG1GC -jar {jar_name} nogui\npause"
    return start_sh, start_bat

def create_readme(settings, jar_name):
    return f"""MINECRAFT SERVER {settings.get('version')}
Загрузчик: {settings.get('loader')}

ЗАПУСК:
Windows: start.bat
Linux: ./start.sh

Порт: {settings.get('port')}
RAM: {settings.get('ram')}MB
"""

def create_zip_sync(temp_path, jar_data, jar_name, settings):
    with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.writestr(jar_name, jar_data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
        zf.writestr('server.properties', generate_server_properties(settings))
        zf.writestr('eula.txt', 'eula=true')
        start_sh, start_bat = generate_start_script(jar_name, settings.get('ram', '2048'))
        zf.writestr('start.sh', start_sh)
        zf.writestr('start.bat', start_bat)
        zf.writestr('README.txt', create_readme(settings, jar_name))
        zf.writestr('ops.json', '[]')
        zf.writestr('whitelist.json', '[]')

async def create_server_package(user_id, progress_message):
    settings = user_settings.get(user_id, {})
    try:
        async def update_progress(text):
            try:
                await progress_message.edit_text(text)
            except:
                pass
        loader = settings.get('loader') or 'Fabric'
        version = settings.get('version') or '1.20.1'
        jar_data, jar_name = await get_server_jar(loader, version, update_progress)
        if not jar_data:
            raise Exception("Не удалось загрузить серверное ядро")
        original_size = len(jar_data)
        await update_progress(f"🗜️ Сжатие {original_size // (1024*1024)}MB...")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_path = temp_file.name
        temp_file.close()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_zip_sync, temp_path, jar_data, jar_name, settings)
        archive_size = os.path.getsize(temp_path)
        compression_ratio = 100 - (archive_size / original_size * 100)
        if archive_size > 49.5 * 1024 * 1024:
            os.unlink(temp_path)
            raise Exception(
                f"Архив {archive_size / (1024*1024):.1f}MB превышает лимит 50MB\n\n"
                f"💡 Попробуйте:\n"
                f"• Более старую версию (1.12.2, 1.8.8, 1.7.10)\n"
                f"• Fabric вместо Forge для новых версий"
            )
        await update_progress(f"✅ Архив готов: {archive_size / (1024*1024):.1f}MB")
        return temp_path, archive_size, original_size, compression_ratio
    except Exception as e:
        traceback.print_exc()
        raise Exception(str(e))

def get_default_settings():
    return {
        "version": "1.20.1", "loader": "Fabric", "max_players": "20",
        "difficulty": "normal", "gamemode": "survival", "pvp": "true",
        "online_mode": "true", "port": "25565", "view_distance": "10",
        "simulation_distance": "10", "spawn_protection": "16",
        "allow_nether": "true", "allow_flight": "false", "command_blocks": "false",
        "spawn_monsters": "true", "spawn_animals": "true", "spawn_npcs": "true",
        "generate_structures": "true", "level_type": "minecraft:normal", "seed": "",
        "motd": "A Minecraft Server", "ram": "2048", "max_tick_time": "60000",
        "op_permission_level": "4", "entity_broadcast_range": "100",
        "player_idle_timeout": "0", "hardcore": "false", "whitelist": "false",
        "max_world_size": "29999984"
    }

def format_config_summary(settings):
    difficulty_names = {"peaceful": "Мирная", "easy": "Лёгкая", "normal": "Обычная", "hard": "Тяжёлая"}
    gamemode_names = {"survival": "Выживание", "creative": "Творческий", "adventure": "Приключение", "spectator": "Наблюдатель"}
    level_type_names = {
        "minecraft:normal": "Стандартный", "minecraft:flat": "Плоский",
        "minecraft:large_biomes": "Большие биомы", "minecraft:amplified": "Усиленный"
    }
    return (
        f"🎯 Версия: {settings.get('version', '1.20.1')}\n"
        f"⚡ Загрузчик: {settings.get('loader', 'Fabric')}\n"
        f"💾 Память: {settings.get('ram', '2048')} MB\n"
        f"👥 Игроков: {settings.get('max_players', '20')}\n"
        f"⚔️ Сложность: {difficulty_names.get(settings.get('difficulty', 'normal'), settings.get('difficulty', 'normal'))}\n"
        f"🎮 Режим: {gamemode_names.get(settings.get('gamemode', 'survival'), settings.get('gamemode', 'survival'))}\n"
        f"🌐 Порт: {settings.get('port', '25565')}\n"
        f"👁️ Прорисовка: {settings.get('view_distance', '10')} чанков\n"
        f"🔮 Симуляция: {settings.get('simulation_distance', '10')} чанков\n"
        f"🗺️ Тип мира: {level_type_names.get(settings.get('level_type', 'minecraft:normal'), settings.get('level_type', 'minecraft:normal'))}"
    )

def build_config_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Версия и загрузчик", callback_data="cfg_version_loader")],
        [InlineKeyboardButton("👥 Игроки и режим", callback_data="cfg_players_mode")],
        [InlineKeyboardButton("🌍 Мир и генерация", callback_data="cfg_world")],
        [InlineKeyboardButton("⚙️ Производительность", callback_data="cfg_performance")],
        [InlineKeyboardButton("🔒 Безопасность", callback_data="cfg_security")],
        [InlineKeyboardButton("🚀 Создать сервер", callback_data="create_server")],
        [InlineKeyboardButton("🔙 Назад", callback_data="action_menu")]
    ])

async def edit_menu(bot, chat_id, message_id, text, keyboard):
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception:
        pass

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_settings:
        user_settings[user_id] = get_default_settings()
    user_states[user_id] = None
    user_creating_server[user_id] = False
    keyboard = [[InlineKeyboardButton("📋 Меню", callback_data="action_menu")]]
    await update.message.reply_text(
        "🎮 Minecraft Server Builder\n\n"
        "✨ Поддерживаются загрузчики: Fabric, Forge\n\n"
        "Бот создаёт готовые архивы сервера Minecraft.\n"
        "Настройте конфигурацию или выберите шаблон -\n"
        "и сервер будет собран автоматически.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_action_menu(query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Быстрые шаблоны", callback_data="presets_menu")],
        [InlineKeyboardButton("🛠️ Конфигурация", callback_data="config_menu")],
        [InlineKeyboardButton("☕ Java - инструкция", callback_data="java_info")],
        [InlineKeyboardButton("📖 Помощь", callback_data="help_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    await query.edit_message_text("📋 Выберите действие:", reply_markup=keyboard)

async def show_config_menu(query, user_id):
    curr = user_settings.get(user_id, get_default_settings())
    summary = format_config_summary(curr)
    await query.edit_message_text(
        f"🛠️ Конфигурация сервера\n\n{summary}",
        reply_markup=build_config_keyboard()
    )
    user_menu_message[user_id] = {
        "chat_id": query.message.chat_id,
        "message_id": query.message.message_id
    }

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_settings:
        user_settings[user_id] = get_default_settings()

    if data == "main_menu":
        user_states[user_id] = None
        user_menu_message.pop(user_id, None)
        await query.edit_message_text(
            "🎮 Minecraft Server Builder\n\n"
            "✨ Поддерживаются загрузчики: Fabric, Forge\n\n"
            "Бот создаёт готовые архивы сервера Minecraft.\n"
            "Настройте конфигурацию или выберите шаблон -\n"
            "и сервер будет собран автоматически.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Меню", callback_data="action_menu")]])
        )

    elif data == "action_menu":
        user_states[user_id] = None
        user_menu_message.pop(user_id, None)
        await show_action_menu(query)

    # ───────────────── JAVA ─────────────────
    elif data == "java_info":
        user_menu_message.pop(user_id, None)
        text = (
            "☕ Java для Minecraft\n\n"
            "Minecraft 1.21+      →  Java 21\n"
            "Minecraft 1.18–1.20  →  Java 17\n"
            "Minecraft 1.17       →  Java 16\n"
            "Minecraft 1.7–1.16   →  Java 8\n\n"
            "Скачать Java (Eclipse Temurin - бесплатно, без рекламы):"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("☕ Java 21", url="https://adoptium.net/temurin/releases/?version=21")],
            [InlineKeyboardButton("☕ Java 17", url="https://adoptium.net/temurin/releases/?version=17")],
            [InlineKeyboardButton("☕ Java 8",  url="https://adoptium.net/temurin/releases/?version=8")],
            [InlineKeyboardButton("🔙 Назад", callback_data="action_menu")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard)

    # ───────────────── ПОМОЩЬ ─────────────────
    elif data == "help_menu":
        user_menu_message.pop(user_id, None)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Частые ошибки", callback_data="help_errors")],
            [InlineKeyboardButton("💡 Советы", callback_data="help_tips")],
            [InlineKeyboardButton("🌐 Как подключиться к серверу", callback_data="help_connect")],
            [InlineKeyboardButton("🔙 Назад", callback_data="action_menu")]
        ])
        await query.edit_message_text("📖 Помощь - выберите раздел:", reply_markup=keyboard)

    elif data == "help_errors":
        text = (
            "❌ Частые ошибки\n\n"
            "«java» не является командой\n"
            "→ Java не установлена или не добавлена в PATH. Установите Java и перезапустите терминал.\n\n"
            "Error: Could not find or load main class\n"
            "→ Скорее всего не та версия Java. Проверьте - какая нужна для вашей версии Minecraft.\n\n"
            "Forge не поддерживает эту версию\n"
            "→ Forge есть не для каждой версии. Попробуйте соседнюю (например 1.20.1 вместо 1.20.3).\n\n"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="help_menu")]])
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == "help_tips":
        text = (
            "💡 Советы\n\n"
            "RAM\n"
            "→ Для обычного сервера хватает 4GB. Если играете с модами - берите от 6GB.\n\n"
            "Fabric vs Forge\n"
            "→ Fabric быстрее и легче, хорош для новых версий. Forge нужен для больших модпаков и старых версий.\n\n"
            "Online Mode (проверка лицензии)\n"
            "→ Если играете с пиратками - выключите. Если все с лицензией - лучше оставить включённым, иначе любой зайдёт под чужим ником.\n\n"
            "Прорисовка\n"
            "→ Чем меньше - тем легче серверу. На слабых машинах ставьте 6–8 чанков.\n\n"
            "Сид\n"
            "→ Можно оставить пустым - мир сгенерируется случайно. Или ввести любое число/слово для конкретного мира."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="help_menu")]])
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == "help_connect":
        text = (
            "🌐 Как подключиться к серверу\n\n"
            "Локальная сеть (один роутер)\n"
            "→ Узнайте локальный IP компьютера (ipconfig в консоли (cmd) на Windows, ip на Linux). В Minecraft вводите этот IP и порт, например: 192.168.1.5:25565. Или попробуйте 127.0.1\n\n"
            "Через интернет\n"
            "→ Нужен внешний IP (можно узнать на 2ip.ru). Также нужно пробросить порт 25565 в настройках роутера (раздел Port Forwarding)."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="help_menu")]])
        await query.edit_message_text(text, reply_markup=keyboard)

    # ───────────────── ПРЕСЕТЫ ─────────────────
    elif data == "presets_menu":
        user_menu_message.pop(user_id, None)
        keyboard = []
        for preset_id, preset in PRESETS.items():
            keyboard.append([InlineKeyboardButton(preset["name"], callback_data=preset_id)])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="action_menu")])
        await query.edit_message_text(
            "📦 Быстрые шаблоны\n\n"
            "Выберите готовый пресет - настройки применятся автоматически.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("preset_") and not data.startswith("apply_"):
        preset = PRESETS.get(data)
        if not preset:
            await show_action_menu(query)
            return
        s = preset["settings"]
        difficulty_names = {"peaceful": "Мирная", "easy": "Лёгкая", "normal": "Обычная", "hard": "Тяжёлая"}
        gamemode_names = {"survival": "Выживание", "creative": "Творческий", "adventure": "Приключение", "spectator": "Наблюдатель"}
        info = (
            f"{preset['name']}\n"
            f"{preset['desc']}\n\n"
            f"🎯 Версия: {s['version']}\n"
            f"⚡ Загрузчик: {s['loader']}\n"
            f"💾 Память: {s['ram']} MB\n"
            f"👥 Игроков: {s['max_players']}\n"
            f"⚔️ Сложность: {difficulty_names.get(s['difficulty'], s['difficulty'])}\n"
            f"🎮 Режим: {gamemode_names.get(s['gamemode'], s['gamemode'])}\n"
            f"💀 Хардкор: {'Да' if s['hardcore'] == 'true' else 'Нет'}\n"
            f"📋 Вайтлист: {'Да' if s['whitelist'] == 'true' else 'Нет'}"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Применить и создать сервер", callback_data=f"apply_create_{data}")],
            [InlineKeyboardButton("🛠️ Применить и настроить", callback_data=f"apply_edit_{data}")],
            [InlineKeyboardButton("🔙 Назад к шаблонам", callback_data="presets_menu")]
        ])
        await query.edit_message_text(info, reply_markup=keyboard)

    elif data.startswith("apply_create_preset_"):
        preset_id = data.replace("apply_create_", "")
        preset = PRESETS.get(preset_id)
        if preset:
            user_settings[user_id] = dict(preset["settings"])
        if user_creating_server.get(user_id, False):
            await query.answer("⚠️ Сервер уже создаётся!", show_alert=True)
            return
        user_creating_server[user_id] = True
        msg = await query.edit_message_text("⏳ Запуск...")
        await _do_create_server(user_id, msg, query, context)

    elif data.startswith("apply_edit_preset_"):
        preset_id = data.replace("apply_edit_", "")
        preset = PRESETS.get(preset_id)
        if preset:
            user_settings[user_id] = dict(preset["settings"])
        await show_config_menu(query, user_id)

    elif data == "config_menu":
        user_states[user_id] = None
        await show_config_menu(query, user_id)

    elif data == "cfg_version_loader":
        user_states[user_id] = None
        curr = user_settings.get(user_id, get_default_settings())
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🎯 Версия: {curr.get('version', '1.20.1')}", callback_data="set_version")],
            [InlineKeyboardButton(f"⚡ Загрузчик: {curr.get('loader', 'Fabric')}", callback_data="set_loader")],
            [InlineKeyboardButton(f"💾 Память: {curr.get('ram', '2048')} MB", callback_data="set_ram")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await query.edit_message_text(
            "🎯 Версия и загрузчик\n\n⚠️ Fabric доступен только с версии 1.14 и выше.",
            reply_markup=keyboard
        )
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "cfg_players_mode":
        user_states[user_id] = None
        curr = user_settings.get(user_id, get_default_settings())
        difficulty_names = {"peaceful": "Мирная", "easy": "Лёгкая", "normal": "Обычная", "hard": "Тяжёлая"}
        gamemode_names = {"survival": "Выживание", "creative": "Творческий", "adventure": "Приключение", "spectator": "Наблюдатель"}
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"👥 Макс. игроков: {curr.get('max_players', '20')}", callback_data="set_max_players")],
            [InlineKeyboardButton(f"⚔️ Сложность: {difficulty_names.get(curr.get('difficulty','normal'), curr.get('difficulty','normal'))}", callback_data="set_difficulty")],
            [InlineKeyboardButton(f"🎮 Режим игры: {gamemode_names.get(curr.get('gamemode','survival'), curr.get('gamemode','survival'))}", callback_data="set_gamemode")],
            [InlineKeyboardButton(f"⚔️ PvP: {'Включено' if curr.get('pvp','true')=='true' else 'Выключено'}", callback_data="set_pvp")],
            [InlineKeyboardButton(f"🔐 Проверка лицензии: {'Включена' if curr.get('online_mode','true')=='true' else 'Выключена'}", callback_data="set_online_mode")],
            [InlineKeyboardButton(f"🌐 Порт: {curr.get('port', '25565')}", callback_data="set_port")],
            [InlineKeyboardButton("📝 Описание сервера (MOTD)", callback_data="input_motd")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await query.edit_message_text("👥 Игроки и режим игры:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "cfg_world":
        user_states[user_id] = None
        curr = user_settings.get(user_id, get_default_settings())
        level_type_names = {
            "minecraft:normal": "Стандартный", "minecraft:flat": "Плоский",
            "minecraft:large_biomes": "Большие биомы", "minecraft:amplified": "Усиленный"
        }
        def yn(v, t='true'): return "Да" if v == t else "Нет"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"👁️ Прорисовка: {curr.get('view_distance','10')} чанков", callback_data="set_view_distance")],
            [InlineKeyboardButton(f"🔮 Симуляция: {curr.get('simulation_distance','10')} чанков", callback_data="set_simulation_distance")],
            [InlineKeyboardButton(f"🏰 Защита спавна: {curr.get('spawn_protection','16')} блоков", callback_data="set_spawn_protection")],
            [InlineKeyboardButton(f"🔥 Незер: {yn(curr.get('allow_nether','true'))}", callback_data="set_nether")],
            [InlineKeyboardButton(f"👹 Монстры: {yn(curr.get('spawn_monsters','true'))}", callback_data="set_monsters")],
            [InlineKeyboardButton(f"🐷 Животные: {yn(curr.get('spawn_animals','true'))}", callback_data="set_animals")],
            [InlineKeyboardButton(f"👨‍🌾 Жители (NPC): {yn(curr.get('spawn_npcs','true'))}", callback_data="set_npcs")],
            [InlineKeyboardButton(f"🏛️ Структуры: {yn(curr.get('generate_structures','true'))}", callback_data="set_structures")],
            [InlineKeyboardButton(f"🗺️ Тип мира: {level_type_names.get(curr.get('level_type','minecraft:normal'), curr.get('level_type','minecraft:normal'))}", callback_data="set_level_type")],
            [InlineKeyboardButton(f"🌱 Сид: {curr.get('seed','') or 'Случайный'}", callback_data="input_seed")],
            [InlineKeyboardButton(f"📐 Макс. размер мира: {curr.get('max_world_size','29999984')}", callback_data="set_max_world_size")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await query.edit_message_text("🌍 Мир и генерация:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "cfg_performance":
        user_states[user_id] = None
        curr = user_settings.get(user_id, get_default_settings())
        tick = curr.get('max_tick_time', '60000')
        tick_label = "Безлимит" if tick == '-1' else f"{tick} мс"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✈️ Полёт: {'Разрешён' if curr.get('allow_flight','false')=='true' else 'Запрещён'}", callback_data="set_flight")],
            [InlineKeyboardButton(f"🎛️ Командные блоки: {'Включены' if curr.get('command_blocks','false')=='true' else 'Выключены'}", callback_data="set_cmd_blocks")],
            [InlineKeyboardButton(f"⏱️ Макс. время тика: {tick_label}", callback_data="set_max_tick_time")],
            [InlineKeyboardButton(f"📡 Дальность сущностей: {curr.get('entity_broadcast_range','100')}%", callback_data="set_entity_range")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await query.edit_message_text("⚙️ Производительность:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "cfg_security":
        user_states[user_id] = None
        curr = user_settings.get(user_id, get_default_settings())
        idle = curr.get('player_idle_timeout', '0')
        idle_label = f"{idle} мин" if idle != '0' else "Выключен"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💀 Хардкор: {'Включён' if curr.get('hardcore','false')=='true' else 'Выключен'}", callback_data="set_hardcore")],
            [InlineKeyboardButton(f"📋 Белый список: {'Включён' if curr.get('whitelist','false')=='true' else 'Выключен'}", callback_data="set_whitelist")],
            [InlineKeyboardButton(f"👑 Уровень прав оператора: {curr.get('op_permission_level','4')}", callback_data="set_op_level")],
            [InlineKeyboardButton(f"💤 Тайм-аут AFK: {idle_label}", callback_data="set_idle_timeout")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await query.edit_message_text("🔒 Безопасность:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_version":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1.21.4", callback_data="version_1.21.4"), InlineKeyboardButton("1.21.3", callback_data="version_1.21.3")],
            [InlineKeyboardButton("1.21.1", callback_data="version_1.21.1"), InlineKeyboardButton("1.21", callback_data="version_1.21")],
            [InlineKeyboardButton("1.20.6", callback_data="version_1.20.6"), InlineKeyboardButton("1.20.4", callback_data="version_1.20.4")],
            [InlineKeyboardButton("1.20.1 ✅", callback_data="version_1.20.1"), InlineKeyboardButton("1.19.4", callback_data="version_1.19.4")],
            [InlineKeyboardButton("1.18.2", callback_data="version_1.18.2"), InlineKeyboardButton("1.16.5 💾", callback_data="version_1.16.5")],
            [InlineKeyboardButton("1.12.2 💾", callback_data="version_1.12.2"), InlineKeyboardButton("1.8.8 💾", callback_data="version_1.8.8")],
            [InlineKeyboardButton("1.7.10 💾", callback_data="version_1.7.10"), InlineKeyboardButton("✏️ Своя версия", callback_data="input_version")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_version_loader")]
        ])
        await query.edit_message_text(
            "🎯 Выберите версию Minecraft:\n\n💾 = Меньше размер архива\n✅ = Рекомендуется\n⚠️ Fabric доступен только с 1.14+",
            reply_markup=keyboard
        )
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_loader":
        version = user_settings[user_id].get('version', '1.20.1')
        fabric_ok = is_fabric_supported(version)
        rows = []
        if fabric_ok:
            rows.append([InlineKeyboardButton("Fabric 💾 (рекомендуется для новых версий)", callback_data="loader_fabric")])
        else:
            rows.append([InlineKeyboardButton("⚠️ Fabric недоступен для этой версии", callback_data="loader_fabric_blocked")])
        rows.append([InlineKeyboardButton("Forge (поддерживает все версии)", callback_data="loader_forge")])
        rows.append([InlineKeyboardButton("🔙 Назад", callback_data="cfg_version_loader")])
        await query.edit_message_text(
            f"⚡ Выберите загрузчик:\n\nТекущая версия: {version}\n"
            f"{'✅ Fabric поддерживается' if fabric_ok else '❌ Fabric не поддерживает версии ниже 1.14'}",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_ram":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("512 MB", callback_data="ram_512"), InlineKeyboardButton("1 GB", callback_data="ram_1024")],
            [InlineKeyboardButton("2 GB ✅", callback_data="ram_2048"), InlineKeyboardButton("4 GB", callback_data="ram_4096")],
            [InlineKeyboardButton("8 GB", callback_data="ram_8192"), InlineKeyboardButton("16 GB", callback_data="ram_16384")],
            [InlineKeyboardButton("✏️ Ввести вручную (MB)", callback_data="input_ram")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_version_loader")]
        ])
        await query.edit_message_text("💾 Выберите объём оперативной памяти:\n\n✅ = Рекомендуется для большинства серверов", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_max_players":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("5", callback_data="maxplayers_5"), InlineKeyboardButton("10", callback_data="maxplayers_10")],
            [InlineKeyboardButton("20 ✅", callback_data="maxplayers_20"), InlineKeyboardButton("50", callback_data="maxplayers_50")],
            [InlineKeyboardButton("100", callback_data="maxplayers_100"), InlineKeyboardButton("200", callback_data="maxplayers_200")],
            [InlineKeyboardButton("✏️ Ввести вручную", callback_data="input_maxplayers")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_players_mode")]
        ])
        await query.edit_message_text("👥 Максимальное количество игроков:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_difficulty":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("☮️ Мирная", callback_data="difficulty_peaceful")],
            [InlineKeyboardButton("😊 Лёгкая", callback_data="difficulty_easy")],
            [InlineKeyboardButton("😐 Обычная ✅", callback_data="difficulty_normal")],
            [InlineKeyboardButton("😈 Тяжёлая", callback_data="difficulty_hard")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_players_mode")]
        ])
        await query.edit_message_text("⚔️ Сложность:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_gamemode":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⛏️ Выживание ✅", callback_data="gamemode_survival")],
            [InlineKeyboardButton("🎨 Творческий", callback_data="gamemode_creative")],
            [InlineKeyboardButton("🗺️ Приключение", callback_data="gamemode_adventure")],
            [InlineKeyboardButton("👻 Наблюдатель", callback_data="gamemode_spectator")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_players_mode")]
        ])
        await query.edit_message_text("🎮 Режим игры по умолчанию:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_pvp":
        await _toggle_menu(query, user_id, "pvp", "⚔️ PvP (бои между игроками)", "cfg_players_mode")
    elif data == "set_online_mode":
        await _toggle_menu(query, user_id, "online_mode", "🔐 Проверка лицензии (Online Mode)", "cfg_players_mode")
    elif data == "set_nether":
        await _toggle_menu(query, user_id, "allow_nether", "🔥 Незер", "cfg_world")
    elif data == "set_monsters":
        await _toggle_menu(query, user_id, "spawn_monsters", "👹 Спавн монстров", "cfg_world")
    elif data == "set_animals":
        await _toggle_menu(query, user_id, "spawn_animals", "🐷 Спавн животных", "cfg_world")
    elif data == "set_npcs":
        await _toggle_menu(query, user_id, "spawn_npcs", "👨‍🌾 Спавн жителей (NPC)", "cfg_world")
    elif data == "set_structures":
        await _toggle_menu(query, user_id, "generate_structures", "🏛️ Генерация структур", "cfg_world")
    elif data == "set_flight":
        await _toggle_menu(query, user_id, "allow_flight", "✈️ Полёт", "cfg_performance")
    elif data == "set_cmd_blocks":
        await _toggle_menu(query, user_id, "command_blocks", "🎛️ Командные блоки", "cfg_performance")
    elif data == "set_hardcore":
        await _toggle_menu(query, user_id, "hardcore", "💀 Хардкор режим", "cfg_security")
    elif data == "set_whitelist":
        await _toggle_menu(query, user_id, "whitelist", "📋 Белый список", "cfg_security")

    elif data == "set_level_type":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌄 Стандартный ✅", callback_data="leveltype_minecraft:normal")],
            [InlineKeyboardButton("🟫 Плоский", callback_data="leveltype_minecraft:flat")],
            [InlineKeyboardButton("🌿 Большие биомы", callback_data="leveltype_minecraft:large_biomes")],
            [InlineKeyboardButton("⛰️ Усиленный рельеф", callback_data="leveltype_minecraft:amplified")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_world")]
        ])
        await query.edit_message_text("🗺️ Тип генерации мира:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_op_level":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1 - Обход защиты спавна", callback_data="oplevel_1")],
            [InlineKeyboardButton("2 - Команды и блоки", callback_data="oplevel_2")],
            [InlineKeyboardButton("3 - Управление игроками", callback_data="oplevel_3")],
            [InlineKeyboardButton("4 - Полные права ✅", callback_data="oplevel_4")],
            [InlineKeyboardButton("🔙 Назад", callback_data="cfg_security")]
        ])
        await query.edit_message_text("👑 Уровень прав оператора:", reply_markup=keyboard)
        user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

    elif data == "set_port":
        user_states[user_id] = ("input_port", "cfg_players_mode")
        await _ask_input(query, context, user_id, "Введите порт сервера (1–65535):")
    elif data == "set_view_distance":
        user_states[user_id] = ("input_viewdist", "cfg_world")
        await _ask_input(query, context, user_id, "Введите дальность прорисовки в чанках (2–32):")
    elif data == "set_simulation_distance":
        user_states[user_id] = ("input_simdist", "cfg_world")
        await _ask_input(query, context, user_id, "Введите дальность симуляции в чанках (2–32):")
    elif data == "set_spawn_protection":
        user_states[user_id] = ("input_spawnprot", "cfg_world")
        await _ask_input(query, context, user_id, "Введите радиус защиты спавна в блоках (0 = выключено):")
    elif data == "set_max_world_size":
        user_states[user_id] = ("input_max_world_size", "cfg_world")
        await _ask_input(query, context, user_id, "Введите максимальный размер мира в блоках (мин. 1000):")
    elif data == "set_max_tick_time":
        user_states[user_id] = ("input_max_tick", "cfg_performance")
        await _ask_input(query, context, user_id, "Введите макс. время тика в мс (60000 = стандарт, -1 = безлимит):")
    elif data == "set_entity_range":
        user_states[user_id] = ("input_entity_range", "cfg_performance")
        await _ask_input(query, context, user_id, "Введите дальность трансляции сущностей в % (10–1000):")
    elif data == "set_idle_timeout":
        user_states[user_id] = ("input_idle_timeout", "cfg_security")
        await _ask_input(query, context, user_id, "Введите тайм-аут AFK в минутах (0 = выключено):")
    elif data == "input_version":
        user_states[user_id] = ("input_version", "cfg_version_loader")
        await _ask_input(query, context, user_id, "Введите версию Minecraft (например: 1.20.1):")
    elif data == "input_ram":
        user_states[user_id] = ("input_ram", "cfg_version_loader")
        await _ask_input(query, context, user_id, "Введите объём RAM в MB (например: 2048):")
    elif data == "input_maxplayers":
        user_states[user_id] = ("input_maxplayers", "cfg_players_mode")
        await _ask_input(query, context, user_id, "Введите максимальное количество игроков:")
    elif data == "input_motd":
        user_states[user_id] = ("input_motd", "cfg_players_mode")
        await _ask_input(query, context, user_id, "Введите описание сервера (MOTD):")
    elif data == "input_seed":
        user_states[user_id] = ("input_seed", "cfg_world")
        await _ask_input(query, context, user_id, "Введите сид мира (или отправьте - для случайного):")

    elif data == "loader_fabric_blocked":
        await query.answer("❌ Fabric недоступен для версий ниже 1.14. Выберите Forge или смените версию.", show_alert=True)

    elif data.startswith("version_"):
        user_settings[user_id]["version"] = data[len("version_"):]
        info = user_menu_message.get(user_id)
        if info:
            curr = user_settings.get(user_id, get_default_settings())
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🎯 Версия: {curr.get('version', '1.20.1')}", callback_data="set_version")],
                [InlineKeyboardButton(f"⚡ Загрузчик: {curr.get('loader', 'Fabric')}", callback_data="set_loader")],
                [InlineKeyboardButton(f"💾 Память: {curr.get('ram', '2048')} MB", callback_data="set_ram")],
                [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
            ])
            await edit_menu(context.bot, info["chat_id"], info["message_id"],
                            "🎯 Версия и загрузчик\n\n⚠️ Fabric доступен только с версии 1.14 и выше.", keyboard)

    elif data.startswith("loader_") and data != "loader_fabric_blocked":
        loader_val = data[len("loader_"):].capitalize()
        if loader_val.lower() == "fabric" and not is_fabric_supported(user_settings[user_id].get("version", "1.20.1")):
            await query.answer("❌ Fabric не поддерживает версии ниже 1.14!", show_alert=True)
            return
        user_settings[user_id]["loader"] = loader_val
        info = user_menu_message.get(user_id)
        if info:
            curr = user_settings.get(user_id, get_default_settings())
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🎯 Версия: {curr.get('version', '1.20.1')}", callback_data="set_version")],
                [InlineKeyboardButton(f"⚡ Загрузчик: {curr.get('loader', 'Fabric')}", callback_data="set_loader")],
                [InlineKeyboardButton(f"💾 Память: {curr.get('ram', '2048')} MB", callback_data="set_ram")],
                [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
            ])
            await edit_menu(context.bot, info["chat_id"], info["message_id"],
                            "🎯 Версия и загрузчик\n\n⚠️ Fabric доступен только с версии 1.14 и выше.", keyboard)

    elif data.startswith("ram_"):
        user_settings[user_id]["ram"] = data[len("ram_"):]
        info = user_menu_message.get(user_id)
        if info:
            curr = user_settings.get(user_id, get_default_settings())
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🎯 Версия: {curr.get('version', '1.20.1')}", callback_data="set_version")],
                [InlineKeyboardButton(f"⚡ Загрузчик: {curr.get('loader', 'Fabric')}", callback_data="set_loader")],
                [InlineKeyboardButton(f"💾 Память: {curr.get('ram', '2048')} MB", callback_data="set_ram")],
                [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
            ])
            await edit_menu(context.bot, info["chat_id"], info["message_id"],
                            "🎯 Версия и загрузчик\n\n⚠️ Fabric доступен только с версии 1.14 и выше.", keyboard)

    elif data.startswith("maxplayers_"):
        user_settings[user_id]["max_players"] = data[len("maxplayers_"):]
        await _refresh_submenu(context.bot, user_id, "cfg_players_mode")

    elif data.startswith("difficulty_"):
        user_settings[user_id]["difficulty"] = data[len("difficulty_"):]
        await _refresh_submenu(context.bot, user_id, "cfg_players_mode")

    elif data.startswith("gamemode_"):
        user_settings[user_id]["gamemode"] = data[len("gamemode_"):]
        await _refresh_submenu(context.bot, user_id, "cfg_players_mode")

    elif data.startswith("toggle_"):
        parts = data[len("toggle_"):].rsplit("_", 1)
        setting_name = parts[0]
        value = parts[1]
        user_settings[user_id][setting_name] = value
        back_map = {
            "allow_nether": "cfg_world", "spawn_monsters": "cfg_world",
            "spawn_animals": "cfg_world", "spawn_npcs": "cfg_world",
            "generate_structures": "cfg_world",
            "allow_flight": "cfg_performance", "command_blocks": "cfg_performance",
            "hardcore": "cfg_security", "whitelist": "cfg_security",
            "pvp": "cfg_players_mode", "online_mode": "cfg_players_mode"
        }
        await _refresh_submenu(context.bot, user_id, back_map.get(setting_name, "config_menu"))

    elif data.startswith("leveltype_"):
        user_settings[user_id]["level_type"] = data[len("leveltype_"):]
        await _refresh_submenu(context.bot, user_id, "cfg_world")

    elif data.startswith("oplevel_"):
        user_settings[user_id]["op_permission_level"] = data[len("oplevel_"):]
        await _refresh_submenu(context.bot, user_id, "cfg_security")

    elif data == "create_server":
        if user_creating_server.get(user_id, False):
            await query.answer("⚠️ Сервер уже создаётся!", show_alert=True)
            return
        user_menu_message.pop(user_id, None)
        user_creating_server[user_id] = True
        msg = await query.edit_message_text("⏳ Запуск...")
        await _do_create_server(user_id, msg, query, context)

async def _ask_input(query, context, user_id, prompt_text):
    sent = await query.message.reply_text(
        f"✏️ {prompt_text}\n\nСообщение удалится через 3 секунды после отправки."
    )
    if context.user_data is not None:
        context.user_data["prompt_msg_id"] = sent.message_id
        context.user_data["prompt_chat_id"] = query.message.chat_id

async def _toggle_menu(query, user_id, setting_name, display_name, back_menu):
    curr_val = user_settings.get(user_id, {}).get(setting_name, 'false')
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ Включить{'  ◀' if curr_val == 'true' else ''}", callback_data=f"toggle_{setting_name}_true")],
        [InlineKeyboardButton(f"❌ Выключить{'  ◀' if curr_val == 'false' else ''}", callback_data=f"toggle_{setting_name}_false")],
        [InlineKeyboardButton("🔙 Назад", callback_data=back_menu)]
    ])
    await query.edit_message_text(f"{display_name}:", reply_markup=keyboard)
    user_menu_message[user_id] = {"chat_id": query.message.chat_id, "message_id": query.message.message_id}

async def _refresh_submenu(bot, user_id, menu_key):
    info = user_menu_message.get(user_id)
    if not info:
        return
    curr = user_settings.get(user_id, get_default_settings())

    if menu_key == "cfg_players_mode":
        difficulty_names = {"peaceful": "Мирная", "easy": "Лёгкая", "normal": "Обычная", "hard": "Тяжёлая"}
        gamemode_names = {"survival": "Выживание", "creative": "Творческий", "adventure": "Приключение", "spectator": "Наблюдатель"}
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"👥 Макс. игроков: {curr.get('max_players','20')}", callback_data="set_max_players")],
            [InlineKeyboardButton(f"⚔️ Сложность: {difficulty_names.get(curr.get('difficulty','normal'), curr.get('difficulty','normal'))}", callback_data="set_difficulty")],
            [InlineKeyboardButton(f"🎮 Режим игры: {gamemode_names.get(curr.get('gamemode','survival'), curr.get('gamemode','survival'))}", callback_data="set_gamemode")],
            [InlineKeyboardButton(f"⚔️ PvP: {'Включено' if curr.get('pvp','true')=='true' else 'Выключено'}", callback_data="set_pvp")],
            [InlineKeyboardButton(f"🔐 Проверка лицензии: {'Включена' if curr.get('online_mode','true')=='true' else 'Выключена'}", callback_data="set_online_mode")],
            [InlineKeyboardButton(f"🌐 Порт: {curr.get('port','25565')}", callback_data="set_port")],
            [InlineKeyboardButton("📝 Описание сервера (MOTD)", callback_data="input_motd")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await edit_menu(bot, info["chat_id"], info["message_id"], "👥 Игроки и режим игры:", keyboard)

    elif menu_key == "cfg_world":
        level_type_names = {
            "minecraft:normal": "Стандартный", "minecraft:flat": "Плоский",
            "minecraft:large_biomes": "Большие биомы", "minecraft:amplified": "Усиленный"
        }
        def yn(v, t='true'): return "Да" if v == t else "Нет"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"👁️ Прорисовка: {curr.get('view_distance','10')} чанков", callback_data="set_view_distance")],
            [InlineKeyboardButton(f"🔮 Симуляция: {curr.get('simulation_distance','10')} чанков", callback_data="set_simulation_distance")],
            [InlineKeyboardButton(f"🏰 Защита спавна: {curr.get('spawn_protection','16')} блоков", callback_data="set_spawn_protection")],
            [InlineKeyboardButton(f"🔥 Незер: {yn(curr.get('allow_nether','true'))}", callback_data="set_nether")],
            [InlineKeyboardButton(f"👹 Монстры: {yn(curr.get('spawn_monsters','true'))}", callback_data="set_monsters")],
            [InlineKeyboardButton(f"🐷 Животные: {yn(curr.get('spawn_animals','true'))}", callback_data="set_animals")],
            [InlineKeyboardButton(f"👨‍🌾 Жители (NPC): {yn(curr.get('spawn_npcs','true'))}", callback_data="set_npcs")],
            [InlineKeyboardButton(f"🏛️ Структуры: {yn(curr.get('generate_structures','true'))}", callback_data="set_structures")],
            [InlineKeyboardButton(f"🗺️ Тип мира: {level_type_names.get(curr.get('level_type','minecraft:normal'), curr.get('level_type','minecraft:normal'))}", callback_data="set_level_type")],
            [InlineKeyboardButton(f"🌱 Сид: {curr.get('seed','') or 'Случайный'}", callback_data="input_seed")],
            [InlineKeyboardButton(f"📐 Макс. размер мира: {curr.get('max_world_size','29999984')}", callback_data="set_max_world_size")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await edit_menu(bot, info["chat_id"], info["message_id"], "🌍 Мир и генерация:", keyboard)

    elif menu_key == "cfg_performance":
        tick = curr.get('max_tick_time', '60000')
        tick_label = "Безлимит" if tick == '-1' else f"{tick} мс"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✈️ Полёт: {'Разрешён' if curr.get('allow_flight','false')=='true' else 'Запрещён'}", callback_data="set_flight")],
            [InlineKeyboardButton(f"🎛️ Командные блоки: {'Включены' if curr.get('command_blocks','false')=='true' else 'Выключены'}", callback_data="set_cmd_blocks")],
            [InlineKeyboardButton(f"⏱️ Макс. время тика: {tick_label}", callback_data="set_max_tick_time")],
            [InlineKeyboardButton(f"📡 Дальность сущностей: {curr.get('entity_broadcast_range','100')}%", callback_data="set_entity_range")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await edit_menu(bot, info["chat_id"], info["message_id"], "⚙️ Производительность:", keyboard)

    elif menu_key == "cfg_security":
        idle = curr.get('player_idle_timeout', '0')
        idle_label = f"{idle} мин" if idle != '0' else "Выключен"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💀 Хардкор: {'Включён' if curr.get('hardcore','false')=='true' else 'Выключен'}", callback_data="set_hardcore")],
            [InlineKeyboardButton(f"📋 Белый список: {'Включён' if curr.get('whitelist','false')=='true' else 'Выключен'}", callback_data="set_whitelist")],
            [InlineKeyboardButton(f"👑 Уровень прав оператора: {curr.get('op_permission_level','4')}", callback_data="set_op_level")],
            [InlineKeyboardButton(f"💤 Тайм-аут AFK: {idle_label}", callback_data="set_idle_timeout")],
            [InlineKeyboardButton("🔙 Назад к конфигурации", callback_data="config_menu")]
        ])
        await edit_menu(bot, info["chat_id"], info["message_id"], "🔒 Безопасность:", keyboard)

    elif menu_key == "config_menu":
        summary = format_config_summary(curr)
        await edit_menu(bot, info["chat_id"], info["message_id"],
                        f"🛠️ Конфигурация сервера\n\n{summary}", build_config_keyboard())

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_states or user_states[user_id] is None:
        return

    state_tuple = user_states[user_id]
    if not isinstance(state_tuple, tuple):
        return

    state, back_menu = state_tuple
    chat_id = update.message.chat_id
    user_msg_id = update.message.message_id
    applied = False
    error_text = None

    if state == "input_version":
        user_settings[user_id]["version"] = text
        applied = True
    elif state == "input_ram":
        if text.isdigit() and int(text) >= 256:
            user_settings[user_id]["ram"] = text
            applied = True
        else:
            error_text = "❌ Введите число >= 256"
    elif state == "input_maxplayers":
        if text.isdigit() and int(text) >= 1:
            user_settings[user_id]["max_players"] = text
            applied = True
        else:
            error_text = "❌ Введите число >= 1"
    elif state == "input_port":
        if text.isdigit() and 1 <= int(text) <= 65535:
            user_settings[user_id]["port"] = text
            applied = True
        else:
            error_text = "❌ Введите порт от 1 до 65535"
    elif state == "input_viewdist":
        if text.isdigit() and 2 <= int(text) <= 32:
            user_settings[user_id]["view_distance"] = text
            applied = True
        else:
            error_text = "❌ Введите число от 2 до 32"
    elif state == "input_simdist":
        if text.isdigit() and 2 <= int(text) <= 32:
            user_settings[user_id]["simulation_distance"] = text
            applied = True
        else:
            error_text = "❌ Введите число от 2 до 32"
    elif state == "input_spawnprot":
        if text.isdigit():
            user_settings[user_id]["spawn_protection"] = text
            applied = True
        else:
            error_text = "❌ Введите число >= 0"
    elif state == "input_motd":
        user_settings[user_id]["motd"] = text
        applied = True
    elif state == "input_seed":
        user_settings[user_id]["seed"] = "" if text == '-' else text
        applied = True
    elif state == "input_max_tick":
        if text == '-1' or (text.lstrip('-').isdigit() and int(text) >= 0):
            user_settings[user_id]["max_tick_time"] = text
            applied = True
        else:
            error_text = "❌ Введите число >= 0 или -1 для безлимита"
    elif state == "input_entity_range":
        if text.isdigit() and 10 <= int(text) <= 1000:
            user_settings[user_id]["entity_broadcast_range"] = text
            applied = True
        else:
            error_text = "❌ Введите число от 10 до 1000"
    elif state == "input_idle_timeout":
        if text.isdigit():
            user_settings[user_id]["player_idle_timeout"] = text
            applied = True
        else:
            error_text = "❌ Введите число >= 0 (0 = выключено)"
    elif state == "input_max_world_size":
        if text.isdigit() and int(text) >= 1000:
            user_settings[user_id]["max_world_size"] = text
            applied = True
        else:
            error_text = "❌ Введите число >= 1000"

    if error_text:
        note = await context.bot.send_message(chat_id=chat_id, text=error_text)
        await asyncio.sleep(3)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=note.message_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=user_msg_id)
        except:
            pass
        return

    user_states[user_id] = None

    async def cleanup():
        await asyncio.sleep(3)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_msg_id)
        except:
            pass
        prompt_msg_id = context.user_data.get("prompt_msg_id") if context.user_data else None
        prompt_chat_id = context.user_data.get("prompt_chat_id", chat_id) if context.user_data else chat_id
        if prompt_msg_id:
            try:
                await context.bot.delete_message(chat_id=prompt_chat_id, message_id=prompt_msg_id)
            except:
                pass

    if applied:
        asyncio.create_task(cleanup())
        await _refresh_submenu(context.bot, user_id, back_menu)

async def _do_create_server(user_id, msg, query, context):
    temp_path = None
    try:
        temp_path, archive_size, original_size, compression = await create_server_package(user_id, msg)
        s = user_settings.get(user_id, {})
        loader = s.get('loader') or 'Fabric'
        version = s.get('version') or '1.20.1'
        ram = s.get('ram') or '2048'
        _, java_label = get_java_for_version(version)
        fname = f"minecraft-server-{version}-{loader.lower()}.zip"
        caption = (
            f"✅ Сервер готов!\n\n"
            f"🎯 {version} {loader}\n"
            f"💾 Память: {ram} MB\n"
            f"📦 Размер: {archive_size / (1024*1024):.1f} MB\n"
            f"☕ Требуется: {java_label}\n\n"
            f"🚀 Распакуйте и запустите start.bat (Windows) или start.sh (Linux)"
        )
        await msg.edit_text(f"📤 Отправка {archive_size / (1024*1024):.1f} MB...")
        with open(temp_path, 'rb') as file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file,
                filename=fname,
                caption=caption,
                read_timeout=600,
                write_timeout=600,
                connect_timeout=120,
                pool_timeout=120
            )
        await msg.delete()
        await asyncio.sleep(3)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Быстрые шаблоны", callback_data="presets_menu")],
            [InlineKeyboardButton("🛠️ Конфигурация", callback_data="config_menu")],
            [InlineKeyboardButton("☕ Java - инструкция", callback_data="java_info")],
            [InlineKeyboardButton("📖 Помощь", callback_data="help_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📋 Выберите действие:",
            reply_markup=keyboard
        )
    except Exception as e:
        traceback.print_exc()
        await msg.edit_text(f"❌ Ошибка:\n\n{str(e)}")
        await asyncio.sleep(5)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Быстрые шаблоны", callback_data="presets_menu")],
            [InlineKeyboardButton("🛠️ Конфигурация", callback_data="config_menu")],
            [InlineKeyboardButton("☕ Java - инструкция", callback_data="java_info")],
            [InlineKeyboardButton("📖 Помощь", callback_data="help_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📋 Выберите действие:",
            reply_markup=keyboard
        )
    finally:
        user_creating_server[user_id] = False
        if temp_path and os.path.exists(temp_path):
            try:
                await asyncio.sleep(1)
                os.unlink(temp_path)
            except Exception as e:
                print(f"[ERROR] Удаление файла: {e}")

def main():
    print("[INFO] Запуск бота...")
    request = HTTPXRequest(
        connection_pool_size=16,
        read_timeout=600,
        write_timeout=600,
        connect_timeout=120,
        pool_timeout=120
    )
    app = Application.builder().token(TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    print("[INFO] Бот запущен! Ожидание команд...")
    app.run_polling()

if __name__ == "__main__":
    main()
