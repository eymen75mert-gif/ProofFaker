import discord
from discord import app_commands
import datetime
import random
import traceback
import os
import pyppeteer
import pytz

# ============================================================
# AYARLAR
# ============================================================
channels = [1546966686035349508]
token = os.getenv("TOKEN")

# ============================================================
# ZAMAN DİLİMİ
# ============================================================
locale_to_timezone = {
    discord.Locale.american_english: 'America/New_York',
    discord.Locale.british_english: 'Europe/London',
    discord.Locale.bulgarian: 'Europe/Sofia',
    discord.Locale.chinese: 'Asia/Shanghai',
    discord.Locale.taiwan_chinese: 'Asia/Taipei',
    discord.Locale.croatian: 'Europe/Zagreb',
    discord.Locale.czech: 'Europe/Prague',
    discord.Locale.indonesian: 'Asia/Jakarta',
    discord.Locale.danish: 'Europe/Copenhagen',
    discord.Locale.dutch: 'Europe/Amsterdam',
    discord.Locale.finnish: 'Europe/Helsinki',
    discord.Locale.french: 'Europe/Paris',
    discord.Locale.german: 'Europe/Berlin',
    discord.Locale.greek: 'Europe/Athens',
    discord.Locale.hindi: 'Asia/Kolkata',
    discord.Locale.hungarian: 'Europe/Budapest',
    discord.Locale.italian: 'Europe/Rome',
    discord.Locale.japanese: 'Asia/Tokyo',
    discord.Locale.korean: 'Asia/Seoul',
    discord.Locale.latin_american_spanish: 'America/Mexico_City',
    discord.Locale.lithuanian: 'Europe/Vilnius',
    discord.Locale.norwegian: 'Europe/Oslo',
    discord.Locale.polish: 'Europe/Warsaw',
    discord.Locale.brazil_portuguese: 'America/Sao_Paulo',
    discord.Locale.romanian: 'Europe/Bucharest',
    discord.Locale.russian: 'Europe/Moscow',
    discord.Locale.spain_spanish: 'Europe/Madrid',
    discord.Locale.swedish: 'Europe/Stockholm',
    discord.Locale.thai: 'Asia/Bangkok',
    discord.Locale.turkish: 'Europe/Istanbul',
    discord.Locale.ukrainian: 'Europe/Kyiv',
    discord.Locale.vietnamese: 'Asia/Ho_Chi_Minh',
}

def get_current_time_in_locale(interaction: discord.Interaction):
    user_locale = interaction.locale
    timezone_str = locale_to_timezone.get(user_locale, 'UTC')
    timezone = pytz.timezone(timezone_str)
    return datetime.datetime.now(timezone)

def generate_time_range(interaction):
    current_time = get_current_time_in_locale(interaction)
    random_minutes = random.randint(2, 7)
    new_time = current_time + datetime.timedelta(minutes=random_minutes)
    if new_time.minute > 59:
        new_time = new_time.replace(hour=new_time.hour + 1, minute=new_time.minute % 60)
    current_time_format = current_time.strftime('%I:%M %p').lstrip('0')
    new_time_format = new_time.strftime('%I:%M %p').lstrip('0')
    original_time_format = current_time.strftime("%d %B %Y")
    return current_time_format, new_time_format, original_time_format

# ============================================================
# CHROME BAŞLATMA (LINUX UYUMLU)
# ============================================================
async def launch_browser():
    """Linux/Railway uyumlu Chrome başlatma"""
    executable_path = os.getenv("PUPPETEER_EXECUTABLE_PATH", "/usr/bin/chromium")
    return await pyppeteer.launch(
        executablePath=executable_path,
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--single-process',
        ]
    )

# ============================================================
# BOT CLIENT
# ============================================================
class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # GLOBAL SYNC - Guild ID yok, tüm sunucularda çalışır
        await self.tree.sync()
        print("✅ Komutlar global olarak senkronize edildi!")

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="Use /proof to see the commands"))
        print(f"✅ {self.user} ({self.user.id}) hazır!")

client = Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(client.user.mention):
        await message.channel.send(f"{message.author.mention} Please use /proof command.")

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
def sanitize(text):
    if text is None:
        return ""
    return str(text).replace('<', '').replace('>', '').replace('script', '')

def get_user_name(user):
    if user.global_name:
        return user.global_name
    return user.name

def get_user_avatar(user):
    if user.avatar:
        return user.avatar.url
    return user.default_avatar.url

async def take_screenshot(html_content, clip_x, clip_y, clip_w, clip_h, width=1300, height=500):
    """HTML'den ekran görüntüsü al"""
    with open("assets/temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    browser = await launch_browser()
    page = await browser.newPage()
    await page.setViewport({'width': width, 'height': height})
    absolute_path = f'file://{os.path.abspath("assets/temp.html")}'
    await page.goto(absolute_path, waitUntil='networkidle0')
    
    await page.screenshot({
        'path': 'proof.png',
        'clip': {
            'x': clip_x,
            'y': clip_y,
            'width': clip_w,
            'height': clip_h
        }
    })
    await browser.close()

def send_error_embed(interaction, error_msg="Oops! Something went wrong."):
    embed = discord.Embed(color=0xFF0000, title="Error", description=f"> **{error_msg}**")
    embed.set_footer(text="PekkleDev")
    return embed

def send_success_embed(interaction, note=""):
    embed = discord.Embed(color=0x717CDA, title="Success", description=f"> **Please check your DMs!** {note}")
    embed.set_footer(text="PekkleDev")
    return embed

# ============================================================
# NITRO PROOF
# ============================================================
class NitroPage:
    def __init__(self, gifter_username, receiver_username, gifter_message, receiver_message,
                 gifter_avatar_url, receiver_avatar_url, timestamp_1, timestamp_2, full_date, claimed):
        self.gifter_username = sanitize(gifter_username)
        self.receiver_username = sanitize(receiver_username)
        self.gifter_message = sanitize(gifter_message)
        self.receiver_message = sanitize(receiver_message)
        self.gifter_avatar_url = gifter_avatar_url
        self.receiver_avatar_url = receiver_avatar_url
        self.timestamp_1 = timestamp_1
        self.timestamp_2 = timestamp_2
        self.full_date = full_date.lstrip('0') if full_date.startswith('0') else full_date
        self.claimed = claimed

    def get_proof(self):
        if self.claimed:
            filename = "assets/nitroproof.html"
        else:
            filename = "assets/nitroproofclaimed.html"
        
        with open(filename, 'r', encoding="utf-8") as file:
            content = file.read()
        
        content = content.replace('GIFTER_USERNAME', self.gifter_username)
        content = content.replace('RECEIVER_USERNAME', self.receiver_username)
        content = content.replace('GIFTER_MESSAGE', self.gifter_message + '\u2004' if self.gifter_message else self.gifter_message)
        content = content.replace('RECEIVER_MESSAGE', self.receiver_message)
        content = content.replace('GIFTER_AVATAR_URL', self.gifter_avatar_url)
        content = content.replace('RECEIVER_AVATAR_URL', self.receiver_avatar_url)
        content = content.replace('TIMESTAMP_1', self.timestamp_1)
        content = content.replace('TIMESTAMP_2', self.timestamp_2)
        content = content.replace('FULL_DATE', self.full_date)
        content = content.replace('KJASNZXCJD', f'{random.randint(36, 47)}')
        return content

class NitroModal(discord.ui.Modal, title='Nitro proof generator'):
    nitro_type = discord.ui.TextInput(
        label="Nitro type (leave empty for unclaimed)",
        placeholder="unclaimed/claimed",
        style=discord.TextStyle.short,
        required=False,
    )
    gifter_id = discord.ui.TextInput(
        label="Gifter's ID (leave empty for yours)",
        style=discord.TextStyle.short,
        placeholder='12345678901234567890',
        required=False,
    )
    gifter_text = discord.ui.TextInput(
        label="Gifter's message",
        placeholder="Congratulations! You won the giveaway, here's your nitro: ",
        style=discord.TextStyle.short,
        required=False,
    )
    receiver_id = discord.ui.TextInput(
        label="Receiver's ID (leave empty for random)",
        style=discord.TextStyle.short,
        placeholder='12345678901234567890',
        required=False,
    )
    receiver_text = discord.ui.TextInput(
        label="Receiver's message",
        style=discord.TextStyle.short,
        placeholder='OMG! Thanks!',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            is_claimed = self.nitro_type.value and self.nitro_type.value.lower() == "claimed"
            
            # Gifter
            gifter = interaction.user
            note = ""
            if self.gifter_id.value:
                try:
                    gifter = await client.fetch_user(int(self.gifter_id.value))
                except Exception:
                    note = "Note: Invalid Gifter ID"
            
            # Receiver
            members = await interaction.guild.chunk()
            receiver = random.choice(members)
            if self.receiver_id.value:
                try:
                    receiver = await client.fetch_user(int(self.receiver_id.value))
                except Exception:
                    note = "Note: Invalid Receiver ID"
            
            gifter_message = self.gifter_text.value if self.gifter_text.value else ""
            receiver_message = self.receiver_text.value
            
            times = generate_time_range(interaction)
            
            proof = NitroPage(
                get_user_name(gifter), get_user_name(receiver),
                gifter_message, receiver_message,
                get_user_avatar(gifter), get_user_avatar(receiver),
                times[0], times[1], times[2], is_claimed
            ).get_proof()
            
            await take_screenshot(proof, random.randint(1, 8), random.randint(75, 83),
                                  random.randint(850, 1100), random.randint(400, 420), 1300, 500)
            
            await interaction.followup.send(embed=send_success_embed(interaction, note))
            await interaction.user.send(file=discord.File('proof.png'))
            
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(embed=send_error_embed(interaction, str(e)[:500]))

@client.tree.command(description='Generate proof for a nitro giveaway.')
async def nitroproof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(NitroModal())

# ============================================================
# ROBUX PROOF
# ============================================================
class RobuxPage:
    def __init__(self, gifter_username, receiver_username, receiver_message,
                 gifter_avatar_url, receiver_avatar_url, timestamp_1, timestamp_2, full_date):
        self.gifter_username = sanitize(gifter_username)
        self.receiver_username = sanitize(receiver_username)
        self.receiver_message = sanitize(receiver_message)
        self.gifter_avatar_url = gifter_avatar_url
        self.receiver_avatar_url = receiver_avatar_url
        self.timestamp_1 = timestamp_1
        self.timestamp_2 = timestamp_2
        self.full_date = full_date.lstrip('0') if full_date.startswith('0') else full_date

    def get_proof(self):
        with open("assets/robuxproof.html", 'r', encoding="utf-8") as file:
            content = file.read()
        
        content = content.replace('GIFTER_USERNAME', self.gifter_username)
        content = content.replace('RECEIVER_USERNAME', self.receiver_username)
        content = content.replace('RECEIVER_MESSAGE', self.receiver_message)
        content = content.replace('GIFTER_AVATAR_URL', self.gifter_avatar_url)
        content = content.replace('RECEIVER_AVATAR_URL', self.receiver_avatar_url)
        content = content.replace('TIMESTAMP_1', self.timestamp_1)
        content = content.replace('TIMESTAMP_2', self.timestamp_2)
        content = content.replace('FULL_DATE', self.full_date)
        return content

class RobuxModal(discord.ui.Modal, title='Robux proof generator'):
    gifter_id = discord.ui.TextInput(
        label="Gifter's ID (leave empty for yours)",
        style=discord.TextStyle.short,
        placeholder='12345678901234567890',
        required=False,
    )
    receiver_id = discord.ui.TextInput(
        label="Receiver's ID (leave empty for random)",
        style=discord.TextStyle.short,
        placeholder='12345678901234567890',
        required=False,
    )
    receiver_text = discord.ui.TextInput(
        label="Receiver's message",
        style=discord.TextStyle.short,
        placeholder='OMG! Thanks!',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            gifter = interaction.user
            note = ""
            if self.gifter_id.value:
                try:
                    gifter = await client.fetch_user(int(self.gifter_id.value))
                except Exception:
                    note = "Note: Invalid Gifter ID"
            
            members = await interaction.guild.chunk()
            receiver = random.choice(members)
            if self.receiver_id.value:
                try:
                    receiver = await client.fetch_user(int(self.receiver_id.value))
                except Exception:
                    note = "Note: Invalid Receiver ID"
            
            times = generate_time_range(interaction)
            
            proof = RobuxPage(
                get_user_name(gifter), get_user_name(receiver),
                self.receiver_text.value,
                get_user_avatar(gifter), get_user_avatar(receiver),
                times[0], times[1], times[2]
            ).get_proof()
            
            await take_screenshot(proof, random.randint(1, 8), random.randint(130, 135),
                                  random.randint(850, 1100), random.randint(350, 355), 1300, 500)
            
            await interaction.followup.send(embed=send_success_embed(interaction, note))
            await interaction.user.send(file=discord.File('proof.png'))
            
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(embed=send_error_embed(interaction, str(e)[:500]))

@client.tree.command(description='Generate proof for a robux giveaway.')
async def robuxproof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(RobuxModal())

# ============================================================
# MINECRAFT PROOF
# ============================================================
class MinecraftPage:
    def __init__(self, gifter_username, receiver_username, receiver_message,
                 gifter_avatar_url, receiver_avatar_url, timestamp_1, timestamp_2, full_date):
        self.gifter_username = sanitize(gifter_username)
        self.receiver_username = sanitize(receiver_username)
        self.receiver_message = sanitize(receiver_message)
        self.gifter_avatar_url = gifter_avatar_url
        self.receiver_avatar_url = receiver_avatar_url
        self.timestamp_1 = timestamp_1
        self.timestamp_2 = timestamp_2
        self.full_date = full_date.lstrip('0') if full_date.startswith('0') else full_date

    def get_proof(self):
        with open("assets/minecraftproof.html", 'r', encoding="utf-8") as file:
            content = file.read()
        
        content = content.replace('GIFTER_USERNAME', self.gifter_username)
        content = content.replace('RECEIVER_USERNAME', self.receiver_username)
        content = content.replace('RECEIVER_MESSAGE', self.receiver_message)
        content = content.replace('GIFTER_AVATAR_URL', self.gifter_avatar_url)
        content = content.replace('MC_EMAIL', 'user' + str(random.randint(1, 10000000)) + '@gmail.com')
        content = content.replace('MC_PASS', 'pass' + str(random.randint(1, 10000000)))
        content = content.replace('RECEIVER_AVATAR_URL', self.receiver_avatar_url)
        content = content.replace('TIMESTAMP_1', self.timestamp_1)
        content = content.replace('TIMESTAMP_2', self.timestamp_2)
        content = content.replace('FULL_DATE', self.full_date)
        return content

class MinecraftModal(discord.ui.Modal, title='Minecraft proof generator'):
    gifter_id = discord.ui.TextInput(
        label="Gifter's ID (leave empty for yours)",
        style=discord.TextStyle.short,
        placeholder='12345678901234567890',
        required=False,
    )
    receiver_id = discord.ui.TextInput(
        label="Receiver's ID (leave empty for random)",
        style=discord.TextStyle.short,
        placeholder='12345678901234567890',
        required=False,
    )
    receiver_text = discord.ui.TextInput(
        label="Receiver's message",
        style=discord.TextStyle.short,
        placeholder='OMG! Thanks!',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            gifter = interaction.user
            note = ""
            if self.gifter_id.value:
                try:
                    gifter = await client.fetch_user(int(self.gifter_id.value))
                except Exception:
                    note = "Note: Invalid Gifter ID"
            
            members = await interaction.guild.chunk()
            receiver = random.choice(members)
            if self.receiver_id.value:
                try:
                    receiver = await client.fetch_user(int(self.receiver_id.value))
                except Exception:
                    note = "Note: Invalid Receiver ID"
            
            times = generate_time_range(interaction)
            
            proof = MinecraftPage(
                get_user_name(gifter), get_user_name(receiver),
                self.receiver_text.value,
                get_user_avatar(gifter), get_user_avatar(receiver),
                times[0], times[1], times[2]
            ).get_proof()
            
            await take_screenshot(proof, random.randint(1, 8), random.randint(170, 180),
                                  random.randint(850, 1100), random.randint(300, 320), 1300, 500)
            
            await interaction.followup.send(embed=send_success_embed(interaction, note))
            await interaction.user.send(file=discord.File('proof.png'))
            
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(embed=send_error_embed(interaction, str(e)[:500]))

@client.tree.command(description='Generate proof for a minecraft giveaway.')
async def minecraftproof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(MinecraftModal())

# ============================================================
# BOOSTS PROOF
# ============================================================
class BoostsPage:
    def __init__(self, channel_name, gifter_username, timestamp_1, full_date):
        self.channel_name = sanitize(channel_name)
        self.gifter_username = sanitize(gifter_username)
        self.timestamp_1 = timestamp_1
        self.full_date = full_date.lstrip('0') if full_date.startswith('0') else full_date

    def get_proof(self):
        with open("assets/boostproof.html", 'r', encoding="utf-8") as file:
            content = file.read()
        
        content = content.replace('CHANNEL_NAME', self.channel_name)
        content = content.replace('BOOSTER_USERNAME', self.gifter_username)
        content = content.replace('TIMESTAMP_1', f'Today at {self.timestamp_1}')
        content = content.replace('FULL_DATE', self.full_date)
        return content

class BoostsModal(discord.ui.Modal, title='14x Boosts proof generator'):
    booster_username = discord.ui.TextInput(
        label="Booster Username (leave empty for yours)",
        placeholder=".gg/proofgen",
        style=discord.TextStyle.short,
        required=False,
    )
    channel_name = discord.ui.TextInput(
        label='Channel name (leave empty for general)',
        style=discord.TextStyle.short,
        placeholder='general',
        required=False,
        max_length=32,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            if self.booster_username.value:
                gifter_name = self.booster_username.value
            else:
                gifter_name = get_user_name(interaction.user)
            
            channel_name = self.channel_name.value if self.channel_name.value else "general"
            
            times = generate_time_range(interaction)
            
            proof = BoostsPage(channel_name, gifter_name, times[0], times[2]).get_proof()
            
            await take_screenshot(proof, 0, 140, 950, 550, 1350, 700)
            
            await interaction.followup.send(embed=send_success_embed(interaction))
            await interaction.user.send(file=discord.File('proof.png'))
            
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(embed=send_error_embed(interaction, str(e)[:500]))

@client.tree.command(description='Generate proof for a 14x boost sale.')
async def boostsproof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(BoostsModal())

# ============================================================
# INVENTORY PROOF
# ============================================================
class InventoryPage:
    def __init__(self, gifter_username, nitro_amount, basic_amount):
        self.gifter_username = sanitize(gifter_username)
        self.nitro_amount = sanitize(nitro_amount)
        self.basic_amount = sanitize(basic_amount)

    def get_proof(self):
        with open("assets/inventorypage.html", 'r', encoding="utf-8") as file:
            content = file.read()
        
        content = content.replace('USERNAME', self.gifter_username)
        content = content.replace('BOOSTAMOUNT', self.nitro_amount)
        content = content.replace('BASICAMOUNT', self.basic_amount)
        return content

class InventoryModal(discord.ui.Modal, title='Inventory proof generator'):
    username = discord.ui.TextInput(
        label="Username (leave empty for yours)",
        placeholder="mahdi1337",
        style=discord.TextStyle.short,
        required=False,
    )
    nitro_amount = discord.ui.TextInput(
        label='Boost amount',
        style=discord.TextStyle.short,
        placeholder='10',
        required=False,
        max_length=32
    )
    basic_amount = discord.ui.TextInput(
        label='Basic amount',
        style=discord.TextStyle.short,
        placeholder='10',
        required=False,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            if self.username.value:
                gifter_name = self.username.value
            else:
                gifter_name = get_user_name(interaction.user)
            
            nitro_amt = self.nitro_amount.value if self.nitro_amount.value else "0"
            basic_amt = self.basic_amount.value if self.basic_amount.value else "0"
            
            proof = InventoryPage(gifter_name, nitro_amt, basic_amt).get_proof()
            
            await take_screenshot(proof, 0, 0, 1070, 1150, 1350, 1100)
            
            await interaction.followup.send(embed=send_success_embed(interaction))
            await interaction.user.send(file=discord.File('proof.png'))
            
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(embed=send_error_embed(interaction, str(e)[:500]))

@client.tree.command(description='Generate proof of a gift inventory.')
async def inventoryproof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(InventoryModal())

# ============================================================
# PAYPAL PROOF
# ============================================================
class PaypalPage:
    def __init__(self, amount, receiver):
        amount = str(amount)
        if ',' not in amount:
            amount += ',00'
        if '.' in amount:
            amount = amount.replace('.', ',')
        if '$' in amount:
            amount = amount.replace('$', '')
        self.amount = amount
        self.receiver = sanitize(receiver)

    def get_proof(self):
        with open("assets/paypal_page.html", 'r', encoding="utf-8") as file:
            content = file.read()
        
        content = content.replace('AMOUNT', self.amount)
        content = content.replace('RECEIVER', self.receiver)
        return content

class PaypalModal(discord.ui.Modal, title='Paypal transaction proof generator'):
    receiver_name = discord.ui.TextInput(
        label="Receiver Name",
        placeholder="mahdi",
        style=discord.TextStyle.short,
        required=True,
    )
    amount = discord.ui.TextInput(
        label='Amount',
        style=discord.TextStyle.short,
        placeholder='10',
        required=True,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            proof = PaypalPage(self.amount.value, self.receiver_name.value).get_proof()
            
            with open("assets/temp.html", "w", encoding="utf-8") as f:
                f.write(proof)
            
            browser = await launch_browser()
            page = await browser.newPage()
            await page.setViewport({'width': 1280, 'height': 1024})
            absolute_path = f'file://{os.path.abspath("assets/temp.html")}'
            await page.goto(absolute_path, waitUntil='networkidle0')
            await page.screenshot({'path': 'proof.png', 'fullPage': True})
            await browser.close()
            
            await interaction.followup.send(embed=send_success_embed(interaction))
            await interaction.user.send(file=discord.File('proof.png'))
            
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(embed=send_error_embed(interaction, str(e)[:500]))

@client.tree.command(description='Generate proof of a paypal transaction.')
async def paypalproof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(PaypalModal())

# ============================================================
# PROOF & HELP KOMUTLARI
# ============================================================
@client.tree.command(description='See all the proof generator commands.')
async def proof(interaction: discord.Interaction):
    if interaction.channel.id not in channels:
        embed = discord.Embed(color=0xFF0000, title="Error", description="> Oops! You can't use this command here.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        color=0x717CDA,
        title="Proof Generator",
        description="/nitroproof\n/inventoryproof\n/robuxproof\n/minecraftproof\n/paypalproof\n/boostsproof\n/bloxfruitsproof - COMING SOON\n/cashappproof - COMING SOON"
    )
    embed.set_footer(text="PekkleDev")
    await interaction.response.send_message(embed=embed, delete_after=10)

@client.tree.command(description='See help.')
async def help(interaction: discord.Interaction):
    await proof.callback(interaction)

# ============================================================
# BOT BAŞLAT
# ============================================================
if __name__ == "__main__":
    if not token:
        print(" TOKEN ortam değişkeni bulunamadı!")
    else:
        client.run(token)
