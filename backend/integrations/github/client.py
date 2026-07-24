import httpx

async def analyze_github_profile(username: str) -> float:
    """
    Fetches GitHub public profile and calculates a simple mock technical score
    based on public repositories and followers.
    """
    api_url = f"https://api.github.com/users/{username}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        if response.status_code == 404:
            raise ValueError(f"GitHub user {username} not found")
        response.raise_for_status()
        
        data = response.json()
        public_repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        
        # Calculate a simple score out of 100 based on basic metrics
        # Base score of 60, add points for repos and followers, cap at 100
        score = min(60.0 + (public_repos * 0.5) + (followers * 0.2), 100.0)
        return round(score, 1)
