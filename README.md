# LeetCode Trainer

A (currently) command-line-interface dashboard for optimising your LeetCode practice routine. Track attempts, measure mastery, and use spaced repetition to maximise retention, getting you ready for your technical interviews!

## Features

- **Problem Fetch & Caching**: Automatically fetches and caches LeetCode problem metadata via GraphQL API, with thanks to @akarsh1995 for providing the query structures for these calls.
- **Attempt Logging**: Record attempts with date, time, confidence level, and success/failure outcomes.
- **Mastery Scoring**: Calculate topic mastery based on success rate, solution speed, confidence, and recency of attempt modelled by exponential formulas.
- **Performance Analytics**: Get comprehensive stats on success rates, difficulty breakdown, and weak areas
- **Topic Recommendations**: Get recommended which weak topics you should tackle next.
- **Spaced Repetition Cognitive Science**: Automatically schedule problem reviews based on your confidence levels, leveraging science-backed methods to help combat the forgettign curve.
- **Review Management**: See what problems are due for your review, either today or on any day.

## Basic installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marcus-nguyen37/leetcode-trainer.git
   cd leetcode-trainer
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # On Windows PowerShell
   # or
   source .venv/bin/activate  # On Linux/macOS
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Commands Reference

### `log <slug> <date> <time_min> <confidence> <success>`
Log a LeetCode problem attempt.

**Arguments:**
- `slug` - Problem slug from LeetCode URL (e.g., "two-sum", "add-two-numbers")
- `date` - Attempt date in format `YYYY-MM-DD`
- `time_min` - Time spent in minutes (integer)
- `confidence` - Confidence level 1-5 (1=very unsure, 5=very confident)
- `success` - 0 if failed, 1 if passed

**Example:**
```bash
python main.py log two-sum 2026-02-20 30 4 1
```

**Notes:**
- If the problem isn't cached, it will auto-fetch from LeetCode's API.
- Review dates are automatically scheduled based on your confidence and success, no need to manually add it yourself.
- All inputs are validated before insertion.

---

### `stats`
Display a comprehensive performance report.

**Output includes:**
- Total attempts and unique problems practiced.
- Overall success rate.
- Average time spent per attempt.
- Success rate broken down by difficulty (Easy/Medium/Hard).
- Your strongest and weakest topics.
- Top 3 recommended topics for review.

**Example:**
```bash
python main.py stats
```

---

### `reviews <date>`
Show problems due for review today or on a specified date.

**Arguments:**
- `date` (optional) - Specific date in ISO format `YYYY-MM-DD` (defaults to today)

**Example:**
```bash
python main.py reviews
python main.py reviews 2026-02-25
```

**Notes:**
- Spaced repetition schedules reviews based on your confidence level.
- Failed attempts are scheduled for the next day (1 day).
- Passed attempts are scheduled using these intervals:
  - Confidence 1-2: 2 days
  - Confidence 3: 5 days
  - Confidence 4: 7 days
  - Confidence 5: 10 days
- These values are modifiable through `constants.py` through `CONF_REVIEW_DAYS`.

---

### `schedule <slug>`
View the review schedule for all problems or a specific problem, given the problem's title slug.

**Arguments:**
- `slug` (optional) - Problem slug (e.g., "two-sum"). If omitted, shows all scheduled reviews.

**Example:**
```bash
python main.py schedule
python main.py schedule two-sum
```

**Output:**
- Problem title and slug.
- Next scheduled review date.
- Sorted chronologically.

---

### `add <slug> <title> <difficulty> <topics>`
Manually add a problem to the local database (rarely needed due to auto-API fetch though).

**Arguments:**
- `slug` - Problem's title slug.
- `title` - Full problem title
- `difficulty` - One of: Easy, Medium, Hard
- `topics` - Comma-separated topics (e.g., "Array,Hash Table")

**Example:**
```bash
python main.py add two-sum "Two Sum" Easy "Array,Hash Table"
```

**Notes:**
- Most of the time, problems are auto-fetched when you log an attempt. You only really need to use this if the API fetch fails for some reason.

---

### `help`
Display CLI usage information and all available commands.

```bash
python main.py help
```

---

## Shortcut (Optional)

To avoid tediously typing `python main.py` every time, add this function to your PowerShell profile:

```powershell
function lc { python main.py @args }
```

Then use:
```powershell
lc log two-sum 2026-02-20 30 4 1
lc stats
lc reviews
```

## Database

- **Location:** `leetcode.db` (using SQLite)
- **Tables:**
  - `problems` - Cached LeetCode problem metadata (id, slug, title, difficulty, topics)
  - `attempts` - Your practice attempts with outcomes
  - `reviews` - Spaced repetition schedule

The database is automatically initialised on first run of `main.py`.

## Configuration

Edit `constants.py` to customise:

- **MASTERY_DAYS_WINDOW** - Time window for mastery calculation (default: 60 days)
- **EXPECTED_TIMES** - Expected completion times by difficulty (used to calculate speed score)
- **MIN_ATTEMPT_RECC_THRESHOLD** - Minimum attempts before a topic is recommended
- **NUM_RECC** - Number of topics to recommend
- **CONF_REVIEW_DAYS** - Review schedule based on confidence level
- And lots more :D

## Mastery Scoring

Your mastery score for each topic (0–1) is calculated as:

```
Mastery = 0.35 × Success Rate
         + 0.25 × Speed Score (time vs expected)
         + 0.20 × Recency Score (exponential decay)
         + 0.20 × Confidence Score (average confidence)
```
Note that the weights of these factors can be adjusted by editing their respective constants in `constants.py`.

Topics are only included if you have at least 1 attempt within the last 60 days. The 60-day window can be modified through `constants.py`.

## Requirements

- **Python 3.10+**
- **requests** - For LeetCode API calls
- **sqlite3** - Built-in (no install needed)

Please see `requirements.txt` for exact versions needed.

## Future Enhancements That I Might Add...

- [ ] Actual GUI!
- [ ] Web dashboard for visualisation
- [ ] Export stats to CSV/PDF
- [ ] Integration with actual LeetCode submission tracking
- [ ] Streak tracking
- [ ] Difficulty-specific mastery metrics
- [ ] Study goals and milestones
- [ ] Problem filtering/searching by topic
