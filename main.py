import sys
from data.database import init_db
from data.models import *
from analytics.mastery import topic_mastery
from analytics.readiness import readiness_score
from engine.recommender import recommend_topics

init_db()

cmd = sys.argv[1]

# "add_problem" command adds a LeetCode q. (not attempt) to database
if cmd == "add_problem":
    add_problem(sys.argv[2], sys.argv[3], sys.argv[4].split(","))
    print(f"Added problem: {sys.argv[2]}")

# "log" adds an LeetCode attempt using cache-aside pattern
elif cmd == "log":
    # Usage: python main.py log "Two Sum" "2025-02-17" 30 85 1
    problem_title = sys.argv[2]
    date = sys.argv[3]
    time_taken = int(sys.argv[4])
    confidence = int(sys.argv[5])
    success = sys.argv[6] == "1"
    
    result = log_attempt(problem_title, date, time_taken, confidence, success)
    
    if result['success']:
        print(f"✓ Attempt logged (ID: {result['attempt_id']})")
    else:
        print(f"✗ Error: {result['error']}")

# "stats" displays the mastery score of each topic
elif cmd == "stats":
    attempts = get_attempts()
    mastery = topic_mastery(attempts)

    print("\nTopic Mastery:")
    for k,v in mastery.items():
        print(k, round(v,3))

# "recommend" calculates and shows topics with lowest mastery
elif cmd == "recommend":
    attempts = get_attempts()
    mastery = topic_mastery(attempts)

    recs = recommend_topics(mastery)

    print("\nRecommended Topics:")
    for t,s in recs:
        print(t, round(s,3))

# "readiness" shows the calc'd. interview readiness score
elif cmd == "readiness":
    attempts = get_attempts()
    mastery = topic_mastery(attempts)

    score = readiness_score(mastery, attempts)
    print("\nInterview Readiness:", round(score*100,1),"%")
