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
TAGS_FILE = os.path.join(CACHE_DIR, "tags.json")


def ensure_cache():
    """Create cache directory if it doesn't exist"""
    try:

        if not os.path.exists(CACHE_DIR):

            os.mkdir(CACHE_DIR)

    except OSError as e:
        console = Console()
        console.print(f"Error creating cache directory: {e}", style="red")
        sys.exit(1)

        
def validate_credentials(api_key, steam_id):
    """Test credentials with a request to API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json"
    )
    try:

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return 'response' in data

    except Exception:

        return False


def setup_config():
    """Setup for creating config"""
    console = Console()

    console.print("\n[bold cyan]Steam Backlog Tracker Setup[/bold cyan]\n")
    console.print("To use this tool, you'll need a Steam API key and your Steam ID.\n")

    console.print("[bold]Step 1: Steam API key[/bold]")
    console.print("Get your key at: https://steamcommunity.com/dev/apikey", style='dim')
    api_key = input("Enter your Steam API key: ").strip()

    if not api_key:

        console.print("Error: API key cannot be empty", style='red')
        sys.exit(1)

    console.print("\n[bold]Step 2: Steam ID[/bold]")
    console.print("Find your 64-bit Steam ID at: https://steamid.io", style='dim')
    steam_id = input("Enter your Steam ID: ").strip()

    if not steam_id:

        console.print("Error: Steam ID cannot be empty", style='red')
        sys.exit(1)

    console.print("\nValidating credentials..", style='dim')

    if validate_credentials(api_key, steam_id):

        console.print("Credentials are valid. Saving config..", style='green')

    else:

        console.print("Warning: Could not validate credentials", style='yellow')
        console.print("This could mean invalid API key, private profile, or network issues.", style='dim')
        confirm = input("Save anyway? (y/n): ").strip().lower()

        if confirm != 'y':

            console.print("Setup cancelled. Exiting..", style='red')
            sys.exit(1)

    config = {
        "API_KEY": api_key,
        "STEAM_ID": steam_id
    }

    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        console.print("\nConfig saved to config.json", style='green')
        console.print("Run 'python backlog.py --sync' to fetch your game library\n", style='dim')
    except OSError as e:
        console.print(f"Error saving config: {e}", style='red')
        sys.exit(1)

    return config


def load_config():

    console = Console()

    if not os.path.exists("config.json"):

        return setup_config()

    try:

        with open("config.json") as f:

            config = json.load(f)

    except json.JSONDecodeError:

        console.print("Error: config.json is corrupted or invalid", style='red')
        console.print("Delete config.json and run again to start fresh", style='yellow')
        sys.exit(1)

    if "API_KEY" not in config or "STEAM_ID" not in config:

        console.print("Error: config.json is missing required keys", style='red')
        console.print("Delete config.json and run again to start fresh", style='yellow')
        sys.exit(1)

    return config


def fetch_games(api_key, steam_id):
    """Fetch the user's game library from Steam API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    )

    console = Console()

    # check if API key is valid
    try:

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'response' not in data or 'games' not in data['response']:

            console.print("Error: Unexpected response format from Steam API", style="red")
            sys.exit(0)

        return data['response']['games']

    # checks if there is a network error
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


def load_tags():
    """Load tags from file"""
    if not os.path.exists(TAGS_FILE):

        return {}

    try:

        with open(TAGS_FILE) as f:

            return json.load(f)
    except (json.JSONDecodeError, OSError):

        return {}

def save_tags(tags):
    """Save tags to file"""
    ensure_cache()

    try:

        with open(TAGS_FILE, 'w') as f:

            json.dump(tags, f, indent=2)

    except OSError as e:

        console = Console()
        console.print(f"Error saving tags: {e}", style="red")

        
def find_game_by_name(games, search_term):
    """Find game by partial name match"""
    search_lower = search_term.lower()

    for game in games:

        if game['name'].lower() == search_lower:

            return game

    matches = [g for g in games if search_lower in g['name'].lower()]

    if len(matches) == 1:

        return matches[0]

    elif len(matches) > 1:

        return matches
    
    return None

def display_games(games, title="Library", last_updated=None):
    """Display the user's game library"""
    console = Console()
    tags = load_tags()


    table = Table(title=title)
    table.add_column("Game", justify="left", style="green", no_wrap=False)
    table.add_column("Playtime", justify="right", style="cyan")

    if tags:
        
        table.add_column("Tags", justify="left", style="yellow")

    # checks hours played and displays it
    for game in games:

        hours = game["playtime_forever"] / 60
        appid = str(game["appid"])
        game_tags = tags.get(appid, [])

        if tags:

            table.add_row(game["name"], f"{hours:.2f} hours", ", ".join(game_tags))
        else:
            table.add_row(game["name"], f"{hours:.2f} hours")

    console.print(table)
    console.print(f"\nTotal games: {len(games)}", style="dim")

    # self explanatory i think
    if last_updated:

        dt = datetime.fromisoformat(last_updated)
        console.print(f"Last synced: {dt.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")


