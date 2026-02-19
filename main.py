import sys
from datetime import datetime

from data.database import init_db
from data.database_access import add_problem, log_attempt, get_problem_by_slug, get_or_create_problem
from data.scheduler import get_due_reviews, get_review_schedule
from analytics.stats import generate_report

init_db()

def print_usage():
    """Display CLI usage information."""
    usage = """
USE:
    python main.py <command> [arguments]

COMMANDS:
    log <slug> <date> <time_min> <confidence> <success>
        Log a LeetCode attempt.
        
        Args:
            slug - Problem slug (e.g., "two-sum")
            date - Attempt date in YYYY-MM-DD format
            time_min - Time spent in minutes (integer)
            confidence - Confidence level (1-5, inclusive) (integer)
            success - Whether solved: 0 (Failed) or 1 (Passed)
        
        Ex: python main.py log two-sum 2026-02-20 30 4 1

    add <slug> <title> <difficulty> <topic1,topic2,...>
        Add a problem to the local database. If problem doesn't exist,
        fetches from LeetCode API automatically.
        
        Args:
            slug - Problem slug (e.g., "two-sum")
            title - Problem title (e.g., "Two Sum")
            difficulty - Difficulty: Easy, Medium, or Hard
            topics - Comma-separated topics (e.g., "Array,Hash Table")
        
        Ex: python main.py add two-sum "Two Sum" Easy "Array,Hash Table"

    stats
        Display a comprehensive performance report including:
        - Total attempts and problems practiced
        - Success rate overall and by difficulty
        - Strongest and weakest topics
        - Recommended topics for review
        
        Example: python main.py stats

    reviews <date>
        Show problems due for review, either today or on a specified date.
        
        Args:
            date - Specific date (YYYY-MM-DD), optional (defaults to today)
        
        Example: python main.py reviews
        Example: python main.py reviews 2026-02-21

    schedule <slug>
        Show the review schedule for all problems or a specific problem.
        
        Args:
            slug - Problem slug (optional)
        
        Example: python main.py schedule
        Example: python main.py schedule two-sum

    help
        Show this usage information.
"""
    print(usage)


def cmd_log(args: list):
    """Handle 'log' command."""
    if len(args) < 5:
        print("Error: log requires 5 arguments: <slug> <date> <time_min> <confidence> <success>")
        return
    
    slug = args[0]
    date = args[1]
    
    try:
        time_taken = int(args[2])
        confidence = int(args[3])
        success = int(args[4])
    except ValueError:
        print("Error: time_min, confidence, and success must be integers")
        return
    
    result = log_attempt(slug, date, time_taken, confidence, success)
    
    if result["success"]:
        print(f"Attempt logged successfully (ID: {result['attempt_id']})")
    else:
        print(f"Error: {result['error']}")


def cmd_add(args: list):
    """Handle 'add' command."""
    if len(args) < 4:
        print("Error: add requires 4 arguments: <slug> <title> <difficulty> <topics>")
        return
    
    # TODO: defs just have user input slug, since adding a problem means calling API anyways
    slug = args[0]
    title = args[1]
    difficulty = args[2]
    topics = args[3].split(",")
    
    # Check if problem already cached
    existing = get_problem_by_slug(slug)
    if existing:
        print(f"Problem already cached: {existing[1]} ({existing[2]})")
        return
    
    # Try to fetch from API and add
    problem_id = get_or_create_problem(slug)
    
    if problem_id is None:
        # Fallback to manual add if API fails
        try:
            # We need to manually determine the problem_id
            # For now, just inform user
            print(f"Could not fetch problem '{slug}' from LeetCode API.")
            print("Please ensure the slug is correct (e.g., 'two-sum').")
        except Exception as e:
            print(f"Error adding problem: {str(e)}.")
    else:
        print(f"Problem added: {slug}.")


def cmd_stats():
    """Handle 'stats' command."""
    report = generate_report()
    print(report)


def cmd_reviews(args: list):
    """Handle 'reviews' command."""
    date = None
    if len(args) > 0:
        date = args[0]
    
    due_problems = get_due_reviews(date)
    
    if not due_problems:
        today = date if date else datetime.now().strftime("%Y-%m-%d")
        print(f"No reviews due on {today}.")
        return
    
    print(f"Problems due for review ({date or datetime.now().strftime('%Y-%m-%d')}):")
    conn = __import__('data.database', fromlist=['get_conn']).get_conn()
    cur = conn.cursor()
    
    for problem_id in due_problems:
        cur.execute(
            "SELECT slug, title, difficulty FROM problems WHERE id = ?",
            (problem_id,)
        )
        row = cur.fetchone()
        if row:
            print(f"  • {row[1]} ({row[0]}) - {row[2]}")
    
    conn.close()


def cmd_schedule(args: list):
    """Handle 'schedule' command."""
    if len(args) > 0:
        slug = args[0]
        problem = get_problem_by_slug(slug)
        
        if not problem:
            print(f"Problem '{slug}' not found in database.")
            return
        
        problem_id = problem[0]
        schedule = get_review_schedule(problem_id)
        
        if schedule:
            print(f"Review schedule for '{slug}':")
            print(f"Next review date: {schedule}.")
        else:
            print(f"No review scheduled for '{slug}'.")
    else:
        # Show all reviews
        schedule = get_review_schedule()
        
        if not schedule:
            print("No reviews scheduled.")
            return
        
        print("Review Schedule (all problems):")
        conn = __import__('data.database', fromlist=['get_conn']).get_conn()
        cur = conn.cursor()
        
        for problem_id, review_date in sorted(schedule.items(), key=lambda x: x[1]):
            cur.execute(
                "SELECT slug, title FROM problems WHERE id = ?",
                (problem_id,)
            )
            row = cur.fetchone()
            if row:
                print(f" - {row[1]} ({row[0]}) - Review on {review_date}")
        
        conn.close()


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if cmd == "log":
        cmd_log(args)
    elif cmd == "add":
        cmd_add(args)
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "reviews":
        cmd_reviews(args)
    elif cmd == "schedule":
        cmd_schedule(args)
    elif cmd == "help" or cmd == "-h" or cmd == "--help":
        print_usage()
    else:
        print(f"Unknown command: '{cmd}'")
        print("Use 'python main.py help' for usage information")


if __name__ == "__main__":
    main()
