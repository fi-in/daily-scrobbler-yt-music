
import os
import time
import pylast
import ytmusicapi


API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")

username = os.getenv("LASTFM_USERNAME")
password = os.getenv("LASTFM_PASSWORD")
password_hash = pylast.md5(password) if password else None


def to_scrobble(entry: dict) -> dict:
    artist_list = entry.get("artists") or []

    artists = ", ".join(
        artist["name"]
        for artist in artist_list
        if artist.get("id") and artist.get("name")
    )

    if not artists:
        artists = "Unknown Artist"

    primary_artist = (
        artist_list[0].get("name") or artists
        if artist_list
        else artists
    )

    album = (entry.get("album") or {}).get("name", "")
    duration_seconds = entry.get("duration_seconds") or 180

    return {
        "artist": artists,
        "title": entry.get("title") or "Unknown Title",
        "timestamp": int(time.time()),
        "album": album,
        "duration": duration_seconds,
        "album_artist": primary_artist,
    }


def scrobble_tracks(network: pylast.LastFMNetwork, tracks: list):
    if not tracks:
        print("No tracks to scrobble.")
        return

    try:
        network.scrobble_many(tracks)
    except pylast.WSError as e:
        print(f"Error scrobbling tracks: {e}")
        raise

    print(f"Scrobbled {len(tracks)} tracks to Last.fm")


def main():
    browser_json_path = "browser.json"
    browser_json_raw = os.getenv("BROWSER_JSON")

    if not os.path.exists(browser_json_path):
        with open(browser_json_path, "w", encoding="utf-8") as f:
            f.write(browser_json_raw or "{}")

    ytmusic = ytmusicapi.YTMusic(browser_json_path)

    lastfm = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=username,
        password_hash=password_hash,
    )

    history = ytmusic.get_history()

    history = [
        entry
        for entry in history
        if entry.get("played") == "Yesterday"
    ]

    scrobbles = [to_scrobble(entry) for entry in history]

    print(f"{len(scrobbles)} tracks to scrobble")

    scrobble_tracks(lastfm, scrobbles)


if __name__ == "__main__":
    main()
