from .database import get_conn

def add_problem(title, difficulty, topics):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO problems(title,difficulty,topics) VALUES(?,?,?)",
        (title, difficulty, ",".join(topics))
    )

    conn.commit()
    conn.close()

def log_attempt(problem_id, date, time_taken, confidence, success):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO attempts(problem_id,date,time_taken,confidence,success)
    VALUES(?,?,?,?,?)
    """,(problem_id,date,time_taken,confidence,int(success)))

    conn.commit()
    conn.close()

def get_attempts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.title,p.difficulty,p.topics,a.date,a.time_taken,a.confidence,a.success
        FROM attempts a
        JOIN problems p ON a.problem_id=p.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
