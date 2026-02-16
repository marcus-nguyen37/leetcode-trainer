import sys
from db.database import init_db
from db.models import *
from analytics.mastery import topic_mastery
from analytics.readiness import readiness_score
from engine.recommender import recommend_topics

init_db()

cmd = sys.argv[1]

if cmd == "add_problem":
    add_problem(sys.argv[2], sys.argv[3], sys.argv[4].split(","))

elif cmd == "log":
    log_attempt(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]=="1")

elif cmd == "stats":
    attempts = get_attempts()
    mastery = topic_mastery(attempts)

    print("\nTopic Mastery:")
    for k,v in mastery.items():
        print(k, round(v,3))

elif cmd == "recommend":
    attempts = get_attempts()
    mastery = topic_mastery(attempts)

    recs = recommend_topics(mastery)

    print("\nRecommended Topics:")
    for t,s in recs:
        print(t, round(s,3))

elif cmd == "readiness":
    attempts = get_attempts()
    mastery = topic_mastery(attempts)

    score = readiness_score(mastery, attempts)
    print("\nInterview Readiness:", round(score*100,1),"%")
