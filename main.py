import sys
from data.database import init_db
from data.models import *
from analytics.mastery import get_mastery
from analytics.readiness import readiness_score
from engine.recommender import recommend_topics

init_db()

cmd = sys.argv[1]

# "add_problem" command adds a LeetCode problem (not an attempt) to the database
# Usage: python main.py add_problem <problem_id> <slug> <title> <difficulty> <topic1,topic2,...>
if cmd == "add_problem":
    # Parsing arguments
    # TO-DO: add validation
    problem_id = int(sys.argv[2])
    slug = sys.argv[3]
    title = sys.argv[4]
    difficulty = sys.argv[5]
    topics = sys.argv[6].split(",")
    add_problem(problem_id, slug, title, difficulty, topics)
    print(f"Added problem: {problem_id} - {title}")

# "log" adds an LeetCode attempt using cache-aside pattern
elif cmd == "log":
    # Usage: python main.py log <slug> "YYYY-MM-DD" <time_min> <confidence> <0|1>
    slug = sys.argv[2]
    date = sys.argv[3]
    time_taken = int(sys.argv[4])
    confidence = int(sys.argv[5])
    success = sys.argv[6] == "1"
    
    result = log_attempt(slug, date, time_taken, confidence, success)
    
    if result["success"]:
        print(f"Attempt logged (ID: {result["attempt_id"]})")
    else:
        print(f"Error: {result["error"]}")

# "stats" displays the mastery score of each topic
elif cmd == "stats":
    attempts = get_attempts()
    mastery = get_mastery(attempts)

    print("\nTopic Mastery:")
    for k,v in mastery.items():
        print(k, round(v,3))

# "recommend" calculates and shows topics with lowest mastery
elif cmd == "recommend":
    attempts = get_attempts()
    mastery = get_mastery(attempts)

    recs = recommend_topics(mastery)

    print("\nRecommended Topics:")
    for t,s in recs:
        print(t, round(s,3))

# "readiness" shows the calc'd. interview readiness score
elif cmd == "readiness":
    attempts = get_attempts()
    mastery = get_mastery(attempts)

    score = readiness_score(mastery, attempts)
    print("\nInterview Readiness:", round(score*100,1),"%")
