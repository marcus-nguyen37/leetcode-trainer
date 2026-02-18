from .database import get_conn
from .leetcode_api import fetch_problem_from_api

def add_problem(problem_id: int, title: str, difficulty: str, topics: list[str]):
    """
    Add a LeetCode problem to the problems database.
    
    Args:
        problem_id (int): ID of problem on LeetCode. Used as primary key.
            Ex. 1
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
        "INSERT INTO problems(id,title,difficulty,topics) VALUES(?,?,?,?)",
        (problem_id, title, difficulty, topics_str)
    )

    conn.commit()
    conn.close()


def get_problem_by_id(problem_id: int):
    """
    Retrieve a problem from the local database by its ID on LeetCode.
    
    Args:
        problem_id (int): ID of problem on LeetCode.
    
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
        "SELECT id, title, difficulty, topics FROM problems WHERE id = ?",
        (problem_id,)
    )
    
    row = cur.fetchone()
    conn.close()
    
    return row


def log_attempt(problem_id: int, date: str, time_taken: int, confidence: int, success: int):
    """
    Log a LeetCode attempt.

    Uses the flow:
    1. Check if the problem exists in the local database.
    2. If not, fetch from the API and add to the database.
    3. If the API fails and/or problem doesn't exist, return an error.
    4. If successful, insert the attempt record.
    
    Args:
        problem_id (int): ID of problem on LeetCode.
        date (str): Date of the attempt in ISO format ("YYYY-MM-DD").
        time_taken (int): Time spent on the attempt (in minutes).
        confidence (int): User-rated confidence level (1-5).
        success (int): Whether attempt was successful (0/1).
    
    Returns:
        dict: Success response with attempt_id if logged successfully.
              Ex. {"success": True, "attempt_id": 42}
        dict: Error response if problem not found or API call failed.
              Example: {"success": False, "error": "Problem not found in database or LeetCode"}
    """
    
    # Check if the problem exists in the local database
    problem_row = get_problem_by_id(problem_id)
    
    if problem_row is None:
        # Problem not in cached database, attempt to fetch from API
        problem_data = fetch_problem_from_api(problem_id)
        
        if problem_data is None:
            # API failed or problem does not exist on LeetCode
            return {
                "success": False,
                "error": f"Problem with ID {problem_id} not found in database or LeetCode."
            }
        
        else:
        
            # Problem successfully found. Cache the problem to the problems database
            # Extracting metadata from API response

            ################################ FIX THE KEYS FOR API DATA WHEN API IS FINISHED
            problem_id = problem_data.get("ID", "Unknown")
            title = problem_data.get("title", "Unknown")
            difficulty = problem_data.get("difficulty", "Unknown")
            topics = problem_data.get("topics", [])
            
            # Insert the new problem into the database
            add_problem(problem_id, title, difficulty, topics)

    
    # STEP 3: Insert the attempt record using the problem_id
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO attempts(problem_id, date, time_taken, confidence, success)
        VALUES (?, ?, ?, ?, ?)
        """,
        (problem_id, date, time_taken, confidence, success)
    )

    attempt_id = cur.lastrowid  # Get the ID of the newly inserted attempt
    conn.commit()
    conn.close()
    
    # Return success response with the attempt ID
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
            int: ID of problem on LeetCode.
                Ex. 1
            str: Title of problem.
                Ex. "Two Sum"
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
            int: Whether attempt was successful (0/1).
                Ex. 1
    """

    conn = get_conn()
    cur = conn.cursor()
    
    # Getting data from both problems and attempts tables.
    cur.execute(
        """
        SELECT p.id, p.title, p.difficulty, p.topics, a.date, a.time_taken, a.confidence, a.success
        FROM attempts a
        JOIN problems p ON a.problem_id = p.id
        """
    )
    
    attempts = cur.fetchall()
    conn.close()
    
    return attempts