
# GraphQL endpoint for LeetCode API
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Name of database storing problems and attempts tables
DB_NAME = "leetcode.db"

# Mathematical constant to calculate retention decay
RETENTION_DECAY = 7

# Constant when calculating recency. Has to be a positive value.
RECENCY_DECAY = 14

# Proportions for each factor in mastery calculation. These 3 constants should always add up to 1 (100%)
MASTERY_SUCCESS_PROP = 0.4
MASTERY_SPEED_PROP = 0.3
MASTERY_RECENCY_PROP = 0.3