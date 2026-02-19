import requests

from constants import LEETCODE_GRAPHQL_URL

def fetch_problem_from_api(slug: str) -> dict[str, int | str | list[str]] | None:
    """
    Fetch LeetCode problem metadata from GraphQL endpoint user problem's slug.
    
    Args:
        slug (text): The problem's title slug.
            Ex. "two-sum"
    
    Returns:
        dict: Dictionary {"id": int, "title": str, "difficulty": str, "topics": list[str]} if the problem is found.
              Ex. {
                  "id": 1,
                  "title": "Two Sum",
                  "difficulty": "Easy",
                  "topics": ["Array", "Hash Table"]
              }
        None: If the problem does not exist or the API call fails in any way.
    """

    query = """
    query getQuestion($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        difficulty
        topicTags {
          name
        }
      }
    }
    """

    variables = {"titleSlug": slug}

    response = requests.post(
        LEETCODE_GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com"
        },
        timeout=10
    )

    # Response didn't work properly
    if response.status_code != 200:
        return None
    
    data = response.json()

    # Error in data fetching
    if "errors" in data:
        return None
    
    q = data["data"]["question"]

    # If null LeetCode problem
    if q is None:
        return None
    
    return {
        "id": int(q["questionFrontendId"]),
        "title": q["title"],
        "difficulty": q["difficulty"],
        "topics": [t["name"] for t in q["topicTags"]]
    }
