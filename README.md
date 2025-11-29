# Backpile

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A simple command-line tool for tracking your Steam game library.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
|**Sync Library** | Fetch games directly from Steam API |
|**Smart Filtering** | Filter by playtime, status, tags, recent activity |
|**Tag System** | Organize games with custom tags |
|**Status Tracking** | Auto-detects playing/backlog/dropped with manual overrides |
|**Manual Entries** | Track non-Steam games alongside your library |
|**Statistics** | Playtime distribution charts and library insights |
|**Export** | Save to CSV or JSON |

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/refractable/backpile.git
cd steam-backlog
pip install requests rich
```

### Setup

```bash
python main.py
```

You'll need:
- **Steam API Key** → [Get one here](https://steamcommunity.com/dev/apikey)
- **Steam ID** → [Find yours here](https://steamid.io)

### First Run

```bash
python main.py --sync    # Fetch your library
python main.py           # View all games
python main.py --stats   # See statistics
```

---

## Usage

### Filtering Games

```bash
# By playtime
python main.py --notplayed           # Never played
python main.py --under 5             # Under 5 hours
python main.py --over 100            # Over 100 hours
python main.py --between 10 50       # 10-50 hours
python main.py --started             # Barely started (0-2 hrs)

# By activity
python main.py --recent              # Played last 2 weeks
python main.py --filterstatus backlog

# By name or tag
python main.py --search "dark souls"
python main.py --filter-tag rpg
```

### Sorting

```bash
python main.py --sortby name          # Alphabetical
python main.py --sortby playtime      # Most played first
python main.py --sortby playtime-asc  # Least played first
python main.py --sortby recent        # Recently played first
```

### Tags

```bash
python main.py --tag "Dark Souls" rpg              # Add tag
python main.py --untag "Dark Souls" rpg            # Remove tag
python main.py --tags                              # View all tags

# Bulk operations
python main.py --bulktag coop "Portal 2" "Left 4 Dead" Terraria
python main.py --bulkuntag coop "Portal 2" "Left 4 Dead"
```

### Status Tracking

**Auto-detected:**
| Status | Condition |
|--------|-----------|
| `playing` | Played in last 2 weeks |
| `backlog` | Never played |
| `inactive` | Played but not recently |
| `dropped` | No activity in 6+ months |

**Manual overrides:**
```bash
python main.py --setstatus "Dark Souls" completed
python main.py --bulkstatus completed "Dark Souls" "Elden Ring" "Sekiro"
python main.py --clearstatus "Dark Souls"    # Revert to auto-detect
```

### Manual Games

Track non-Steam games or games from other platforms:

```bash
# Add games
python main.py --addgame "God of War" --platform "PS5"
python main.py --addgame 105600 --platform "PC"    # Steam App ID lookup

# Manage
python main.py --logtime "God of War" 5            # Log 5 hours
python main.py --removegame "God of War"

# Filter
python main.py --source steam     # Steam only
python main.py --source manual    # Manual only
```

### Export

```bash
python main.py --export csv                        # Export all
python main.py --over 50 --export json             # Export filtered
python main.py --filterstatus completed --export csv
```

---

## Examples

```bash
# Find RPGs I haven't finished
python main.py --filter-tag rpg --filterstatus inactive

# Short games to clear from backlog
python main.py --notplayed --sortby playtime-asc --limit 20

# What I've been playing lately
python main.py --recent --sortby playtime

# Export completed games
python main.py --filterstatus completed --export csv
```

---

## Project Structure

```
backpile/
├── main.py              # Entry point
├── backlog/
│   ├── __init__.py      # Constants
│   ├── api.py           # Steam API
│   ├── cache.py         # Data storage
│   ├── cli.py           # CLI interface
│   ├── display.py       # Output formatting
│   ├── export.py        # CSV/JSON export
│   └── utils.py         # Helpers
├── cache/               # Local data (auto-generated)
│   ├── games.json
│   ├── tags.json
│   ├── status.json
│   └── manual_games.json
└── ...
```

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) © 2025
