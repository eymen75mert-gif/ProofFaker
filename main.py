
import os
import random
import discord
from discord.ext import commands
from discord import app_commands

# ==========================================
# AYARLAR
# ==========================================

TOKEN = os.getenv("TOKEN")

PROOF_CHANNEL_ID = 1563982186011435232
STATUS_ROLE_ID = 1563982169100132484
STATUS_LOG_CHANNEL_ID = 1563982173491564594

# Boş bırakırsan otomatik algılama denenir
GUILD_TAG = "free"

REQUIRED_STATUS_TEXTS = [
    "/trnitro",
    ".gg/trnitro",
    "@trnitro"
]

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================

def random_code(prefix):
    parts = [
        "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4))
        for _ in range(3)
    ]
    return f"{prefix}-{'-'.join(parts)}"


async def send_role_log(member, message):
    channel = member.guild.get_channel(STATUS_LOG_CHANNEL_ID)
    if channel is None:
        return

    embed = discord.Embed(
        title="📋 Durum / Guild Tag Rol Kaydı",
        description=(
            f"**Üye:** {member.mention}\n"
            f"**ID:** `{member.id}`\n"
            f"**İşlem:** {message}"
        ),
        color=discord.Color.gold()
    )
    await channel.send(embed=embed)


def has_required_status(member):
    for activity in getattr(member, "activities", []):
        if isinstance(activity, discord.CustomActivity):
            status = activity.name or ""
            if any(text.casefold() in status.casefold()
                   for text in REQUIRED_STATUS_TEXTS):
                return True
    return False


def has_server_guild_tag(member):
    # Discord.py sürümünün sunduğu profil alanlarını kontrol eder.
    primary_guild = getattr(member, "primary_guild", None)
    if primary_guild is None:
        return False

    identity_guild_id = getattr(primary_guild, "identity_guild_id", None)
    identity_enabled = getattr(primary_guild, "identity_enabled", False)
    tag = getattr(primary_guild, "tag", None)

    # Tag açıkça ayarlanmışsa tam eşleşme ara.
    if GUILD_TAG:
        return (
            str(identity_guild_id) == str(member.guild.id)
            and identity_enabled is True
            and tag == GUILD_TAG
        )

    # Tag ayarı boşsa Discord'un sunduğu profil bilgisini kullan.
    return (
        str(identity_guild_id) == str(member.guild.id)
        and identity_enabled is True
        and bool(tag)
    )


async def update_special_role(member):
    if member.bot:
        return

    role = member.guild.get_role(STATUS_ROLE_ID)
    if role is None:
        return

    status_match = has_required_status(member)
    tag_match = has_server_guild_tag(member)

    # Durum veya Guild Tag koşullarından biri yeterli.
    should_have_role = status_match or tag_match
    already_has_role = role in member.roles

    try:
        if should_have_role and not already_has_role:
            await member.add_roles(
                role,
                reason="Belirlenen durum veya Guild Tag eşleşti"
            )

            reasons = []
            if status_match:
                reasons.append("Belirlenen durum")
            if tag_match:
                reasons.append("Sunucu Guild Tag'i")

            await send_role_log(
                member,
                "✅ Rol verildi: " + " + ".join(reasons)
            )

        elif not should_have_role and already_has_role:
            await member.remove_roles(
                role,
                reason="Durum ve Guild Tag koşulları artık sağlanmıyor"
            )
            await send_role_log(
                member,
                "❌ Rol kaldırıldı: Durum ve Guild Tag koşulları sağlanmıyor."
            )

    except discord.Forbidden:
        print(f"{member} için rol işlemi yapılamadı: izin veya rol sırası.")
    except discord.HTTPException as error:
        print(f"Rol işlem hatası: {error}")


# ==========================================
# /NITRO
# ==========================================

