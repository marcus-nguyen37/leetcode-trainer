# Caculate readiness score

def readiness_score(mastery, attempts):

    if not attempts:
        return 0

    avg_mastery = sum(mastery.values())/len(mastery) if mastery else 0

    topics = set()
    for row in attempts:
        for t in row[2].split(","):
            topics.add(t)

    coverage = len(topics)/10  # assume 10 major topics

    recent = sum(1 for a in attempts if a[3] > "2025-01-01")
    activity = min(recent/20,1)

    return 0.4*avg_mastery + 0.3*coverage + 0.3*activity
