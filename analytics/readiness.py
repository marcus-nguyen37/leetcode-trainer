# Caculate readiness score

def readiness_score(mastery, attempts):

    if not attempts:
        return 0

    avg_mastery = sum(mastery.values())/len(mastery) if mastery else 0

    topics = set()
    for row in attempts:
        # row[3] accesses the attempted problem's topics
        for t in row[3].split(","):
            topics.add(t)

    coverage = len(topics)/10  # assume 10 major topics for now, probably change this later to specifically cover listed topics

    # TODO: Change the magic ISO string "2025-01-01" to a dynamic variable representing ISO date 1 month before now.
    # so that recent effectively counts the number of attempts made in the last month
    # a[4] accesses the date column since each row in attempts is a tuple with structure:
    # (`problem_id`, `title`, `difficulty`, `topics`, `date`, ...)
    recent = sum(1 for a in attempts if a[4] > "2025-01-01")
    activity = min(recent/30,1)

    # Arbitrary proportions for now
    return 0.4*avg_mastery + 0.3*coverage + 0.3*activity
