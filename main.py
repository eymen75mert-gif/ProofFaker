
import os
import random
import string
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def generate_code():
    chars = string.ascii_uppercase + string.digits
    parts = [
        "".join(random.choices(chars, k=4))
        for _ in range(3)
    ]
    return "NITRO-" + "-".join(parts)


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
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Tür",
        value=tur.value,
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
            "1. Discord'u aç.\n"
            "2. Kullanıcı Ayarları'na gir.\n"
            "3. Hediye Envanteri / Redeem Code bölümünü aç.\n"
            "4. Kodunu gir ve onayla."
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)


@nitro.error
async def nitro_error(interaction, error):
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


if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN ayarlanmamış!")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} aktif!")


bot.run(TOKEN)