@bot.tree.command(name="nitro", description="Örnek Nitro kodu oluşturur.")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    tur=[
        app_commands.Choice(name="Basic", value="Basic"),
        app_commands.Choice(name="Boost", value="Boost")
    ],
    sure=[
        app_commands.Choice(name="Aylık", value="Aylık"),
        app_commands.Choice(name="Yıllık", value="Yıllık")
    ]
)
async def nitro(
    interaction: discord.Interaction,
    tur: app_commands.Choice[str],
    sure: app_commands.Choice[str]
):
    code = random_code("NITRO")
    embed = discord.Embed(
        title="🎁 Nitro Kod Örneği",
        description=(
            f"**Tür:** {tur.value}\n"
            f"**Süre:** {sure.value}\n"
            f"**Kod:** `{code}`\n\n"
            "Bu rastgele oluşturulmuş örnek bir koddur; gerçek Nitro sağlamaz."
        ),
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# /ROBUX
# ==========================================

@bot.tree.command(name="robux", description="Örnek Robux kodu oluşturur.")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    miktar=[
        app_commands.Choice(name="450 Robux", value=450),
        app_commands.Choice(name="1500 Robux", value=1500),
        app_commands.Choice(name="4500 Robux", value=4500),
        app_commands.Choice(name="5000 Robux", value=5000),
        app_commands.Choice(name="10000 Robux", value=10000)
    ],
    sure=[
        app_commands.Choice(name="Aylık", value="Aylık"),
        app_commands.Choice(name="Yıllık", value="Yıllık")
    ]
)
async def robux(
    interaction: discord.Interaction,
    miktar: app_commands.Choice[int],
    sure: app_commands.Choice[str]
):
    code = random_code("ROBUX")
    embed = discord.Embed(
        title="🎮 Robux Kod Örneği",
        description=(
            f"**Miktar:** {miktar.value} Robux\n"
            f"**Süre:** {sure.value}\n"
            f"**Kod:** `{code}`\n\n"
            "Bu rastgele oluşturulmuş örnek bir koddur; Robux sağlamaz."
        ),
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# /PROOF
# ==========================================

@bot.tree.command(name="proof", description="Ödül görselini kanala gönderir.")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(gorsel_url="Görselin doğrudan URL'si")
async def proof(
    interaction: discord.Interaction,
    gorsel_url: str
):
    channel = bot.get_channel(PROOF_CHANNEL_ID)

    if channel is None:
        await interaction.response.send_message(
            "Proof kanalı bulunamadı. Kanal ID'sini kontrol et.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🏆 ÖDÜL KAZANILDI!",
        description="Davet etkinliği ödül bildirimi.",
        color=discord.Color.gold()
    )
    embed.set_image(url=gorsel_url)

    await channel.send(embed=embed)
    await interaction.response.send_message(
        "Proof görseli gönderildi.",
        ephemeral=True
    )


# ==========================================
# /DMALL
# ==========================================

@bot.tree.command(name="dmall", description="Üyelere duyuru DM'si gönderir.")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(mesaj="Gönderilecek duyuru")
async def dmall(interaction: discord.Interaction, mesaj: str):
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "Bu komut sunucuda kullanılmalı.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    sent = 0
    failed = 0

    # Üye listesinin dolu olmasını sağlamayı dener.
    try:
        await guild.chunk(cache=True)
    except (discord.HTTPException, discord.Forbidden):
        pass

    for member in guild.members:
        if member.bot:
            continue

        try:
            embed = discord.Embed(
                title="📩 Sunucu Duyurusu",
                description=mesaj[:4000],
                color=discord.Color.blurple()
            )
            embed.set_footer(text=guild.name)
            await member.send(embed=embed)
            sent += 1

        except (discord.Forbidden, discord.HTTPException):
            failed += 1

    await interaction.followup.send(
        f"📬 DM denemesi tamamlandı.\n"
        f"✅ Gönderilen: {sent}\n"
        f"⚠️ Gönderilemeyen: {failed}",
        ephemeral=True
    )


# ==========================================
# DURUM DEĞİŞİKLİĞİ
# ==========================================

@bot.event
async def on_presence_update(before, after):
    await update_special_role(after)


# ==========================================
# ÜYE GÜNCELLEMESİ
# ==========================================

@bot.event
async def on_member_update(before, after):
    await update_special_role(after)


# ==========================================
# ÜYE SUNUCUYA KATILINCA
# ==========================================

@bot.event
async def on_member_join(member):
    await update_special_role(member)


# ==========================================
# BOT HAZIR
# ==========================================

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash komutu senkronize edildi.")
    except discord.HTTPException as error:
        print(f"Komut senkronizasyon hatası: {error}")


# ==========================================
# ÇALIŞTIR
# ==========================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_BOT_TOKEN ortam değişkenini ayarla."
    )

bot.run(TOKEN)
