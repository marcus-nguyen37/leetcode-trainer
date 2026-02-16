from collections import defaultdict
from datetime import datetime
import math

# Calculate the mastery score for each topic
def topic_mastery(attempts):

    topic_data = defaultdict(list)

    for title,difficulty,topics,date,time,conf,success in attempts:
        for topic in topics.split(","):
            topic_data[topic].append((time,success,date))

    mastery = {}

    for topic,entries in topic_data.items():
        success_rate = sum(e[1] for e in entries)/len(entries)

        avg_time = sum(e[0] for e in entries)/len(entries)
        speed_score = 1/(1+avg_time)

        last_date = max(e[2] for e in entries)
        days = (datetime.now()-datetime.fromisoformat(last_date)).days
        recency = math.exp(-days/14)

        mastery[topic] = 0.4*success_rate + 0.3*speed_score + 0.3*recency

    return mastery
