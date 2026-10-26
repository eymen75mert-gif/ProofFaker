
import os
import random
import string
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

# /proof mesajının gönderileceği kanal ID'sini buraya yaz
PROOF_CHANNEL_ID = 1563982186011435232

# Otomatik durum rolü ayarları
STATUS_ROLE_ID = 1563982169100132484
REQUIRED_STATUS_TEXT = "/trnitro"


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def generate_code():
    chars = string.ascii_uppercase + string.digits
    parts = [
        "".join(random.choices(chars, k=4))
        for _ in range(3)
    ]
    return "NITRO-" + "-".join(parts)


@bot.tree.command(name="nitro", description="Nitro kodu oluştur.")
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
    # Yalnızca HTTP/HTTPS görsel bağlantılarına izin ver
    if not gorsel_url.startswith(("https://", "http://")):
        await interaction.response.send_message(
            "Lütfen geçerli bir HTTPS görsel URL'si gir.",
            ephemeral=True
        )
        return

    channel = bot.get_channel(PROOF_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(PROOF_CHANNEL_ID)
        except discord.HTTPException:
            await interaction.response.send_message(
                "Belirlenen kanal bulunamadı. Kanal ID'sini kontrol et.",
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
    except discord.HTTPException:
        await interaction.response.send_message(
            "Mesaj gönderilemedi. Botun kanal izinlerini ve görsel URL'sini kontrol et.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ Ödül mesajı <#{PROOF_CHANNEL_ID}> kanalına gönderildi.",
        ephemeral=True
    )


@nitro.error
@proof.error
async def command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ Bu komutu yalnızca yöneticiler kullanabilir."
    else:
        message = "Bir hata oluştu. Bot ayarlarını kontrol et."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(
            message, ephemeral=True
        )


intents.members = True
intents.presences = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_presence_update(before, after):
    if after.bot:
        return

    role = after.guild.get_role(STATUS_ROLE_ID)
    if role is None:
        return

    activity_text = " ".join(
        str(getattr(activity, "state", "") or "")
        + " "
        + str(getattr(activity, "name", "") or "")
        for activity in after.activities
    ).casefold()

    if REQUIRED_STATUS_TEXT.casefold() in activity_text:
        if role not in after.roles:
            try:
                await after.add_roles(
                    role,
                    reason="Gerekli durum metni algılandı"
                )
            except discord.Forbidden:
                print("Botun rol verme yetkisi yok.")



if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN ortam değişkeni ayarlanmamış!")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} aktif!")


bot.run(TOKEN)
