from collections import defaultdict
from datetime import datetime
import math
from statistics import mean

from constants import RECENCY_DECAY,MASTERY_SUCCESS_PROP, MASTERY_SPEED_PROP, MASTERY_RECENCY_PROP

def get_mastery(attempts):
    """
    Returns the calculated mastery of each topic.
    
    :list[tuple] attempts: List of tuples produced by data.models.get_attempts()

    Each tuple is structured as:
    (`problem_id`, `title`, `difficulty`, `topics`, `date`, `time_taken`, `confidence`, `success`)
    
    """

    # Collecting all related attempts for each topic
    topic_data = defaultdict(list)

    # Unpacking: ignoring slug, which is the first column
    for _slug,difficulty,topics,date,time,conf,success in attempts:
        for topic in topics.split(","):
            topic_data[topic].append((time,success,date))

    # Calculating mastery score
    mastery = {}

    for topic,entries in topic_data.items():
        # Average success across all problem attempts of that topic
        success_rate = mean(e[1] for e in entries)

        # Average time across all problem attempts of topic
        avg_time = mean(e[0] for e in entries)
        # (1+avg_time) prevents zero-div error
        speed_score = 1/(1+avg_time)

        last_date = max(e[2] for e in entries)
        # Days since last attempt of that topic
        days = (datetime.now()-datetime.fromisoformat(last_date)).days
        recency = math.exp(-days/RECENCY_DECAY)

        # Proportions are a bit arbitrary
        mastery[topic] = MASTERY_SUCCESS_PROP*success_rate + MASTERY_SPEED_PROP*speed_score + MASTERY_RECENCY_PROP*recency

    return mastery
