from collections import defaultdict
from datetime import datetime
import math


def get_mastery(attempts):
    """
    Returns the calculated mastery of each topic.
    
    :list[tuple] attempts: List of tuples produced by data.models.get_attempts()

    Each tuple is structured as:
    (`problem_id`, `title`, `difficulty`, `topics`, `date`, `time_taken`, `confidence`, `success`)
    
    """

    # Collecting all related attempts for each topic
    topic_data = defaultdict(list)

    # Unpacking: ignore problem ID, which is the first column
    for _id,title,difficulty,topics,date,time,conf,success in attempts:
        for topic in topics.split(","):
            topic_data[topic].append((time,success,date))

    # Calculating mastery score
    mastery = {}

    for topic,entries in topic_data.items():
        success_rate = sum(e[1] for e in entries)/len(entries)

        avg_time = sum(e[0] for e in entries)/len(entries)
        speed_score = 1/(1+avg_time)

        last_date = max(e[2] for e in entries)
        days = (datetime.now()-datetime.fromisoformat(last_date)).days
        recency = math.exp(-days/14)

        # Proportions are a bit arbitrary
        mastery[topic] = 0.4*success_rate + 0.3*speed_score + 0.3*recency

    return mastery
