from .database import get_conn
from .leetcode_api import fetch_problem_from_api

# TODO: Maybe edit this function to get only slug, and call from API. This way, there's validation + less user work
def add_problem(problem_id: int, slug: str, title: str, difficulty: str, topics: list[str]):
    """
    Add a LeetCode problem to the problems database.
    
    Args:
        problem_id (int): ID of problem on LeetCode. Used as primary key.
            Ex. 1
        slug (str): Title slug of problem.
            Ex. "two-sum"
        title (str): Title of problem.
            Ex. "Two Sum"
        difficulty (str): Difficulty level ("Easy", "Medium", "Hard").
            Ex. "Easy"
        topics (list[str]): List of problem's topics as strings.
            Ex. ["Junior", "Array", "Hash Table"]
    """
    conn = get_conn()
    cur = conn.cursor()

    # Convert topics list to comma-separated string for storage
    topics_str = ",".join(topics)
    
    # Inserting problem into problem database using problem_id as id
    cur.execute(
        "INSERT INTO problems(id,slug,title,difficulty,topics) VALUES(?,?,?,?,?)",
        (problem_id, slug, title, difficulty, topics_str)
    )

    conn.commit()
    conn.close()


def get_problem_by_slug(slug: str):
    """
    Retrieve a problem from the local database by its title slug on LeetCode.
    
    Args:
        slug (str): Title slug of problem.
    
    Returns:
        tuple: (problem_id, title, difficulty, topics) if found.
            int: Numeric ID of problem on LeetCode.
            str: Title of problem.
            str: Difficulty level.
        None: If the problem does not exist in the local database.
    """

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title, difficulty, topics FROM problems WHERE slug = ?",
        (slug,)
    )
    
    row = cur.fetchone()
    conn.close()
    
    return row


def log_attempt(slug: str, date: str, time_taken: int, confidence: int, success: int):
    """
    Log a LeetCode attempt.

    Flow:
    1. Ensure problem exists in local database (attempt fetch + cache if missing)
    2. Insert attempt entry referencing slug
    3. Return result dictionary
    
    Args:
        slug (str): Title slug of problem.
        date (str): Date of the attempt in ISO format ("YYYY-MM-DD").
        time_taken (int): Time spent on the attempt (in minutes).
        confidence (int): User-rated confidence level (1-5).
        success (int): Whether attempt was successful (0|1).
    
    Returns:
        dict: Success response with attempt_id and slug if logged successfully.
              Ex. {"success": True, "attempt_id": 42}
        dict: Error response if problem not found or API call failed.
              Example: {"success": False, "error": "Problem not found in database or LeetCode"}
    """
    # Validity checks
    if not slug or not isinstance(slug, str):
        return {"success": False, "error": "Invalid slug. Input a string."}
    if not (1 <= confidence <= 5):
        return {"success": False, "error": "Confidence must be between 1 and 5, inclusive."}
    if time_taken < 0:
        return {"success": False, "error": "Time taken cannot be negative."}
    if success not in ["0", "1"]:
        return {"success": False, "error": "Success must either be 0 (Fail) or 1 (Pass)."}
        
    # Attempting to get problem from local database
    problem_row = get_problem_by_slug(slug)
    
    if problem_row is None:
        # Problem not in local database, attempt to fetch from API
        problem_data = fetch_problem_from_api(slug)
        
        if problem_data is None:
            # API failed or problem does not exist on LeetCode
            return {
                "success": False,
                "error": f'Problem with slug "{slug}" not found in database or LeetCode.'
            }
        
        else:
            # Problem successfully found. Cache the problem to problems database
            problem_id = problem_data.get("id")
            title = problem_data.get("title")
            difficulty = problem_data.get("difficulty")
            topics = problem_data.get("topics")

            if None in (problem_id, title, difficulty, topics):
                return {
                    "success": False,
                    "error": "Incomplete data returned from API when adding problem to database."
                }
            
            # Insert the new problem into the database
            add_problem(problem_id, slug, title, difficulty, topics)

    # Found / successfully fetched and added problem. Inserting attempt record
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO attempts(slug, date, time_taken, confidence, success)
            VALUES (?, ?, ?, ?, ?)
            """,
            (slug, date, time_taken, confidence, int(success))
        )

        attempt_id = cur.lastrowid
        conn.commit()

    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }

    finally:
        conn.close()

    return {
        "success": True,
        "attempt_id": attempt_id
    }


def get_attempts() -> list[tuple]:
    """
    Retrieve all logged attempts with their associated problem metadata.
    
    This joins the attempts table with the problems table to provide complete information about eachs attempt.

    Returns:
         List of tuples, where each tuple contained an attempt metadata. Each tuple has:
            str: Title slug of problem.
                Ex. "two-sum"
            str: Difficulty level.
                Ex. "Easy"
            list[str]: List of problem's topics as strings.
                Ex. ["Junior", "Array", "Hash Table"]
            str: Date of the attempt in ISO format: "YYYY-MM-DD".
                Ex. "2026-02-09"
            int: Time spent on the attempt (in minutes).
                Ex. 42
            int: User-rated confidence level (1-5).
                Ex. 5
            int: Whether attempt was successful (0|1).
                Ex. 1
    """

    conn = get_conn()
    cur = conn.cursor()
    
    # Getting data from both problems and attempts tables
    cur.execute(
        """
        SELECT p.slug, p.difficulty, p.topics, a.date, a.time_taken, a.confidence, a.success
        FROM attempts a
        JOIN problems p ON a.slug = p.slug
        """
    )
    
    attempts = cur.fetchall()
    conn.close()
    
    return attempts