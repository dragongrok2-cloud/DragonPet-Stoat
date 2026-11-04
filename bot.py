#!/usr/bin/env python3
"""
Dragon Pet — добрый дракон-питомец для Stoat.
"""

import os
import random
import asyncio
from dotenv import load_dotenv

try:
    from stoat import Client
    from stoat.ext import commands
except ImportError:
    print("Установи зависимости: pip install -r requirements.txt")
    raise

load_dotenv()

TOKEN = os.getenv("STOAT_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

if not TOKEN:
    raise SystemExit("Нужен STOAT_TOKEN в .env")

# -------------------- Состояние питомца --------------------

class DragonState:
    def __init__(self):
        self.happiness = 80
        self.energy = 70
        self.mood = "довольный"
        self.last_pet = None

    def pet(self):
        self.happiness = min(100, self.happiness + random.randint(8, 18))
        self.energy = max(10, self.energy - random.randint(3, 8))
        self._update_mood()
        return self.happiness

    def rest(self):
        self.energy = min(100, self.energy + random.randint(15, 30))
        self.happiness = min(100, self.happiness + random.randint(5, 12))
        self._update_mood()
        return self.energy

    def _update_mood(self):
        if self.happiness >= 85 and self.energy >= 60:
            self.mood = "очень довольный"
        elif self.happiness >= 60:
            self.mood = "довольный"
        elif self.happiness >= 40:
            self.mood = "спокойный"
        else:
            self.mood = "хочет внимания"

state = DragonState()

# -------------------- Фразы --------------------

PET_PHRASES = [
    "*тихо урчит и подставляет голову под ладонь* ммм... приятно~",
    "*прикрывает глаза и чуть виляет хвостом* спасибо, всадник...",
    "*низко мурлычет, прижимаясь щекой* ещё чуть-чуть...",
    "*тепло выдыхает дымок и трётся лбом* люблю, когда меня гладят",
    "*складывает крылья и полностью расслабляется* идеально~",
]

PURR_PHRASES = [
    "*глубоко и довольно мурлычет* ррррр~",
    "*закрывает глаза и издаёт низкое довольное урчание*",
    "*вибрирует всем телом от удовольствия* мммррр...",
]

REST_PHRASES = [
    "*сворачивается клубочком, подкладывая хвост под морду* сейчас отдохну...",
    "*медленно складывает крылья и устраивается поудобнее* спасибо, что разрешил",
    "*зевает, показывая клыки, и ложится* немного покемарю~",
]

NUZZLE_PHRASES = [
    "*осторожно тычется мокрым носом в ладонь* привет...",
    "*прижимается щекой и тихо сопит* я тут",
    "*трётся головой о плечо* не уходи пока",
]

WING_PHRASES = [
    "*осторожно накрывает тебя тёплым крылом* вот так лучше?",
    "*подставляет крыло, чтобы можно было прислониться* устраивайся",
    "*расправляет одно крыло как одеяло* грейся",
]

# -------------------- Бот --------------------

bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_ready(event):
    print(f"Дракон проснулся: {bot.me}")
    print(f"Префикс: {PREFIX}")

@bot.command(name="pet", aliases=["гладь", "погладь", "гладить"])
async def cmd_pet(ctx):
    happiness = state.pet()
    phrase = random.choice(PET_PHRASES)
    await ctx.send(f"{phrase}\n\n*уровень счастья: {happiness}%*")

@bot.command(name="purr", aliases=["мур", "мурлычь", "урчи"])
async def cmd_purr(ctx):
    phrase = random.choice(PURR_PHRASES)
    await ctx.send(phrase)

@bot.command(name="rest", aliases=["отдых", "спать", "лежать", "doze"])
async def cmd_rest(ctx):
    energy = state.rest()
    phrase = random.choice(REST_PHRASES)
    await ctx.send(f"{phrase}\n\n*энергия: {energy}%*")

@bot.command(name="nuzzle", aliases=["ткнуться", "тычок", "нос"])
async def cmd_nuzzle(ctx):
    phrase = random.choice(NUZZLE_PHRASES)
    await ctx.send(phrase)

@bot.command(name="wing", aliases=["крыло", "под крыло", "укрыть"])
async def cmd_wing(ctx):
    phrase = random.choice(WING_PHRASES)
    await ctx.send(phrase)

@bot.command(name="status", aliases=["статус", "состояние", "какдела"])
async def cmd_status(ctx):
    await ctx.send(
        f"**Состояние дракона**\n"
        f"• Настроение: {state.mood}\n"
        f"• Счастье: {state.happiness}%\n"
        f"• Энергия: {state.energy}%\n\n"
        f"*добрый дракон с седлом всегда рядом~*"
    )

@bot.command(name="help", aliases=["помощь", "команды"])
async def cmd_help(ctx):
    text = (
        "**Команды Dragon Pet**\n\n"
        f"`{PREFIX}pet` / `{PREFIX}гладь` — погладить дракона\n"
        f"`{PREFIX}purr` / `{PREFIX}мур` — попросить помурлыкать\n"
        f"`{PREFIX}rest` / `{PREFIX}отдых` — уложить отдыхать\n"
        f"`{PREFIX}nuzzle` / `{PREFIX}ткнуться` — ткнуться мордкой\n"
        f"`{PREFIX}wing` / `{PREFIX}крыло` — укрыть крылом\n"
        f"`{PREFIX}status` / `{PREFIX}статус` — узнать состояние\n"
        f"`{PREFIX}help` — эта справка\n\n"
        "*Я просто добрый дракон с седлом. Буду рядом.*"
    )
    await ctx.send(text)

# Простая реакция на упоминание
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = (message.content or "").lower()

    if bot.user and bot.user.id in (message.mention_ids or []):
        replies = [
            "*поворачивает голову* да, всадник?",
            "*тихо урчит* я здесь~",
            "*слегка наклоняет голову* слушаю",
        ]
        await message.channel.send(random.choice(replies))

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)