def display_all_tags(games):
    """Display all tags and their game counts"""
    console = Console()
    tags = load_tags()

    if not tags:

        console.print("No tags found. Use --tag to add tags to games", style="yellow")
        return
    
    tag_games = {}
    games_by_id = {str(g['appid']): g['name'] for g in games}

    for appid, game_tags in tags.items():

        for tag in game_tags:

            if tag not in tag_games:

                tag_games[tag] = []

            game_name = games_by_id.get(appid, f"Unknown ({appid})")
            tag_games[tag].append(game_name)

    table = Table(title="Tags")
    table.add_column("Tag", style="yellow")
    table.add_column("Count", justify='right', style='cyan')
    table.add_column("Games", style='green')

    for tag in sorted(tag_games.keys()):

        game_list = tag_games[tag]
        preview = ", ".join(game_list[:3])

        if len(game_list) > 3:

            preview += f" (+{len(game_list) - 3} more)"

        table.add_row(tag, str(len(game_list)), preview)
    
    console.print(table)


def display_stats(games):
    """Display stats about the user's game library"""
    console = Console()

    # total games, total playtime, not played games
    total_games = len(games)
    total_minutes = sum(g['playtime_forever'] for g in games)
    total_hours = total_minutes / 60

    not_played = [g for g in games if g['playtime_forever'] == 0]
    not_played_count = len(not_played)
    not_played_percent = (not_played_count / total_games * 100) if total_games > 0 else 0

    played_games = [g for g in games if g['playtime_forever'] > 0]
    avg_hours = (sum(g['playtime_forever'] for g in played_games) / 60 / len(played_games)) if played_games else 0

    most_played = max(games, key=lambda g: g['playtime_forever']) if games else None
    least_played = min(played_games, key=lambda g: g['playtime_forever']) if played_games else None

    brackets = [
        ("Never played", lambda h: h == 0),
        ("Under 1 hour", lambda h: 0 < h < 1),
        ("1-10 hours", lambda h: 1 <= h < 10),
        ("10-50 hours", lambda h: 10 <= h < 50),
        ("50-100 hours", lambda h: 50 <= h < 100),
        ("100+ hours", lambda h: h >= 100),
    ]

    # initialize table
    table = Table(title="Library Statistics", show_header=False)
    table.add_column("Statistic", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Total Games", str(total_games))
    table.add_row("Total Playtime", f"{total_hours:.2f} hours")
    table.add_row("Not Played Games", f"{not_played_count} ({not_played_percent:.2f}%)")
    table.add_row("Played Games", str(len(played_games)))

    if played_games:

        table.add_row("Average Playtime", f"{avg_hours:.2f} hours")

    if most_played:

        most_played_hours = most_played['playtime_forever'] / 60
        table.add_row("Most Played", f"{most_played['name']} ({most_played_hours:.2f} hrs)")

    if least_played:

        least_played_hours = least_played['playtime_forever'] / 60
        table.add_row("Least Played", f"{least_played['name']} ({least_played_hours:.2f} hrs)")
 
    console.print(table)
    
    # playtime distribution table for additional insight
    console.print()
    console.print("[bold]Playtime Distribution[/bold]")
    console.print()

    bracket_data = []

    for label, condition in brackets:

        count = len([g for g in games if condition(g['playtime_forever'] / 60)])
        percent = (count / total_games * 100) if total_games else 0
        bracket_data.append((label, count, percent))

    max_height = 12
    max_percent = max(b[2] for b in bracket_data) if bracket_data else 1

    for row in range(max_height, 0, -1):

        line = "    "

        for label, count, percent in bracket_data:

            bar_height = int((percent / max_percent) * max_height) if max_percent > 0 else 0

            if row <= bar_height:

                line += " [yellow]██[/yellow]    "

            else:

                line += "       "

        console.print(line)

    console.print("  " + "───────" * len(bracket_data))

    pct_line = " "

    for label, count, percent in bracket_data:

        pct_line += f" [green]{percent:4.0f}%[/green] "

    console.print(pct_line)
    short_labels = [" 0 hr", " <1 hr", "1-10", "10-50", "50-100", "100+"]
    label_line = " "

    for short in short_labels:

        label_line += f" [cyan]{short:^5}[/cyan] "

    console.print(label_line)


def main():

    # initializing parser
    parser = argparse.ArgumentParser(description="Steam game backlog tracker")
    parser.add_argument('--notplayed', action='store_true', help='Display games that have not been played')
    parser.add_argument('--under', type=float, help="Display games that have less than X hours played")
    parser.add_argument('--over', type=float, help="Display games hat have more than X hours played")
    parser.add_argument('--between', nargs=2, type=float, metavar=('MIN', 'MAX'),
                        help="Display games that have between MIN and MAX hours played")
    parser.add_argument('--started', action='store_true', help="Display games started but barely played (0-2hrs)")
    parser.add_argument('--recent', action='store_true', help="Display recently played games in the last two weeks")
    parser.add_argument('--sync', action='store_true', help="Sync the game library from Steam")
    parser.add_argument('--sortby', choices=['name', 'playtime', 'playtime-asc', 'recent'],
                        help='Sort games by name or playtime')
    parser.add_argument('--stats', action='store_true', help='Display library statistics')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard to configure credentials')
    parser.add_argument('--search', type=str, help='Search for a game by name')
    parser.add_argument('--tag', nargs=2, metavar=('GAME', 'TAG'), help='Add a tag to a game')
    parser.add_argument('--untag', nargs=2, metavar=('GAME', 'TAG'), help='Remove a tag from a game')
    parser.add_argument('--tags', action='store_true', help='Display all tags')
    parser.add_argument('--filter-tag', type=str, metavar='TAG', help='Filter games by tag')

    args = parser.parse_args()

    config = load_config()

    # first time setup / reconfigure setup
    if args.setup:

        if os.path.exists("config.json"):

            console = Console()
            confirm = input("config.json already exists. Overwrite? (y/n): ").strip().lower()

            if confirm != 'y':

                console.print("Setup cancelled", style='yellow')

                return

        setup_config()

        return

    # tag management
    if args.tag or args.untag or args.tags:
        
        cache_data = load_cache()

        if cache_data is None:
           
            console = Console()
            console.print("No cache found. Use --sync first", style='red')
            return

        games = cache_data["games"]
        
        if args.tags:

            display_all_tags(games)
            return
        
        if args.tag:

            game_name, tag_name = args.tag
            result = find_game_by_name(games, game_name)
            console = Console()

            if result is None:

                console.print(f"No game found matching '{game_name}'", style="red")
                return

            elif isinstance(result, list):

                console.print(f"Multiple games match '{game_name}':", style='yellow')

                for g in result[:10]:
                    console.print(f" - {g['name']}", style='dim')
                return

            tags = load_tags()
            appid = str(result['appid'])

            if appid not in tags:
                tags[appid] = []
            if tag_name not in tags[appid]:

                tags[appid].append(tag_name)
                save_tags(tags)
                console.print(f"Added tag '{tag_name}' to {result['name']}", style='green')
            else:

                console.print(f"{result['name']} already has tag '{tag_name}'", style="yellow")

            return

        if args.untag:
 
            game_name, tag_name = args.untag
            result = find_game_by_name(games, game_name)
            console = Console()

            if result is None:

                console.print(f"No game found matching '{game_name}'", style="red")
                return

            elif isinstance(result, list):

                console.print(f"Multiple games match '{game_name}':", style="yellow")

                for g in result[:10]:

                    console.print(f" - {g['name']}", style="dim")

                return

            tags = load_tags()
            appid = str(result['appid'])

            if appid in tags and tag_name in tags[appid]:

                tags[appid].remove(tag_name)

                if not tags[appid]:

                    del tags[appid]

                save_tags(tags)

                console.print(f"Removed tag '{tag_name}' from {result['name']}", style="green")

            else:

                console.print(f"{result['name']} doesn't have tag '{tag_name}'", style="yellow")

            return

    # syncing, checks if user has cache already or not
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


    # statistics
    if args.stats:
        display_stats(games)
        return

    
    # filtering
    if args.search:

        search_term = args.search.lower()
        games = [g for g in games if search_term in g['name'].lower()]
    
    if args.filter_tag:

        tags = load_tags()
        games = [g for g in games if args.filter_tag in tags.get(str(g['appid']), [])]

    if args.notplayed:

        games = [g for g in games if g['playtime_forever'] == 0]

    elif args.started:

        games = [g for g in games if g['playtime_forever'] / 60 <= 2]

    elif args.recent:

        games = [g for g in games if g.get('playtime_2weeks', 0) > 0]

    elif args.under:

        games = [g for g in games if g['playtime_forever'] / 60 < args.under]

    elif args.over:

        games = [g for g in games if g['playtime_forever'] / 60 > args.over]

    elif args.between:

        min_hrs, max_hrs = args.between
        games = [g for g in games if min_hrs <= g['playtime_forever'] / 60 <= max_hrs]


    # sorting

    if args.sortby == 'name':

        games = sorted(games, key=lambda g: g['name'].lower())

    elif args.sortby == 'playtime':

        games = sorted(games, key=lambda g: g['playtime_forever'], reverse=True)

    elif args.sortby == 'playtime-asc':

        games = sorted(games, key=lambda g: g['playtime_forever'])
    
    elif args.sortby == 'recent':

        games = sorted(games, key=lambda g: g.get('rtime_last_played', 0), reverse=True)

    # title labeling

    if args.search:

        title = f"Search results for {args.search}"

    if args.notplayed:

        title = "Not played games"
    elif args.started:

        title = "Started but barely played games (0-2hrs)"

    elif args.recent:
        
        title = f"Recently played (last 2 weeks)"

    elif args.under:

        title = f"Games under {args.under} hours"

    elif args.over:
        title = f"Games over {args.over} hours"

    elif args.between:

        title = f"Games between {args.between[0]}-{args.between[1]} hours"

    else:

        title = "Library"
 
    display_games(games, title, last_updated=last_updated)


if __name__ == "__main__":
    main()
