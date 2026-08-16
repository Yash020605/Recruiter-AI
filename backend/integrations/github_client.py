import json
from typing import Dict, Any, Optional
import httpx
from backend.utils.logger import get_logger

logger = get_logger(__name__)

GITHUB_API_URL = "https://api.github.com"

async def fetch_github_user_profile(username: str) -> Dict[str, Any]:
    """
    Fetches public profile and repository info for a given GitHub username.
    Extracts: username, bio, followers, public repos count, top languages, total stars.
    """
    clean_username = username.strip().replace("@", "")
    headers = {
        "User-Agent": "Recruiter-AI-Platform",
        "Accept": "application/vnd.github.v3+json"
    }

    user_url = f"{GITHUB_API_URL}/users/{clean_username}"
    repos_url = f"{GITHUB_API_URL}/users/{clean_username}/repos?per_page=100&sort=updated"

    profile_data = {
        "platform": "GitHub",
        "username": clean_username,
        "profile_url": f"https://github.com/{clean_username}",
        "bio": None,
        "location": None,
        "followers": 0,
        "repositories_count": 0,
        "top_languages": None,
        "total_stars": 0,
        "raw_data": None
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            user_resp = await client.get(user_url, headers=headers)
            if user_resp.status_code == 200:
                u_json = user_resp.json()
                profile_data["bio"] = u_json.get("bio")
                profile_data["location"] = u_json.get("location")
                profile_data["followers"] = u_json.get("followers", 0)
                profile_data["repositories_count"] = u_json.get("public_repos", 0)
            else:
                logger.warning(f"GitHub user API returned status {user_resp.status_code} for username {clean_username}")

            repos_resp = await client.get(repos_url, headers=headers)
            if repos_resp.status_code == 200:
                r_json = repos_resp.json()
                total_stars = 0
                languages_count: Dict[str, int] = {}
                for repo in r_json:
                    if not repo.get("fork"):
                        total_stars += repo.get("stargazers_count", 0)
                        lang = repo.get("language")
                        if lang:
                            languages_count[lang] = languages_count.get(lang, 0) + 1

                sorted_langs = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)
                top_langs = [l[0] for l in sorted_langs[:5]]
                profile_data["total_stars"] = total_stars
                profile_data["top_languages"] = ", ".join(top_langs) if top_langs else None
                profile_data["raw_data"] = json.dumps({"languages": languages_count, "repos_count": len(r_json)})

    except Exception as e:
        logger.error(f"Error fetching GitHub profile for {clean_username}: {e}")
        # Fallback profile data gracefully
        profile_data["bio"] = profile_data["bio"] or f"GitHub developer @{clean_username}"

    return profile_data
