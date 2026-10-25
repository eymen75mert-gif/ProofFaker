
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


class NitroView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.plan = None

    @discord.ui.select(
        placeholder="1. Abonelik türünü seç",
        options=[
            discord.SelectOption(label="Basic", value="Basic"),
            discord.SelectOption(label="Nitro", value="Nitro"),
        ]
    )
    async def select_plan(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        self.plan = select.values[0]
        await interaction.response.send_message(
            f"Seçilen tür: **{self.plan}**\nŞimdi süreyi seç:",
            view=DurationView(self.plan),
            ephemeral=True
        )


class DurationView(discord.ui.View):
    def __init__(self, plan):
        super().__init__(timeout=60)
        self.plan = plan

    @discord.ui.select(
        placeholder="2. Abonelik süresini seç",
        options=[
            discord.SelectOption(label="Aylık", value="Aylık"),
            discord.SelectOption(label="Yıllık", value="Yıllık"),
        ]
    )
    async def select_duration(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        duration = select.values[0]
        code = generate_code()

        embed = discord.Embed(
            title="🎁 Nitro Kod",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Tür", value=self.plan, inline=True)
        embed.add_field(name="Süre", value=duration, inline=True)
        embed.add_field(
            name="Kod",
            value=f"```{code}```",
            inline=False
        )

        await interaction.response.send_message(
            "Seçiminiz tamamlandı!",
            ephemeral=True
        )
        await interaction.channel.send(embed=embed)


@bot.tree.command(
    name="nitro",
    description="Abonelik türünü ve süresini seç."
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def nitro(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🎁 **Abonelik türünü seç:**",
        view=NitroView(),
        ephemeral=True
    )


@nitro.error
async def nitro_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        message = "Bu komutu yalnızca yöneticiler kullanabilir."
    else:
        message = "Bir hata oluştu."

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
