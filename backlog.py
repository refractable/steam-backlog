import requests
import json
import argparse
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "games.json")


def ensure_cache():
    """Create cache directory if it doesn't exist"""
    try:

        if not os.path.exists(CACHE_DIR):

            os.mkdir(CACHE_DIR)

    except OSError as e:
        console = Console()
        console.print(f"Error creating cache directory: {e}", style="red")
        sys.exit(1)


def load_config():
    console = Console()

    if not os.path.exists("config.json"):

        console.print("Error: config.json not found", style="red")
        console.print("\nPlease create a config.json file with the following structure:", style="yellow")
        console.print('{\n  "API_KEY": "your_api_key",\n  "STEAM_ID": "your_steam_id"\n}', style="yellow")
        sys.exit(1)

    try:

        with open("config.json") as f:

            config = json.load(f)

    except json.JSONDecodeError:

        console.print("Error: config.json is missing required keys!", style="red")
        console.print('Required keys: "API_KEY" and "STEAM_ID"', style="yellow")
        sys.exit(1)

    return config


def fetch_games(api_key, steam_id):
    """Fetch the user's game library from Steam API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    )

    console = Console()

    try:

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'response' not in data or 'games' not in data['response']:

            console.print("Error: Unexpected response format from Steam API", style="red")
            sys.exit(0)

        return data['response']['games']

    except requests.exceptions.Timeout:

        console.print("Error: Steam API request timed out", style="red")
        console.print("Check your internet connection and try again", style="yellow")
        sys.exit(1)

    except requests.exceptions.ConnectionError:

        console.print("Error: Could not connect to Steam API", style="red")
        console.print("Check your internet connection and try again", style="yellow")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500

        if status_code == 401:

            console.print("Error: Invalid Steam API key", style="red")

        elif status_code == 403:

            console.print("Error: Steam API request forbidden. Check your Steam profile privacy settings", style="red")

        else:

            console.print(f"Error: Steam API request failed with status code {status_code}", style="red")

        sys.exit(1)

    except json.JSONDecodeError:

        console.print("Error: Invalid response from Steam API", style="red")
        sys.exit(1)


def save_cache(games):
    """Save the user's game library to a cache file with timestamp"""
    ensure_cache()

    cache_data = {
        'last_updated': datetime.now().isoformat(),
        'games': games
    }

    try:

        with open(CACHE_FILE, 'w') as f:

            json.dump(cache_data, f, indent=2)

    except OSError as e:

        console = Console()
        console.print(f"Error saving cache file: {e}", style="red")
        sys.exit(1)


def load_cache():
    """Load the user's game library from a cache file if it exists"""
    if not os.path.exists(CACHE_FILE):

        return None

    console = Console()

    try:

        with open(CACHE_FILE) as f:

            cache_data = json.load(f)

    except json.JSONDecodeError:

        console.print("Warning: Cache file is corrupted. Run --sync to rebuild", style="yellow")
        return None

    except OSError as e:

        console.print(f"Error reading cache file: {e}", style="red")
        return None

    return cache_data


def display_games(games, title="Library", last_updated=None):

    console = Console()

    table = Table(title=title)
    table.add_column("Game", justify="left", style="green", no_wrap=False)
    table.add_column("Playtime", justify="right", style="cyan")

    for game in games:

        hours = game["playtime_forever"] / 60
        table.add_row(game["name"], f"{hours:.2f} hours")

    console.print(table)
    console.print(f"\nTotal games: {len(games)}", style="dim")

    if last_updated:

        dt = datetime.fromisoformat(last_updated)
        console.print(f"Last synced: {dt.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")


def main():

    parser = argparse.ArgumentParser(description="Steam game backlog tracker")
    parser.add_argument('--notplayed', action='store_true', help='Display games that have not been played')
    parser.add_argument('--under', type=float, help="Display games that have less than X hours played")
    parser.add_argument('--sync', action='store_true', help="Sync the game library from Steam")
    parser.add_argument('--sortby', choices=['name', 'playtime', 'playtime-asc'],
                        help='Sort games by name or playtime')
    args = parser.parse_args()

    with open("config.json") as f:

        config = json.load(f)

    if args.sync:

        console = Console()
        console.print("Syncing game library from Steam...", style="dim")
        games = fetch_games(config["API_KEY"], config["STEAM_ID"])

        save_cache(games)

        console.print("Games synced successfully!", style="green")
        last_updated = datetime.now().isoformat()

    else:

        cache_data = load_cache()

        if cache_data is None:

            console = Console()
            console.print("No cache found. Use --sync to sync the game library from Steam.", style="red")
            return

        games = cache_data["games"]
        last_updated = cache_data["last_updated"]

    # filtering
    if args.notplayed:

        games = [g for g in games if g['playtime_forever'] == 0]

    elif args.under:

        games = [g for g in games if g['playtime_forever'] / 60 < args.under]

    # sorting
    if args.sortby == 'name':

        games = sorted(games, key=lambda g: g['name'].lower())

    elif args.sortby == 'playtime':

        games = sorted(games, key=lambda g: g['playtime_forever'], reverse=True)

    elif args.sortby == 'playtime-asc':

        games = sorted(games, key=lambda g: g['playtime_forever'])


    # title labeling
    if args.notplayed:

        title = "Not played games"

    elif args.under:

        title = f"Games under {args.under} hours"

    else:

        title = "Library"
 
    display_games(games, title, last_updated=last_updated)


if __name__ == "__main__":
    main()
