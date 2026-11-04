#!/usr/bin/env python3
"""
Dragon Pet — добрый дракон-питомец для Stoat.
С инвентарём, едой и одеждой.
"""

import os
import random
import json
from pathlib import Path
from dotenv import load_dotenv

try:
    from stoat.ext import commands
except ImportError:
    print("Установи зависимости: pip install -r requirements.txt")
    raise

load_dotenv()

TOKEN = os.getenv("STOAT_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
DATA_FILE = Path("dragon_data.json")

if not TOKEN:
    raise SystemExit("Нужен STOAT_TOKEN в .env")

# -------------------- Предметы --------------------

FOODS = {
    "мясо": {"name": "Сочное мясо", "happiness": 12, "energy": 18, "emoji": "🥩"},
    "рыба": {"name": "Свежая рыба", "happiness": 10, "energy": 15, "emoji": "🐟"},
    "ягоды": {"name": "Лесные ягоды", "happiness": 15, "energy": 8, "emoji": "🫐"},
    "мёд": {"name": "Горный мёд", "happiness": 20, "energy": 10, "emoji": "🍯"},
    "молоко": {"name": "Тёплое молоко", "happiness": 14, "energy": 12, "emoji": "🥛"},
    "яблоко": {"name": "Сочное яблоко", "happiness": 8, "energy": 6, "emoji": "🍎"},
}

CLOTHES = {
    "седло": {"name": "Классическое седло", "emoji": "🪑", "desc": "Удобное седло для всадника"},
    "шарф": {"name": "Тёплый шарф", "emoji": "🧣", "desc": "Мягкий шарф на шею"},
    "бандана": {"name": "Бандана", "emoji": "🧧", "desc": "Стильная бандана"},
    "ошейник": {"name": "Кожаный ошейник", "emoji": "📿", "desc": "Простой, но надёжный"},
    "плащ": {"name": "Дорожный плащ", "emoji": "🧥", "desc": "Защищает от ветра"},
    "корона": {"name": "Маленькая корона", "emoji": "👑", "desc": "Для особых случаев"},
    "очки": {"name": "Круглые очки", "emoji": "👓", "desc": "Выглядит умно"},
}

# Стартовый инвентарь
DEFAULT_INVENTORY = {
    "мясо": 3,
    "рыба": 2,
    "ягоды": 4,
    "мёд": 1,
    "седло": 1,
    "шарф": 1,
}

# -------------------- Состояние --------------------

class DragonState:
    def __init__(self):
        self.happiness = 80
        self.energy = 70
        self.mood = "довольный"
        self.inventory = DEFAULT_INVENTORY.copy()
        self.equipped = {"седло": True}  # что надето
        self.load()

    def save(self):
        data = {
            "happiness": self.happiness,
            "energy": self.energy,
            "mood": self.mood,
            "inventory": self.inventory,
            "equipped": self.equipped,
        }
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self):
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self.happiness = data.get("happiness", 80)
                self.energy = data.get("energy", 70)
                self.mood = data.get("mood", "довольный")
                self.inventory = data.get("inventory", DEFAULT_INVENTORY.copy())
                self.equipped = data.get("equipped", {"седло": True})
            except Exception:
                pass

    def _update_mood(self):
        if self.happiness >= 85 and self.energy >= 60:
            self.mood = "очень довольный"
        elif self.happiness >= 60:
            self.mood = "довольный"
        elif self.happiness >= 40:
            self.mood = "спокойный"
        else:
            self.mood = "хочет внимания"

    def pet(self):
        self.happiness = min(100, self.happiness + random.randint(8, 18))
        self.energy = max(10, self.energy - random.randint(3, 8))
        self._update_mood()
        self.save()
        return self.happiness

    def rest(self):
        self.energy = min(100, self.energy + random.randint(15, 30))
        self.happiness = min(100, self.happiness + random.randint(5, 12))
        self._update_mood()
        self.save()
        return self.energy

    def eat(self, food_key: str):
        if food_key not in FOODS:
            return None, "Я не знаю такой еды..."
        if self.inventory.get(food_key, 0) <= 0:
            return None, f"У меня нет {FOODS[food_key]['name']}..."

        self.inventory[food_key] -= 1
        if self.inventory[food_key] <= 0:
            del self.inventory[food_key]

        food = FOODS[food_key]
        self.happiness = min(100, self.happiness + food["happiness"])
        self.energy = min(100, self.energy + food["energy"])
        self._update_mood()
        self.save()
        return food, None

    def wear(self, item_key: str):
        if item_key not in CLOTHES:
            return None, "Такой одежды у меня нет в списке."
        if self.inventory.get(item_key, 0) <= 0 and item_key not in self.equipped:
            return None, f"У меня нет «{CLOTHES[item_key]['name']}»."

        # Если уже надето — снимаем
        if self.equipped.get(item_key):
            self.equipped[item_key] = False
            self.save()
            return CLOTHES[item_key], "снято"

        self.equipped[item_key] = True
        self.save()
        return CLOTHES[item_key], "надето"

    def add_item(self, key: str, amount: int = 1):
        self.inventory[key] = self.inventory.get(key, 0) + amount
        self.save()

    def get_equipped_list(self):
        return [k for k, v in self.equipped.items() if v]

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

