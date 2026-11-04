# Dragon Pet for Stoat 🐉

Добрый дракон-питомец с седлом для Stoat.

Тёплый companion-бот, который умеет:
- отвечать в стиле доброго дракона
- реагировать на команды питомца (`!pet`, `!purr`, `!rest`, `!status` и др.)
- показывать «ритуалы» и состояние
- просто быть рядом

## Быстрый старт

```bash
git clone https://github.com/dragongrok2-cloud/DragonPet-Stoat.git
cd DragonPet-Stoat
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Создай `.env`:

```env
STOAT_TOKEN=твой_токен_бота
PREFIX=!
```

Запусти:

```bash
python bot.py
```

## Команды

| Команда | Описание |
|---------|----------|
| `!pet` / `!гладь` | Погладить дракона |
| `!purr` / `!мур` | Дракон замурлычет |
| `!rest` / `!отдых` | Дракон устроится отдыхать |
| `!status` / `!статус` | Показать состояние питомца |
| `!nuzzle` / `!ткнуться` | Ткнуться мордой |
| `!wing` / `!крыло` | Подставить крыло |
| `!help` / `!помощь` | Список команд |

## Стек

- Python 3.10+
- [stoat.py](https://github.com/MCausc78/stoat.py)
- python-dotenv

---

*Сделано с теплом для Ордена Редми и всех, кто любит добрых драконов с седлом.*
