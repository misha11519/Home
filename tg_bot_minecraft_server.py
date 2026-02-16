import os
import zipfile
import logging
import aiohttp
import asyncio
import tempfile
import traceback
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from telegram.error import TimedOut, NetworkError

logging.disable(logging.CRITICAL)

TOKEN = "BOT_TOKEN"

user_settings = {}
user_states = {}
user_creating_server = {}

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
    parsed = parse_version(version)
    return parsed >= (1, 14, 0)

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
        
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
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
        
        timeout = aiohttp.ClientTimeout(
            total=None,
            connect=60,
            sock_read=900
        )
        
        connector = aiohttp.TCPConnector(
            limit=1,
            limit_per_host=1,
            ttl_dns_cache=300,
            force_close=False
        )
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            
            if loader == "fabric":
                if not is_fabric_supported(version):
                    raise Exception(f"❌ Fabric не существует для версии {version}\n\n💡 Fabric доступен только с версии 1.14 и выше\n\nИспользуйте Forge для старых версий")
                
                if progress_callback:
                    await progress_callback("⏳ Поиск Fabric...")
                
                loader_url = "https://meta.fabricmc.net/v2/versions/loader"
                async with session.get(loader_url) as loader_resp:
                    if loader_resp.status == 200:
                        loaders = await loader_resp.json()
                        if loaders:
                            loader_version = loaders[0]['version']
                            
                            installer_url = "https://meta.fabricmc.net/v2/versions/installer"
                            async with session.get(installer_url) as inst_resp:
                                if inst_resp.status == 200:
                                    installers = await inst_resp.json()
                                    if installers:
                                        installer_version = installers[0]['version']
                                        download_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
                                        jar_name = f"fabric-server-{version}.jar"
                                        
                                        jar_data = await download_with_retry(session, download_url, progress_callback)
                                        return jar_data, jar_name
                raise Exception(f"Fabric не поддерживает {version}")
            
            elif loader == "forge":
                if progress_callback:
                    await progress_callback("⏳ Поиск Forge...")
                
                promo_url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
                async with session.get(promo_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        promos = data.get('promos', {})
                        forge_version = promos.get(f"{version}-latest") or promos.get(f"{version}-recommended")
                        
                        if forge_version:
                            version_parts = version.split('.')
                            major = int(version_parts[1]) if len(version_parts) > 1 else 0
                            
                            if major >= 7 and major <= 12:
                                full_version = f"{version}-{forge_version}"
                                download_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{full_version}/forge-{full_version}-universal.jar"
                                
                                try:
                                    jar_name = f"forge-{version}-universal.jar"
                                    jar_data = await download_with_retry(session, download_url, progress_callback)
                                    return jar_data, jar_name
                                except:
                                    if version == "1.7.10":
                                        full_version_dup = f"{version}-{forge_version}-{version}"
                                        download_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{full_version_dup}/forge-{full_version_dup}-universal.jar"
                                        jar_name = f"forge-{version}-universal.jar"
                                        jar_data = await download_with_retry(session, download_url, progress_callback)
                                        return jar_data, jar_name
                            else:
                                full_version = f"{version}-{forge_version}"
                                download_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{full_version}/forge-{full_version}-installer.jar"
                                jar_name = f"forge-{version}-installer.jar"
                                
                                if progress_callback:
                                    await progress_callback("⚠️ Forge 1.13+ требует запуска installer")
                                
                                jar_data = await download_with_retry(session, download_url, progress_callback)
                                return jar_data, jar_name
                        
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
        
        print(f"[DEBUG] Загрузка jar для {loader} {version}")
        jar_data, jar_name = await get_server_jar(loader, version, update_progress)
        
        if not jar_data:
            raise Exception("Не удалось загрузить серверное ядро")
        
        original_size = len(jar_data)
        print(f"[DEBUG] Jar загружен: {original_size / (1024*1024):.1f}MB")
        await update_progress(f"🗜️ Сжатие {original_size // (1024*1024)}MB...")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_path = temp_file.name
        temp_file.close()
        print(f"[DEBUG] Временный файл: {temp_path}")
        
        print(f"[DEBUG] Создание архива...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_zip_sync, temp_path, jar_data, jar_name, settings)
        
        archive_size = os.path.getsize(temp_path)
        compression_ratio = 100 - (archive_size / original_size * 100)
        print(f"[DEBUG] Архив создан: {archive_size / (1024*1024):.1f}MB")
        
        max_size = 49.5 * 1024 * 1024
        
        if archive_size > max_size:
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
        print(f"[ERROR] create_server_package: {e}")
        traceback.print_exc()
        raise Exception(str(e))

def get_default_settings():
    return {
        "version": "1.20.1",
        "loader": "Fabric",
        "max_players": "20",
        "difficulty": "normal",
        "gamemode": "survival",
        "pvp": "true",
        "online_mode": "true",
        "port": "25565",
        "view_distance": "10",
        "simulation_distance": "10",
        "spawn_protection": "16",
        "allow_nether": "true",
        "allow_flight": "false",
        "command_blocks": "false",
        "spawn_monsters": "true",
        "spawn_animals": "true",
        "spawn_npcs": "true",
        "generate_structures": "true",
        "level_type": "minecraft:normal",
        "seed": "",
        "motd": "A Minecraft Server",
        "ram": "2048",
        "max_tick_time": "60000",
        "op_permission_level": "4",
        "entity_broadcast_range": "100",
        "player_idle_timeout": "0",
        "hardcore": "false",
        "whitelist": "false",
        "max_world_size": "29999984"
    }

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_settings:
        user_settings[user_id] = get_default_settings()
    user_states[user_id] = None
    user_creating_server[user_id] = False
    
    keyboard = [[InlineKeyboardButton("📋 Меню", callback_data="action_menu")]]
    await update.message.reply_text(
        "🎮 Minecraft Server Builder\n\n"
        "✨ Fabric, Forge\n\n"
        "Бот способен создавать готовые майнкрафт сервера\n"
        "Для этого зайдите в меню и настройте сервер, как вам нужно\n"
        "После настройки можно начинать создавать сервер",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def action_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔨 Создать сервер", callback_data="create_server")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    await query.edit_message_text("📋 Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    curr = user_settings.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton(f"🎯 Версия: {curr.get('version', '1.20.1')}", callback_data="set_version")],
        [InlineKeyboardButton(f"⚡ Загрузчик: {curr.get('loader', 'Fabric')}", callback_data="set_loader")],
        [InlineKeyboardButton(f"💾 RAM: {curr.get('ram', '2048')}MB", callback_data="set_ram")],
        [InlineKeyboardButton("📝 Основные", callback_data="server_properties")],
        [InlineKeyboardButton("🌍 Мир", callback_data="world_settings")],
        [InlineKeyboardButton("⚙️ Производительность", callback_data="performance_settings")],
        [InlineKeyboardButton("🔒 Безопасность", callback_data="security_settings")],
        [InlineKeyboardButton("🔙 Назад", callback_data="action_menu")]
    ]
    await query.edit_message_text("⚙️ Настройки сервера:", reply_markup=InlineKeyboardMarkup(keyboard))

async def version_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1.21.4", callback_data="version_1.21.4"), InlineKeyboardButton("1.21.3", callback_data="version_1.21.3")],
        [InlineKeyboardButton("1.21.1", callback_data="version_1.21.1"), InlineKeyboardButton("1.21", callback_data="version_1.21")],
        [InlineKeyboardButton("1.20.6", callback_data="version_1.20.6"), InlineKeyboardButton("1.20.4", callback_data="version_1.20.4")],
        [InlineKeyboardButton("1.20.1 ✅", callback_data="version_1.20.1"), InlineKeyboardButton("1.19.4", callback_data="version_1.19.4")],
        [InlineKeyboardButton("1.18.2", callback_data="version_1.18.2"), InlineKeyboardButton("1.16.5 💾", callback_data="version_1.16.5")],
        [InlineKeyboardButton("1.12.2 💾", callback_data="version_1.12.2"), InlineKeyboardButton("1.8.8 💾", callback_data="version_1.8.8")],
        [InlineKeyboardButton("1.7.10 💾", callback_data="version_1.7.10"), InlineKeyboardButton("✏️ Ввести", callback_data="input_version")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text(
        "🎯 Выберите версию:\n\n"
        "💾 = Меньше размер\n"
        "✅ = Рекомендуется",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def loader_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Fabric 💾", callback_data="loader_fabric")],
        [InlineKeyboardButton("Forge", callback_data="loader_forge")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text(
        "⚡ Выберите загрузчик:\n\n"
        "💾 = Меньше размер",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ram_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("512MB", callback_data="ram_512"), InlineKeyboardButton("1GB", callback_data="ram_1024")],
        [InlineKeyboardButton("2GB", callback_data="ram_2048"), InlineKeyboardButton("4GB", callback_data="ram_4096")],
        [InlineKeyboardButton("8GB", callback_data="ram_8192"), InlineKeyboardButton("16GB", callback_data="ram_16384")],
        [InlineKeyboardButton("✏️ Ввести (MB)", callback_data="input_ram")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text("💾 Выберите RAM:", reply_markup=InlineKeyboardMarkup(keyboard))

async def server_properties_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    current = user_settings.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton(f"👥 Max Players: {current.get('max_players', '20')}", callback_data="set_max_players")],
        [InlineKeyboardButton(f"⚔️ Difficulty: {current.get('difficulty', 'normal')}", callback_data="set_difficulty")],
        [InlineKeyboardButton(f"🎮 Gamemode: {current.get('gamemode', 'survival')}", callback_data="set_gamemode")],
        [InlineKeyboardButton(f"⚔️ PVP: {current.get('pvp', 'true')}", callback_data="set_pvp")],
        [InlineKeyboardButton(f"🔐 Online: {current.get('online_mode', 'true')}", callback_data="set_online_mode")],
        [InlineKeyboardButton(f"🔌 Port: {current.get('port', '25565')}", callback_data="set_port")],
        [InlineKeyboardButton(f"📝 MOTD", callback_data="input_motd")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text("📝 Основные настройки:", reply_markup=InlineKeyboardMarkup(keyboard))

async def world_settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    current = user_settings.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton(f"👁️ View: {current.get('view_distance', '10')}", callback_data="set_view_distance")],
        [InlineKeyboardButton(f"🎯 Simulation: {current.get('simulation_distance', '10')}", callback_data="set_simulation_distance")],
        [InlineKeyboardButton(f"🏰 Spawn Protect: {current.get('spawn_protection', '16')}", callback_data="set_spawn_protection")],
        [InlineKeyboardButton(f"🔥 Nether: {current.get('allow_nether', 'true')}", callback_data="set_nether")],
        [InlineKeyboardButton(f"👹 Monsters: {current.get('spawn_monsters', 'true')}", callback_data="set_monsters")],
        [InlineKeyboardButton(f"🐷 Animals: {current.get('spawn_animals', 'true')}", callback_data="set_animals")],
        [InlineKeyboardButton(f"👨‍🌾 NPCs: {current.get('spawn_npcs', 'true')}", callback_data="set_npcs")],
        [InlineKeyboardButton(f"🏛️ Structures: {current.get('generate_structures', 'true')}", callback_data="set_structures")],
        [InlineKeyboardButton(f"🗺️ Level Type", callback_data="set_level_type")],
        [InlineKeyboardButton(f"🌱 Seed", callback_data="input_seed")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text("🌍 Настройки мира:", reply_markup=InlineKeyboardMarkup(keyboard))

async def performance_settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    current = user_settings.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton(f"✈️ Flight: {current.get('allow_flight', 'false')}", callback_data="set_flight")],
        [InlineKeyboardButton(f"🎛️ Cmd Blocks: {current.get('command_blocks', 'false')}", callback_data="set_cmd_blocks")],
        [InlineKeyboardButton(f"⏱️ Max Tick: {current.get('max_tick_time', '60000')}", callback_data="set_max_tick_time")],
        [InlineKeyboardButton(f"📡 Entity Range: {current.get('entity_broadcast_range', '100')}%", callback_data="set_entity_range")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text("⚙️ Производительность:", reply_markup=InlineKeyboardMarkup(keyboard))

async def security_settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    current = user_settings.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton(f"💀 Hardcore: {current.get('hardcore', 'false')}", callback_data="set_hardcore")],
        [InlineKeyboardButton(f"📋 Whitelist: {current.get('whitelist', 'false')}", callback_data="set_whitelist")],
        [InlineKeyboardButton(f"👑 Op Level: {current.get('op_permission_level', '4')}", callback_data="set_op_level")],
        [InlineKeyboardButton(f"💤 Idle: {current.get('player_idle_timeout', '0')}", callback_data="set_idle_timeout")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    await query.edit_message_text("🔒 Безопасность:", reply_markup=InlineKeyboardMarkup(keyboard))

async def max_players_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("5", callback_data="maxplayers_5"), InlineKeyboardButton("10", callback_data="maxplayers_10")],
        [InlineKeyboardButton("20", callback_data="maxplayers_20"), InlineKeyboardButton("50", callback_data="maxplayers_50")],
        [InlineKeyboardButton("100", callback_data="maxplayers_100"), InlineKeyboardButton("200", callback_data="maxplayers_200")],
        [InlineKeyboardButton("✏️ Ввести", callback_data="input_maxplayers")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    await query.edit_message_text("👥 Макс. игроков:", reply_markup=InlineKeyboardMarkup(keyboard))

async def difficulty_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☮️ Peaceful", callback_data="difficulty_peaceful")],
        [InlineKeyboardButton("😊 Easy", callback_data="difficulty_easy")],
        [InlineKeyboardButton("😐 Normal", callback_data="difficulty_normal")],
        [InlineKeyboardButton("😈 Hard", callback_data="difficulty_hard")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    await query.edit_message_text("⚔️ Сложность:", reply_markup=InlineKeyboardMarkup(keyboard))

async def gamemode_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⛏️ Survival", callback_data="gamemode_survival")],
        [InlineKeyboardButton("🎨 Creative", callback_data="gamemode_creative")],
        [InlineKeyboardButton("🗺️ Adventure", callback_data="gamemode_adventure")],
        [InlineKeyboardButton("👻 Spectator", callback_data="gamemode_spectator")],
        [InlineKeyboardButton("🔙 Назад", callback_data="server_properties")]
    ]
    await query.edit_message_text("🎮 Режим:", reply_markup=InlineKeyboardMarkup(keyboard))

async def level_type_menu(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Default", callback_data="leveltype_minecraft:normal")],
        [InlineKeyboardButton("Flat", callback_data="leveltype_minecraft:flat")],
        [InlineKeyboardButton("Large Biomes", callback_data="leveltype_minecraft:large_biomes")],
        [InlineKeyboardButton("Amplified", callback_data="leveltype_minecraft:amplified")],
        [InlineKeyboardButton("🔙 Назад", callback_data="world_settings")]
    ]
    await query.edit_message_text("🗺️ Тип мира:", reply_markup=InlineKeyboardMarkup(keyboard))

async def toggle_menu(query, context: ContextTypes.DEFAULT_TYPE, setting_name, display_name, back_menu):
    keyboard = [
        [InlineKeyboardButton("✅ Включить", callback_data=f"toggle_{setting_name}_true")],
        [InlineKeyboardButton("❌ Выключить", callback_data=f"toggle_{setting_name}_false")],
        [InlineKeyboardButton("🔙 Назад", callback_data=back_menu)]
    ]
    await query.edit_message_text(f"{display_name}:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_states or user_states[user_id] is None:
        return
    
    state = user_states[user_id]
    
    if state == "input_version":
        user_settings[user_id]["version"] = text
        await update.message.reply_text(f"✅ Версия: {text}")
    elif state == "input_ram" and text.isdigit():
        user_settings[user_id]["ram"] = text
        await update.message.reply_text(f"✅ RAM: {text}MB")
    elif state == "input_maxplayers" and text.isdigit():
        user_settings[user_id]["max_players"] = text
        await update.message.reply_text(f"✅ Игроков: {text}")
    elif state == "input_port" and text.isdigit():
        user_settings[user_id]["port"] = text
        await update.message.reply_text(f"✅ Порт: {text}")
    elif state == "input_viewdist" and text.isdigit():
        user_settings[user_id]["view_distance"] = text
        await update.message.reply_text(f"✅ View: {text}")
    elif state == "input_simdist" and text.isdigit():
        user_settings[user_id]["simulation_distance"] = text
        await update.message.reply_text(f"✅ Simulation: {text}")
    elif state == "input_spawnprot" and text.isdigit():
        user_settings[user_id]["spawn_protection"] = text
        await update.message.reply_text(f"✅ Spawn protect: {text}")
    elif state == "input_motd":
        user_settings[user_id]["motd"] = text
        await update.message.reply_text(f"✅ MOTD: {text}")
    elif state == "input_seed":
        user_settings[user_id]["seed"] = text
        await update.message.reply_text(f"✅ Seed: {text}")
    
    user_states[user_id] = None

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_settings:
        user_settings[user_id] = get_default_settings()
    
    if data == "main_menu":
        user_states[user_id] = None
        keyboard = [[InlineKeyboardButton("📋 Меню", callback_data="action_menu")]]
        await query.edit_message_text(
        "🎮 Minecraft Server Builder\n\n"
        "✨ Fabric, Forge\n\n"
        "Бот способен создавать готовые майнкрафт сервера\n"
        "Для этого зайдите в меню и настройте сервер, как вам нужно\n"
        "После настройки можно начинать создавать сервер",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "action_menu":
        user_states[user_id] = None
        await action_menu(query, context)
    
    elif data == "create_server":
        if user_creating_server.get(user_id, False):
            await query.answer("⚠️ Сервер уже создаётся!", show_alert=True)
            return
        
        user_creating_server[user_id] = True
        msg = await query.edit_message_text("⏳ Запуск...")
        temp_path = None
        try:
            print(f"[DEBUG] Начало создания для user {user_id}")
            temp_path, archive_size, original_size, compression = await create_server_package(user_id, msg)
            print(f"[DEBUG] Пакет создан: {temp_path}")
            
            s = user_settings.get(user_id, {})
            loader = s.get('loader') or 'Fabric'
            version = s.get('version') or '1.20.1'
            ram = s.get('ram') or '2048'
            
            fname = f"minecraft-server-{version}-{loader.lower()}.zip"
            
            caption = (
                f"✅ Сервер готов!\n\n"
                f"🎯 {version} {loader}\n"
                f"💾 RAM: {ram}MB\n"
                f"📦 {archive_size / (1024*1024):.1f}MB\n\n"
                f"🚀 Распакуйте и запустите start.bat/start.sh"
            )
            
            if not os.path.exists(temp_path):
                raise Exception("Файл не создан")
            
            print(f"[DEBUG] Обновление статуса отправки...")
            await msg.edit_text(f"📤 Отправка {archive_size / (1024*1024):.1f}MB...")
            
            print(f"[DEBUG] Открытие файла для отправки...")
            with open(temp_path, 'rb') as file:
                print(f"[DEBUG] Вызов send_document...")
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
                print(f"[DEBUG] Документ отправлен!")
            
            print(f"[DEBUG] Удаление статусного сообщения...")
            await msg.delete()
            print(f"[DEBUG] Успех!")
            
            await asyncio.sleep(5)
            
            keyboard = [
                [InlineKeyboardButton("🔨 Создать сервер", callback_data="create_server")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="📋 Выберите действие:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
                
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            await msg.edit_text(f"❌ Ошибка: {str(e)}")
            
            await asyncio.sleep(5)
            
            keyboard = [
                [InlineKeyboardButton("🔨 Создать сервер", callback_data="create_server")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="📋 Выберите действие:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        finally:
            user_creating_server[user_id] = False
            if temp_path and os.path.exists(temp_path):
                try:
                    print(f"[DEBUG] Удаление временного файла...")
                    await asyncio.sleep(1)
                    os.unlink(temp_path)
                    print(f"[DEBUG] Временный файл удален")
                except Exception as cleanup_error:
                    print(f"[ERROR] Удаление файла: {cleanup_error}")
            
    elif data == "settings":
        user_states[user_id] = None
        await settings_menu(query, context)
    elif data == "set_version":
        await version_menu(query, context)
    elif data == "set_loader":
        await loader_menu(query, context)
    elif data == "set_ram":
        await ram_menu(query, context)
    elif data == "server_properties":
        user_states[user_id] = None
        await server_properties_menu(query, context)
    elif data == "world_settings":
        user_states[user_id] = None
        await world_settings_menu(query, context)
    elif data == "performance_settings":
        user_states[user_id] = None
        await performance_settings_menu(query, context)
    elif data == "security_settings":
        user_states[user_id] = None
        await security_settings_menu(query, context)
    elif data == "set_max_players":
        await max_players_menu(query, context)
    elif data == "set_difficulty":
        await difficulty_menu(query, context)
    elif data == "set_gamemode":
        await gamemode_menu(query, context)
    elif data == "set_pvp":
        await toggle_menu(query, context, "pvp", "⚔️ PVP", "server_properties")
    elif data == "set_online_mode":
        await toggle_menu(query, context, "online_mode", "🔐 Online Mode", "server_properties")
    elif data == "set_port":
        user_states[user_id] = "input_port"
        await query.message.reply_text("✏️ Введите порт:")
    elif data == "set_view_distance":
        user_states[user_id] = "input_viewdist"
        await query.message.reply_text("✏️ Введите view distance:")
    elif data == "set_simulation_distance":
        user_states[user_id] = "input_simdist"
        await query.message.reply_text("✏️ Введите simulation distance:")
    elif data == "set_spawn_protection":
        user_states[user_id] = "input_spawnprot"
        await query.message.reply_text("✏️ Введите spawn protection:")
    elif data == "set_nether":
        await toggle_menu(query, context, "allow_nether", "🔥 Nether", "world_settings")
    elif data == "set_monsters":
        await toggle_menu(query, context, "spawn_monsters", "👹 Monsters", "world_settings")
    elif data == "set_animals":
        await toggle_menu(query, context, "spawn_animals", "🐷 Animals", "world_settings")
    elif data == "set_npcs":
        await toggle_menu(query, context, "spawn_npcs", "👨‍🌾 NPCs", "world_settings")
    elif data == "set_structures":
        await toggle_menu(query, context, "generate_structures", "🏛️ Structures", "world_settings")
    elif data == "set_level_type":
        await level_type_menu(query, context)
    elif data == "set_flight":
        await toggle_menu(query, context, "allow_flight", "✈️ Flight", "performance_settings")
    elif data == "set_cmd_blocks":
        await toggle_menu(query, context, "command_blocks", "🎛️ Command Blocks", "performance_settings")
    elif data == "set_hardcore":
        await toggle_menu(query, context, "hardcore", "💀 Hardcore", "security_settings")
    elif data == "set_whitelist":
        await toggle_menu(query, context, "whitelist", "📋 Whitelist", "security_settings")
        
    elif data.startswith("version_"):
        user_states[user_id] = None
        user_settings[user_id]["version"] = data.split("_")[1]
        await settings_menu(query, context)
    elif data.startswith("loader_"):
        user_states[user_id] = None
        user_settings[user_id]["loader"] = data.split("_")[1].capitalize()
        await settings_menu(query, context)
    elif data.startswith("ram_"):
        user_states[user_id] = None
        user_settings[user_id]["ram"] = data.split("_")[1]
        await settings_menu(query, context)
    elif data.startswith("maxplayers_"):
        user_states[user_id] = None
        user_settings[user_id]["max_players"] = data.split("_")[1]
        await server_properties_menu(query, context)
    elif data.startswith("difficulty_"):
        user_states[user_id] = None
        user_settings[user_id]["difficulty"] = data.split("_")[1]
        await server_properties_menu(query, context)
    elif data.startswith("gamemode_"):
        user_states[user_id] = None
        user_settings[user_id]["gamemode"] = data.split("_")[1]
        await server_properties_menu(query, context)
    elif data.startswith("toggle_"):
        user_states[user_id] = None
        parts = data.replace("toggle_", "").rsplit("_", 1)
        setting_name = parts[0]
        value = parts[1]
        user_settings[user_id][setting_name] = value
        
        if setting_name in ["allow_nether", "spawn_monsters", "spawn_animals", "spawn_npcs", "generate_structures"]:
            await world_settings_menu(query, context)
        elif setting_name in ["allow_flight", "command_blocks"]:
            await performance_settings_menu(query, context)
        elif setting_name in ["hardcore", "whitelist"]:
            await security_settings_menu(query, context)
        else:
            await server_properties_menu(query, context)
    elif data.startswith("leveltype_"):
        user_states[user_id] = None
        user_settings[user_id]["level_type"] = data.replace("leveltype_", "")
        await world_settings_menu(query, context)
        
    elif data == "input_version":
        user_states[user_id] = "input_version"
        await query.message.reply_text("✏️ Введите версию:")
    elif data == "input_ram":
        user_states[user_id] = "input_ram"
        await query.message.reply_text("✏️ Введите RAM (MB):")
    elif data == "input_maxplayers":
        user_states[user_id] = "input_maxplayers"
        await query.message.reply_text("✏️ Введите макс. игроков:")
    elif data == "input_motd":
        user_states[user_id] = "input_motd"
        await query.message.reply_text("✏️ Введите MOTD:")
    elif data == "input_seed":
        user_states[user_id] = "input_seed"
        await query.message.reply_text("✏️ Введите seed:")

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