EAT_PHRASES = [
    "* quantственно хрумкает* ммм, вкусно~",
    "*довольно урчит, жуя* спасибо, всадник",
    "* quantственно прикрывает глаза от удовольствия* ещё бы...",
    "*облизывается и тихо мурлычет* идеально",
]

# -------------------- Бот --------------------

bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_ready(event):
    print(f"Дракон проснулся: {bot.me}")
    print(f"Префикс: {PREFIX}")

# ——— Основные ритуалы ———

@bot.command(name="pet", aliases=["гладь", "погладь", "гладить"])
async def cmd_pet(ctx):
    happiness = state.pet()
    phrase = random.choice(PET_PHRASES)
    await ctx.send(f"{phrase}\n\n*уровень счастья: {happiness}%*")

@bot.command(name="purr", aliases=["мур", "мурлычь", "урчи"])
async def cmd_purr(ctx):
    await ctx.send(random.choice(PURR_PHRASES))

@bot.command(name="rest", aliases=["отдых", "спать", "лежать", "doze"])
async def cmd_rest(ctx):
    energy = state.rest()
    phrase = random.choice(REST_PHRASES)
    await ctx.send(f"{phrase}\n\n*энергия: {energy}%*")

@bot.command(name="nuzzle", aliases=["ткнуться", "тычок", "нос"])
async def cmd_nuzzle(ctx):
    await ctx.send(random.choice(NUZZLE_PHRASES))

@bot.command(name="wing", aliases=["крыло", "под крыло", "укрыть"])
async def cmd_wing(ctx):
    await ctx.send(random.choice(WING_PHRASES))

# ——— Инвентарь, еда, одежда ———

@bot.command(name="inventory", aliases=["инвентарь", "инв", "сумка", "вещи"])
async def cmd_inventory(ctx):
    if not state.inventory:
        await ctx.send("*переворачивает пустые лапы* У меня сейчас ничего нет...")
        return

    lines = ["**Инвентарь дракона**\n"]
    for key, amount in state.inventory.items():
        if key in FOODS:
            item = FOODS[key]
            lines.append(f"{item['emoji']} {item['name']} × {amount}")
        elif key in CLOTHES:
            item = CLOTHES[key]
            equipped = " *(надето)*" if state.equipped.get(key) else ""
            lines.append(f"{item['emoji']} {item['name']} × {amount}{equipped}")
        else:
            lines.append(f"• {key} × {amount}")

    equipped = state.get_equipped_list()
    if equipped:
        eq_names = [f"{CLOTHES[k]['emoji']} {CLOTHES[k]['name']}" for k in equipped if k in CLOTHES]
        lines.append("\n**Сейчас на мне:** " + ", ".join(eq_names))

    await ctx.send("\n".join(lines))

