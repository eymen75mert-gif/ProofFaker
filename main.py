
import os
import random
import string
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def generate_nitro_code():
    alphabet = string.ascii_uppercase + string.digits
    parts = [
        "".join(random.choices(alphabet, k=4))
        for _ in range(3)
    ]
    return "NİTRO-" + "-".join(parts)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{bot.user} aktif! {len(synced)} komut senkronize edildi.")
    except Exception as error:
        print(f"Komut hatası: {error}")


@bot.tree.command(
    name="nitro",
    description="Rastgele bir örnek Nitro kodu oluşturur."
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def nitro(interaction: discord.Interaction):
    code = generate_nitro_code()

    embed = discord.Embed(
        title="🎁 Nitro Kod Oluşturucu",
        description=(
            f"```{code}```\n"
            "Bu kod rastgele oluşturulmuş bir örnektir; "
            "gerçek bir Nitro hediyesi değildir.\n\n"
            "**Kullanım:** Gerçek bir hediye kodunuz varsa "
            "Discord → Kullanıcı Ayarları → "
            "Hediye Envanteri bölümünden kullanabilirsiniz."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


@nitro.error
async def nitro_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ Bu komutu yalnızca yöneticiler kullanabilir."
    else:
        message = "Bir hata oluştu. Bot ayarlarını kontrol edin."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True
        )


if not TOKEN:
    raise RuntimeError(
        "DISCORD_BOT_TOKEN ortam değişkeni ayarlanmamış!"
    )

bot.run(TOKEN)
