from statistics import mean
from collections import defaultdict

from data.database_access import get_attempts
from analytics.mastery import calculate_mastery
from analytics.recommender import recommend_topics

def generate_report() -> str:
    """
    Generates a formatted CLI performance report ready for print.
    """

    attempts = get_attempts()

    if not attempts:
        return "No attempts logged yet."

    total_attempts = len(attempts)
    unique_problems = len(set(a[0] for a in attempts)) # Making a set of the problem slugs ensures uniqueness

    successes = [a[6] for a in attempts]
    success_rate = mean(successes) * 100

    # TODO: probably make minor helper functions to calculate values like average time?
    avg_time = mean(a[4] for a in attempts)

    # Calculate success rate of each difficulty level
    diff_data = defaultdict(list)

    for _, difficulty, *_ , success in attempts:
        diff_data[difficulty].append(success)

    diff_stats = {
        d: round(mean(v) * 100, 1)
        for d, v in diff_data.items()
    }

    # Calculate strongest and weakest topic
    mastery = calculate_mastery()

    if mastery:
        strongest = max(mastery.items(), key=lambda x: x[1])
        weakest = min(mastery.items(), key=lambda x: x[1])
    else:
        strongest = ("N/A", 0)
        weakest = ("N/A", 0)

    # Getting recommended topics
    recommendations = recommend_topics()

    # Formatting for outputting
    lines = []
    lines.append("===== STATS REPORT =====\n")

    lines.append(f"Total Attempts: {total_attempts}")
    lines.append(f"Problems Practiced: {unique_problems}")
    lines.append(f"Success Rate: {success_rate:.1f}%")
    lines.append(f"Average Time: {avg_time:.1f} min\n")

    lines.append("Success Rate by Difficulty:")
    for d, rate in diff_stats.items():
        lines.append(f"  {d}: {rate}%")

    lines.append("\nStrongest Topic:")
    lines.append(f"  {strongest[0]} ({strongest[1]:.2f})")

    lines.append("\nWeakest Topic:")
    lines.append(f"  {weakest[0]} ({weakest[1]:.2f})")

    lines.append("\nRecommended Topics:")
    if recommendations:
        for topic, score in recommendations:
            lines.append(f"  {topic} ({score:.2f})")
    else:
        lines.append("  Not enough data yet.")

    return "\n".join(lines)