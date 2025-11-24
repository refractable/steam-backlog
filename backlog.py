import requests
import json

with open("config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
STEAM_ID = config["STEAM_ID"]

url = (
    f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    f"?key={API_KEY}&steamid={STEAM_ID}&format=json&include_appinfo=1"
)


response = requests.get(url)
data = response.json()

games = data["response"]["games"]

for game in games:
    print(f"{game['name']} ({game['playtime_forever']}) minutes played")
