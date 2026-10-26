
import os
import random
import string
import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# AYARLAR
# ==========================================
TOKEN = os.getenv("TOKEN")

PROOF_CHANNEL_ID = 1563982186011435232
STATUS_ROLE_ID = 1563982169100132484
STATUS_LOG_CHANNEL_ID = 1563982173491564594

REQUIRED_STATUS_TEXT = "/trnitro"

# ==========================================
# BOT
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)


def generate_code():
    chars = string.ascii_uppercase + string.digits
    parts = [
        "".join(random.choices(chars, k=4))
        for _ in range(3)
    ]
    return "NITRO-" + "-".join(parts)


# ==========================================
# /NITRO
# ==========================================
@bot.tree.command(
    name="nitro",
    description="Tür ve süre seçerek kod oluştur."
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    tur=[
        app_commands.Choice(name="Basic", value="Basic"),
        app_commands.Choice(name="Boost", value="Boost"),
    ],
    sure=[
        app_commands.Choice(name="Aylık", value="Aylık"),
        app_commands.Choice(name="Yıllık", value="Yıllık"),
    ]
)
async def nitro(
    interaction: discord.Interaction,
    tur: app_commands.Choice[str],
    sure: app_commands.Choice[str]
):
    code = generate_code()

    embed = discord.Embed(
        title="🎁 Nitro Kod",
        color=discord.Color.gold()
    )
    embed.add_field(name="Tür", value=tur.value, inline=True)
    embed.add_field(name="Süre", value=sure.value, inline=True)
    embed.add_field(name="Kod", value=f"```{code}```", inline=False)
    embed.add_field(
        name="📌 Nasıl kullanılır?",
        value=(
            "1. Discord Kullanıcı Ayarları'nı aç.\n"
            "2. Hediye Envanteri veya kod kullanma bölümüne gir.\n"
            "3. Geçerli hediye kodunu gir."
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)



# ==========================================
# /ROBUX
# ==========================================
@bot.tree.command(
    name="robux",
    description="Robux miktarını ve süreyi seçerek kod oluştur."
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    miktar=[
        app_commands.Choice(name="450 Robux", value="450"),
        app_commands.Choice(name="1500 Robux", value="1500"),
        app_commands.Choice(name="4500 Robux", value="4500"),
        app_commands.Choice(name="10000 Robux", value="10000"),
        app_commands.Choice(name="5000 Robux", value="5000"),
    ],
    sure=[
        app_commands.Choice(name="Aylık", value="Aylık"),
        app_commands.Choice(name="Yıllık", value="Yıllık"),
    ]
)
async def robux(
    interaction: discord.Interaction,
    miktar: app_commands.Choice[str],
    sure: app_commands.Choice[str]
):
    chars = string.ascii_uppercase + string.digits
    code = "ROBUX-" + "-".join(
        "".join(random.choices(chars, k=4))
        for _ in range(3)
    )

    embed = discord.Embed(
        title="💰 Robux Ödülü",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Miktar",
        value=f"{miktar.value} Robux",
        inline=True
    )
    embed.add_field(
        name="Süre",
        value=sure.value,
        inline=True
    )
    embed.add_field(
        name="Kod",
        value=f"```{code}```",
        inline=False
    )
    embed.add_field(
        name="📌 Nasıl kullanılır?",
        value=(
            "Roblox'un resmi web sitesini aç.\n"
            "Gerçek bir hediye kartın varsa resmi "
            "kod kullanma sayfasından kullan:\n"
            "https://www.roblox.com/redeem"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)



# ==========================================
# /DMALL - ÜYELERE ÖZEL MESAJ
# ==========================================
@bot.tree.command(
    name="dmall",
    description="Sunucu üyelerine özel mesaj gönder."
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(mesaj="Üyelere gönderilecek mesaj")
async def dmall(
    interaction: discord.Interaction,
    mesaj: str
):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    if guild is None:
        await interaction.followup.send(
            "Bu komut yalnızca sunucuda kullanılabilir.",
            ephemeral=True
        )
        return

    sent = 0
    failed = 0

    # Özel mesajları yalnızca açıkça kabul etmiş
    # üyelere gönderecek şekilde genişletilebilir.
    for member in guild.members:
        if member.bot:
            continue

        try:
            embed = discord.Embed(
                title="📩 Sunucu Mesajı",
                description=mesaj[:4000],
                color=discord.Color.blurple()
            )
            embed.set_footer(
                text=f"{guild.name} • Sunucu Duyurusu"
            )

            await member.send(embed=embed)
            sent += 1

        except (discord.Forbidden, discord.HTTPException):
            failed += 1

    await interaction.followup.send(
        f"📬 DM gönderimi tamamlandı.\n"
        f"✅ Gönderilen: {sent}\n"
        f"⚠️ Gönderilemeyen: {failed}",
        ephemeral=True
    )



# ==========================================
# /PROOF
# ==========================================
@bot.tree.command(
    name="proof",
    description="Ödül kazanım görselini belirlenen kanala gönder."
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(gorsel_url="Gönderilecek görselin URL'si")
async def proof(
    interaction: discord.Interaction,
    gorsel_url: str
):
    if not gorsel_url.startswith("https://"):
        await interaction.response.send_message(
            "HTTPS görsel bağlantısı gir.",
            ephemeral=True
        )
        return

    channel = bot.get_channel(PROOF_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(PROOF_CHANNEL_ID)
        except discord.HTTPException:
            await interaction.response.send_message(
                "Belirlenen kanal bulunamadı.",
                ephemeral=True
            )
            return

    embed = discord.Embed(
        title="🏆・ÖDÜL KAZANILDI!",
        description=(
            "✨ Tebrikler!\n\n"
            "Bir kullanıcı davet yaparak ödül kazandı!\n"
            "🎉 Katılımın ve desteğin için teşekkür ederiz.\n\n"
            "💛 Yeni ödüller için bizi takip etmeye devam et!"
        ),
        color=discord.Color.gold()
    )
    embed.set_image(url=gorsel_url)
    embed.set_footer(text="Ödül Sistemi • Başarılar dileriz!")

    try:
        await channel.send(embed=embed)
    except (discord.HTTPException, discord.Forbidden):
        await interaction.response.send_message(
            "Mesaj gönderilemedi. Kanal izinlerini kontrol et.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ Ödül mesajı <#{PROOF_CHANNEL_ID}> kanalına gönderildi.",
        ephemeral=True
    )


# ==========================================
# DURUM METNİNE GÖRE OTOMATİK ROL + LOG
# ==========================================
@bot.event
async def on_presence_update(before, after):
    if after.bot:
        return

    role = after.guild.get_role(STATUS_ROLE_ID)
    if role is None:
        return

    def get_custom_status(member):
        for activity in member.activities:
            if isinstance(activity, discord.CustomActivity):
                return str(activity.state or "").casefold()
        return ""

    old_status = get_custom_status(before)
    new_status = get_custom_status(after)

    required = REQUIRED_STATUS_TEXT.casefold()
    had_text = required in old_status
    has_text = required in new_status

    # Durum metni değişmediyse işlem yapma
    if had_text == has_text:
        return

    log_channel = bot.get_channel(STATUS_LOG_CHANNEL_ID)

    try:
        if has_text and role not in after.roles:
            await after.add_roles(
                role,
                reason="Gerekli durum metni eklendi"
            )

            embed = discord.Embed(
                title="✅ Otomatik Rol Verildi",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(
                name="Üye",
                value=f"{after.mention} (`{after.id}`)",
                inline=False
            )
            embed.add_field(name="Rol", value=role.mention, inline=True)
            embed.add_field(
                name="Durum",
                value=REQUIRED_STATUS_TEXT,
                inline=True
            )

        elif not has_text and role in after.roles:
            await after.remove_roles(
                role,
                reason="Gerekli durum metni kaldırıldı"
            )

            embed = discord.Embed(
                title="➖ Otomatik Rol Kaldırıldı",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(
                name="Üye",
                value=f"{after.mention} (`{after.id}`)",
                inline=False
            )
            embed.add_field(name="Rol", value=role.mention, inline=True)
            embed.add_field(
                name="Durum",
                value="Gerekli metin kaldırıldı",
                inline=True
            )
        else:
            return

        if log_channel:
            await log_channel.send(embed=embed)

    except discord.Forbidden:
        print("Rol işlemi başarısız: bot izinlerini kontrol et.")
    except discord.HTTPException as error:
        print(f"Discord API hatası: {error}")


# ==========================================
# KOMUT HATALARI
# ==========================================
@nitro.error
@proof.error
async def command_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ Bu komutu yalnızca yöneticiler kullanabilir."
    else:
        print(f"Komut hatası: {error}")
        message = "Bir hata oluştu. Bot ayarlarını kontrol et."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# ==========================================
# BAŞLAT
# ==========================================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(
            f"{bot.user} aktif! "
            f"{len(synced)} komut senkronize edildi."
        )
    except discord.HTTPException as error:
        print(f"Komut senkronizasyon hatası: {error}")


if not TOKEN:
    raise RuntimeError(
        "DISCORD_BOT_TOKEN ortam değişkeni ayarlanmamış!"
    )

bot.run(TOKEN)
