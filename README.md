# Steam Backlog Tracker

A command-line tool to track and manage your Steam game backlog.

## Features

- Sync your Steam library with local caching
- Filter games by playtime or unplayed status
- Sort by name or playtime
- View library statistics

## Setup

1. **Install dependencies:**
```bash
   pip install requests rich
```

2. **Get a Steam API key:**
   - Visit https://steamcommunity.com/dev/apikey
   - Sign in and register (domain can be anything like "localhost")

3. **Find your Steam ID:**
   - Use https://steamid.io/ to get your 64-bit Steam ID

4. **Create config.json:**
```json
   {
     "API_KEY": "your_steam_api_key_here",
     "STEAM_ID": "your_steam_id_here"
   }
```

## Usage

**First sync:**
```bash
python backlog.py --sync
```

**View all games:**
```bash
python backlog.py
```

**Filter unplayed games:**
```bash
python backlog.py --notplayed
```

**Filter games under X hours:**
```bash
python backlog.py --under 5
```

**Sort options:**
```bash
python backlog.py --sortby name
python backlog.py --sortby playtime
python backlog.py --sortby playtime-asc
```

**View statistics:**
```bash
python backlog.py --stats
```

Note: The --stats option is not currently supported.

Note2: These filters are able to be used together, e.g. `--notplayed --under 5`.

## Requirements

- Python 3.6+
- requests
- rich

## Notes
This is a work in progress project as this is a personal project. If you have any suggestions or feedback, please open an issue on GitHub.
I have many more features planned, but I am currently focused on getting the core functionality working.
