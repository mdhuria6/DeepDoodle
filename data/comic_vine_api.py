import requests
import os
import requests
import json
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()


# Replace with your actual Comic Vine API key
COMIC_VINE_API_KEY = os.getenv("COMIC_VINE_API_KEY")

if not COMIC_VINE_API_KEY:
    raise ValueError(
        "Missing COMIC_VINE_API_KEY in .env file. Please ensure it's set in your .env file.")

BASE_URL = "https://comicvine.gamespot.com/api"
HEADERS = {"User-Agent": "ComicMetadataFetcher/1.0"}
GENRE = "sci-fi"  # You can change this as needed


def comicvine_get(endpoint, params={}):
    """Generic GET request to Comic Vine API."""
    url = f"{BASE_URL}/{endpoint}/"
    params.update({"api_key": COMIC_VINE_API_KEY, "format": "json"})
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def search_volumes_by_query(query):
    """Search for volumes by query string."""
    return comicvine_get("search", {
        "query": query,
        "resources": "volume",
        "format": "json",
        "limit": 1
    })


def get_volume_issues(volume_id):
    """Get list of issues in a volume."""
    return comicvine_get(f"volume/4050-{volume_id}")


def get_issue_details(issue_id):
    """Get description and characters from an issue."""
    return comicvine_get(f"issue/4000-{issue_id}")


def get_character_description(char_url):
    """Fetch character description from Comic Vine character detail URL."""
    params = {
        "api_key": COMIC_VINE_API_KEY,
        "format": "json"
    }
    try:
        response = requests.get(char_url, headers=HEADERS, params=params)
        response.raise_for_status()
        char_data = response.json().get("results", {})
        print(f"char data is ", char_data)
        exit
        raw_html = char_data.get(
            "description", "") or char_data.get("deck", "")
        return BeautifulSoup(raw_html, "html.parser").get_text().strip() or "No description available."
    except Exception as e:
        print(f"⚠️ Failed to fetch character from {char_url}: {e}")
        return "No description available."


def build_output_from_issue(issue_data):
    result = issue_data.get("results")
    if not result:
        print("⚠️  No data returned for issue.")
        return {
            "genre_preset": GENRE,
            "character_descriptions": [],
            "summary": "No summary available."
        }

    # Summary
    raw_html = result.get("description", "")
    summary_text = BeautifulSoup(raw_html, "html.parser").get_text(
    ) if raw_html else "No summary available."

    # Characters (fetch descriptions)
    character_credits = result.get("character_credits", [])
    selected = character_credits[:2]  # Pick top 2 characters for brevity
    character_descriptions = []

    for char in selected:
        name = char.get("name")
        detail_url = char.get("api_detail_url")
        if name and detail_url:
            desc = get_character_description(detail_url)
            with open(f"char.json", "w") as f:
                json.dump(desc, f, indent=2)
            character_descriptions.append({
                "name": name,
                "description": desc
            })

    return {
        "genre_preset": GENRE,
        "character_descriptions": character_descriptions,
        "summary": summary_text.strip()
    }


def main():
    # Step 1: Search for a volume
    search_result = search_volumes_by_query(
        "Spider-Man")  # Modify keyword to fit genre
    if not search_result["results"]:
        print("No volumes found.")
        return
    with open("search_result.json", "w") as f:
        json.dump(search_result, f, indent=2)
    volume = search_result["results"][0]
    volume_id = volume["id"]
    volume_name = volume["name"]
    print(f"\n🔎 Found volume: {volume_name} (ID: {volume_id})")

    # Step 2: Get volume issues
    volume_data = get_volume_issues(volume_id)
    with open("volume_data.json", "w") as f:
        json.dump(volume_data, f, indent=2)
    issues = volume_data["results"].get("issues", [])
    if not issues:
        print("No issues found in volume.")
        return
    print(f"\n📘 Issues in Volume '{volume_name}':")
    # Step 3: Get first issue details
    last_issue_id = volume_data["results"]["last_issue"]["id"]
    issue_data = get_issue_details(last_issue_id)
    with open("issue_data.json", "w") as f:
        json.dump(issue_data, f, indent=2)
    # Step 4: Build output
    output = build_output_from_issue(issue_data)

    # Step 5: Save result
    with open("sci_fi_comic_summary.json", "w") as f:
        json.dump(output, f, indent=2)
    print("✅ Saved to sci_fi_comic_summary.json")


if __name__ == "__main__":
    main()
