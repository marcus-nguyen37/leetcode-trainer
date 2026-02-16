import math
from datetime import datetime

from constants import RETENTION_DECAY

# Memory decay model

# Calculate retention score
def retention_score(date_str, confidence):
    days = (datetime.now() - datetime.fromisoformat(date_str)).days
    return confidence * math.exp(-days/RETENTION_DECAY)
