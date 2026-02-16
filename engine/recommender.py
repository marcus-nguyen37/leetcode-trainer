# Recommends topics to revise, based on how weak mastery is.

def recommend_topics(mastery):

    weakness = {t:1-v for t,v in mastery.items()}

    ranked = sorted(weakness.items(), key=lambda x:x[1], reverse=True)

    return ranked[:5]
