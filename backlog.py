import requests
import json
import argparse
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "games.json")


def ensure_cache():
    """Create cache directory if it doesn't exist"""
    if not os.path.exists(CACHE_DIR):

        os.makedirs(CACHE_DIR)


def fetch_games(api_key, steam_id):
    """Fetch the user's game library from Steam API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    )
    response = requests.get(url)

    return response.json()['response']['games']


def save_cache(games):
    """Save the user's game library to a cache file with timestamp"""
    ensure_cache()

    cache_data = {
        'last_updated': datetime.now().isoformat(),
        'games': games
    }

    with open(CACHE_FILE, 'w') as f:

        json.dump(cache_data, f, indent=2)


def load_cache():
    """Load the user's game library from a cache file if it exists"""
    if not os.path.exists(CACHE_FILE):

        return None

    with open(CACHE_FILE) as f:

        cache_data = json.load(f)

    return cache_data


def display_games(games, title="Library", last_updated=None):

    console = Console()

    table = Table(title=title)
    table.add_column("Game", justify="left", style="cyan", no_wrap=False)
    table.add_column("Playtime", justify="right", style="green")

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

    if args.notplayed:

        games = [g for g in games if g['playtime_forever'] == 0]
        display_games(games, "Games not played", last_updated=last_updated)

    elif args.under:

        games = [g for g in games if g['playtime_forever'] / 60 < args.under]
        display_games(games, f"Games under {args.under} hours", last_updated=last_updated)

    else:

        display_games(games, "Games", last_updated=last_updated)


if __name__ == "__main__":
    main()
