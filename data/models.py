from .database import get_conn
from .leetcode_api import fetch_problem_from_leetcode


def add_problem(title, difficulty, topics):
    """
    Add a LeetCode problem to the local database.
    
    This function stores metadata about a problem (title, difficulty, topics) 
    for future reference. This is NOT the same as logging an attempt.
    
    Args:
        title (str): The problem title (e.g., "Two Sum").
        difficulty (str): The difficulty level (e.g., "Easy", "Medium", "Hard").
        topics (list): A list of topic strings (e.g., ["Array", "Hash Table"]).
    """
    conn = get_conn()
    cur = conn.cursor()

    # Convert topics list to comma-separated string for storage
    topics_str = ",".join(topics)
    
    cur.execute(
        "INSERT INTO problems(title,difficulty,topics) VALUES(?,?,?)",
        (title, difficulty, topics_str)
    )

    conn.commit()
    conn.close()


def get_problem_by_title(title):
    """
    Retrieve a problem from the local database by its title.
    
    This is the first step in the cache-aside pattern:
    check if the problem already exists locally before calling the API.
    
    Args:
        title (str): The problem title to search for.
    
    Returns:
        tuple: (problem_id, title, difficulty, topics) if found.
        None: If the problem does not exist in the local database.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title, difficulty, topics FROM problems WHERE title = ?",
        (title,)
    )
    
    row = cur.fetchone()
    conn.close()
    
    return row


def log_attempt(problem_title, date, time_taken, confidence, success):
    """
    Log a LeetCode attempt with the cache-aside pattern for problem lookup.
    
    This is the main entry point for recording user attempts. It implements the flow:
    1. Check if the problem exists in the local database (cache).
    2. If not, fetch from the LeetCode API and add to the database.
    3. If the API fails or problem doesn't exist, return an error.
    4. If successful, insert the attempt record.
    
    Args:
        problem_title (str): The title of the LeetCode problem being attempted.
        date (str): The date of the attempt (ISO format: "YYYY-MM-DD").
        time_taken (int): Time spent on the problem (in minutes).
        confidence (int): User's confidence level (0-100, typically).
        success (bool or int): Whether the attempt was successful (1 = yes, 0 = no).
    
    Returns:
        dict: Success response with attempt_id if logged successfully.
              Example: {'success': True, 'attempt_id': 42}
        dict: Error response if problem not found or API call failed.
              Example: {'success': False, 'error': 'Problem not found in database or LeetCode'}
    
    Raises:
        None: All errors are caught and returned in the response dict.
    """
    
    # STEP 1: Check if the problem exists in the local database (CACHE)
    problem_row = get_problem_by_title(problem_title)
    
    if problem_row:
        # Problem found in cache! Extract the problem_id and use it.
        problem_id = problem_row[0]
    else:
        # STEP 2b: Problem not in cache, attempt to fetch from LeetCode API
        problem_data = fetch_problem_from_leetcode(problem_title)
        
        if problem_data is None:
            # STEP 2b(ii): API failed or problem does not exist on LeetCode
            return {
                'success': False,
                'error': f'Problem "{problem_title}" not found in database or LeetCode'
            }
        
        # STEP 2b(i): API successful! Add the problem to the local database
        # Extract title, difficulty, topics from API response
        api_title = problem_data.get('title', problem_title)
        api_difficulty = problem_data.get('difficulty', 'Unknown')
        api_topics = problem_data.get('topics', [])
        
        # Insert the new problem into the database
        add_problem(api_title, api_difficulty, api_topics)
        
        # Retrieve the newly inserted problem to get its ID
        problem_row = get_problem_by_title(api_title)
        problem_id = problem_row[0]
    
    # STEP 3: Insert the attempt record using the problem_id
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO attempts(problem_id, date, time_taken, confidence, success)
        VALUES (?, ?, ?, ?, ?)
        """,
        (problem_id, date, time_taken, confidence, int(success))
    )

    attempt_id = cur.lastrowid  # Get the ID of the newly inserted attempt
    conn.commit()
    conn.close()
    
    # Return success response with the attempt ID
    return {
        'success': True,
        'attempt_id': attempt_id
    }


def get_attempts():
    """
    Retrieve all logged attempts with their associated problem metadata.
    
    This joins the attempts table with the problems table to provide
    complete information about each attempt.
    
    Returns:
        list of tuples: Each tuple contains:
                       (title, difficulty, topics, date, time_taken, confidence, success)
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute(
        """
        SELECT p.title, p.difficulty, p.topics, a.date, a.time_taken, a.confidence, a.success
        FROM attempts a
        JOIN problems p ON a.problem_id = p.id
        """
    )
    
    rows = cur.fetchall()
    conn.close()
    
    return rows
