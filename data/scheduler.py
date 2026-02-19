from datetime import datetime, timedelta
from .database import get_conn

from constants import CONF_REVIEW_DAYS

def next_review_days(confidence: int, success: int) -> int:
    """
    Determines how many days until next review based on confidence.
    """

    if success == 0:
        return 1
    return CONF_REVIEW_DAYS[confidence]


def schedule_review(problem_id: int, confidence: int, success: int):
    """
    Inserts next review date into reviews table.
    """

    days = next_review_days(confidence, success)
    review_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    # Inserts review. If there's already a pending review with same problem, update it
    cur.execute(
    """
    INSERT INTO reviews(problem_id, review_date)
    VALUES (?, ?)
    ON CONFLICT(problem_id)
    DO UPDATE SET review_date=excluded.review_date
    """,
    (problem_id, review_date)
    )
    

    conn.commit()
    conn.close()


def get_due_reviews(today: str | None = None) -> list[int]:
    """
    Returns list of problem_ids due for review today or earlier. If no date is inputted, uses current date as "today".
    """

    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT problem_id
        FROM reviews
        WHERE review_date <= ?
        """,
        (today,)
    )

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]


def show_due_reviews(today: str | None = None) -> list[str]:
    """
    Returns list of problem slugs due for review today or earlier.
    """

    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT p.slug
        FROM reviews r
        JOIN problems p ON r.problem_id = p.id
        WHERE r.review_date <= ?
        ORDER BY r.review_date ASC
        """,
        (today,)
    )

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]

def print_due_reviews():
    reviews = show_due_reviews()

    if not reviews:
        print("No reviews due today.")
        return

    print("Problems to review today:\n")

    for slug in reviews:
        print(f"- {slug}")


def get_review_schedule(problem_id: int | None = None) -> dict[int, str] | str | None:
    """
    Get the review schedule for problems.
    
    Args:
        problem_id (int | None): If provided, returns the review date string for that problem.
                                 If None, returns dict of all scheduled reviews.
    
    Returns:
        str: Review date for a specific problem (if problem_id provided)
        dict[int, str]: Mapping of problem_id to review_date (if no problem_id provided)
        None: If problem has no scheduled review
    """
    conn = get_conn()
    cur = conn.cursor()
    
    if problem_id is not None:
        # Get review date for specific problem
        cur.execute(
            "SELECT review_date FROM reviews WHERE problem_id = ?",
            (problem_id,)
        )
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    else:
        # Get all scheduled reviews
        cur.execute(
            "SELECT problem_id, review_date FROM reviews ORDER BY review_date ASC"
        )
        rows = cur.fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows} if rows else {}
