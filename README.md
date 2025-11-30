<p align="center">
  <h1 align="center">Backpile</h1>
  <p align="center">
    A CLI tool to manage your game backlog.
    <br />
    Syncs with Steam, tracks playtime, and helps you figure out what to play next.
  </p>
</p>

<p align="center">
  <a href="#install">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#features">Features</a> •
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python3-blue?style=flat-square" alt="Made with Python3">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License MIT"></a>
  <a href="https://github.com/refractable/backpile/releases"><img src="https://img.shields.io/github/v/release/refractable/backpile?style=flat-square&color=orange" alt="Latest Release"></a>
</p>

---

## Install

```bash
git clone https://github.com/refractable/backpile.git
cd backpile
pip install requests rich
```

## Setup

```bash
python main.py
```

You'll need a [Steam API Key](https://steamcommunity.com/dev/apikey) and your [Steam ID](https://steamid.io).

## Usage

```bash
python main.py --sync              # Fetch library from Steam
python main.py                     # View all games
python main.py --stats             # Library statistics
```

<details>
<summary>Filtering</summary>

```bash
python main.py --notplayed         # Never played
python main.py --under 5           # Under 5 hours
python main.py --over 100          # Over 100 hours
python main.py --between 10 50     # 10-50 hours
python main.py --recent            # Played last 2 weeks
python main.py --search "dark"     # Search by name
```
</details>

<details>
<summary>Tags</summary>

```bash
python main.py --tag "Elden Ring" souls    # Add tag
python main.py --untag "Elden Ring" souls  # Remove tag
python main.py --filter-tag souls          # Filter by tag
python main.py --tags                      # View all tags

# Bulk operations
python main.py --bulktag rpg "Dark Souls" "Elden Ring" "Sekiro"
```
</details>

<details>
<summary>Status</summary>

```bash
python main.py --setstatus "Hades" completed   # Mark complete
python main.py --filterstatus backlog          # Filter by status

# Bulk operations
python main.py --bulkstatus completed "Hades" "Celeste" "Hollow Knight"
```

Auto-detected: `playing` · `backlog` · `inactive` · `dropped`  
Manual: `completed` · `hold`
</details>

<details>
<summary>Manual Games</summary>

```bash
python main.py --addgame "God of War" --platform PS5
python main.py --addgame 105600 --platform PC    # Steam App ID lookup
python main.py --logtime "God of War" 5          # Log 5 hours
python main.py --removegame "God of War"
python main.py --source manual                   # Show only manual games
```
</details>

<details>
<summary>Export</summary>

```bash
python main.py --export csv
python main.py --export json
python main.py --filterstatus completed --export csv   # Export filtered
```
</details>

Run `python main.py --help` for all options.

## Features

- Sync Steam library via API
- Filter by playtime, status, tags, recent activity
- Custom tagging system with bulk operations
- Auto-detected and manual status tracking
- Track non-Steam games alongside your library
- Export to CSV/JSON

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) © 2025
