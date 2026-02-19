from collections import defaultdict
from datetime import datetime, timedelta
import math
from statistics import mean

from data.models import get_attempts
from constants import RECENCY_DECAY,MASTERY_SUCCESS_PROP, MASTERY_SPEED_PROP, MASTERY_RECENCY_PROP, MASTERY_CONF_PROP, EXPECTED_TIMES, MASTERY_DAYS_WINDOW

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def recency_score(last_date: datetime) -> float:
    days = (datetime.now() - last_date).days
    return math.exp(-days / RECENCY_DECAY)


def speed_score(avg_time: float, difficulty: str) -> float:
    expected = EXPECTED_TIMES.get(difficulty)
    if avg_time == 0:
        return 1
    return min(expected / avg_time, 1)


def calculate_mastery() -> dict[str, float]:
    """
    Returns dictionary mapping topic -> mastery score (0–1).
    Only considers attempts within last 60 days (or whatever MASTERY_DAYS_WINDOW) is.
    """

    attempts = get_attempts()
    cutoff = datetime.now() - timedelta(days=MASTERY_DAYS_WINDOW)

    topic_data = defaultdict(list)

    for slug, difficulty, topics, date, time_taken, confidence, success in attempts:
        dt = parse_date(date)

        if dt < cutoff:
            continue

        # Grouping each attempt based on topics
        topic_list = topics.split(",")

        for topic in topic_list:
            topic_data[topic.strip()].append(
                (difficulty, dt, time_taken, confidence, success)
            )

    # Computing mastery scores
    mastery_scores = {}

    for topic, rows in topic_data.items():

        # Calculating factors that contribute to topic mastery. Each factor is a numerical value between 0 to 1

        success_rate = mean(r[4] for r in rows)

        avg_conf = mean(r[3] for r in rows)
        conf_score = avg_conf / 5 # Dividing by 5 normalises confidence score

        last_date = max(r[1] for r in rows)
        recency = recency_score(last_date)

        speed_vals = [speed_score(r[2], r[0]) for r in rows]
        avg_speed = mean(speed_vals)

        mastery = (
            MASTERY_SUCCESS_PROP * success_rate
            + MASTERY_SPEED_PROP * avg_speed
            + MASTERY_RECENCY_PROP * recency
            + MASTERY_CONF_PROP * conf_score
        )

        mastery_scores[topic] = round(mastery, 2)

    return mastery_scores