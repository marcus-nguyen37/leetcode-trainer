
# GraphQL endpoint for LeetCode API
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Name of database storing problems and attempts tables
DB_NAME = "leetcode.db"

# Mathematical constant to calculate retention decay
RETENTION_DECAY = 7

# Constant when calculating recency. Has to be a positive value.
RECENCY_DECAY = 14

# Proportions for each factor in mastery calculation. These 4 constants should always add up to 1 (100%)
MASTERY_SUCCESS_PROP = 0.35
MASTERY_SPEED_PROP = 0.25
MASTERY_RECENCY_PROP = 0.2
MASTERY_CONF_PROP = 0.2

# Window of time that attempts will be considered in the mastery score of a topic
MASTERY_DAYS_WINDOW = 60

# Expected time of completion for a problem. Used as a baseline to judge whether completion time was good
EXPECTED_TIMES = {"Easy": 10, "Medium": 25, "Hard": 45}