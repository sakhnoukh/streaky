from datetime import date, timedelta


def current_streak(dates: set[date], today: date) -> int:
    if today not in dates:
        return 0
    streak, cur = 1, today
    while (cur := cur - timedelta(days=1)) in dates:
        streak += 1
    return streak

def best_streak(dates: set[date]) -> int:
    if not dates:
        return 0
    s, seen = 0, set(dates)
    for d in list(seen):
        if d - timedelta(days=1) not in seen:
            run, cur = 1, d
            while (cur := cur + timedelta(days=1)) in seen:
                run += 1
            s = max(s, run)
    return s
