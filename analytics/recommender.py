from collections import Counter

from data.database_access import get_attempts
from analytics.mastery import calculate_mastery
from constants import MIN_ATTEMPT_RECC_THRESHOLD, NUM_RECC

def count_attempts_per_topic() -> dict[str, int]:
    """
    Counts the number of attempts made, for each topic.

    Returns:
        dict[str, int]: Mapping topic to number of attempts.
    """

    attempts = get_attempts()
    counts = Counter()

    for _, _, topics, *_ in attempts:
        for topic in topics.split(","):
            topic = topic.strip()
            if topic:
                counts[topic] += 1

    return counts


def recommend_topics() -> list[tuple[str, float]]:
    """
    Returns list of weakest topics sorted ascending by mastery.

    Returns:
        list[tuple[str, int]]: In the form [(topic, mastery_score), ...]
    """

    mastery = calculate_mastery()
    counts = count_attempts_per_topic()

    # Filter topics with too few attempts
    eligible = {
        topic: score for topic, score in mastery.items()
        if counts.get(topic, 0) >= MIN_ATTEMPT_RECC_THRESHOLD
    }

    # Sort with weakest first
    ranked = sorted(eligible.items(), key=lambda x: x[1])

    # Returning only the weakest NUM_RECC number of topics
    return ranked[:NUM_RECC]