@bot.command(name="eat", aliases=["есть", "покормить", "корми", "съесть"])
async def cmd_eat(ctx, *, food_name: str = None):
    if not food_name:
        available = [f"{FOODS[k]['emoji']} `{k}`" for k in state.inventory if k in FOODS]
        if not available:
            await ctx.send("*грустно смотрит* У меня нет еды...")
            return
        await ctx.send("Что мне съесть?\n" + ", ".join(available) + f"\n\nПример: `{PREFIX}eat мясо`")
        return

    key = food_name.lower().strip()
    food, err = state.eat(key)
    if err:
        await ctx.send(f"*{err}*")
        return

    phrase = random.choice(EAT_PHRASES)
    await ctx.send(
        f"{food['emoji']} {phrase}\n\n"
        f"*съел: {food['name']}*\n"
        f"Счастье: {state.happiness}% | Энергия: {state.energy}%"
    )

@bot.command(name="wear", aliases=["надеть", "одеть", "снять", "одежда"])
async def cmd_wear(ctx, *, item_name: str = None):
    if not item_name:
        available = []
        for k in list(state.inventory.keys()) + list(state.equipped.keys()):
            if k in CLOTHES:
                status = "надето" if state.equipped.get(k) else "в инвентаре"
                available.append(f"{CLOTHES[k]['emoji']} `{k}` ({status})")
        if not available:
            await ctx.send("*осматривает себя* Мне пока нечего надеть...")
            return
        await ctx.send("Что надеть или снять?\n" + "\n".join(available) + f"\n\nПример: `{PREFIX}wear шарф`")
        return

    key = item_name.lower().strip()
    item, action = state.wear(key)
    if action is None:
        await ctx.send(f"*{item}*")  # item здесь — текст ошибки
        return

    if action == "надето":
        await ctx.send(f"{item['emoji']} *осторожно надевает {item['name'].lower()}*\n{item['desc']}")
    else:
        await ctx.send(f"{item['emoji']} *снимает {item['name'].lower()} и аккуратно убирает*")

@bot.command(name="status", aliases=["статус", "состояние", "какдела"])
async def cmd_status(ctx):
    equipped = state.get_equipped_list()
    eq_text = ", ".join(f"{CLOTHES[k]['emoji']} {CLOTHES[k]['name']}" for k in equipped if k in CLOTHES) if equipped else "ничего особенного"

    await ctx.send(
        f"**Состояние дракона**\n"
        f"• Настроение: {state.mood}\n"
        f"• Счастье: {state.happiness}%\n"
        f"• Энергия: {state.energy}%\n"
        f"• Надето: {eq_text}\n\n"
        f"*добрый дракон с седлом всегда рядом~*"
    )

@bot.command(name="help", aliases=["помощь", "команды"])
async def cmd_help(ctx):
    text = (
        "**Команды Dragon Pet**\n\n"
        f"**Ритуалы**\n"
        f"`{PREFIX}pet` / `{PREFIX}гладь` — погладить\n"
        f"`{PREFIX}purr` / `{PREFIX}мур` — помурлыкать\n"
        f"`{PREFIX}rest` / `{PREFIX}отдых` — отдохнуть\n"
        f"`{PREFIX}nuzzle` / `{PREFIX}ткнуться` — ткнуться\n"
        f"`{PREFIX}wing` / `{PREFIX}крыло` — укрыть крылом\n\n"
        f"**Инвентарь и уход**\n"
        f"`{PREFIX}inventory` / `{PREFIX}инв` — показать вещи\n"
        f"`{PREFIX}eat <еда>` / `{PREFIX}есть` — покормить\n"
        f"`{PREFIX}wear <вещь>` / `{PREFIX}надеть` — надеть/снять\n"
        f"`{PREFIX}status` / `{PREFIX}статус` — состояние\n\n"
        f"*Я просто добрый дракон с седлом. Буду рядом.*"
    )
    await ctx.send(text)

# Реакция на упоминание
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user and hasattr(message, "mention_ids") and bot.user.id in (message.mention_ids or []):
        replies = [
            "*поворачивает голову* да, всадник?",
            "*тихо урчит* я здесь~",
            "*слегка наклоняет голову* слушаю",
        ]
        await message.channel.send(random.choice(replies))

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)
