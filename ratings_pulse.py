"""MoveInSync Play Store ratings pulse.

Answers "How are our Play Store ratings?" on demand.
Setup:  pip install google-play-scraper pandas
Run:    python ratings_pulse.py            (writes reviews.csv + prints summary)
Not yet run against live Play data from my sandbox (no access to play.google.com).
"""
import pandas as pd
from datetime import datetime, timedelta
from google_play_scraper import app, reviews_all, Sort

APPS = {
    "Employee": "com.moveinsync.ets",
    "Field": "field.moveinsync.ets",
    "DriverOnboarding": "com.moveinsync.driver.dco",
    "Workplace": "com.workinsync.meeting",
}

# Transparent keyword rules; replace with an LLM classifier later.
THEMES = {
    "tracking_gps": ["gps", "location", "tracking", "track", "live"],
    "no_show": ["no show", "no-show", "noshow", "check-in", "check in"],
    "booking_ui": ["book", "update", "ui", "confusing", "button", "shuttle"],
    "crash_perf": ["crash", "stuck", "loading", "slow", "hang", "not opening", "lag"],
    "ops_late_cab": ["late", "delay", "driver", "cab", "waiting", "rude"],
    "support_ignored": ["complaint", "ignore", "no response", "support", "helpline"],
    "login_otp": ["login", "otp", "register", "sign in", "not able to"],
}


def tag(text):
    t = (text or "").lower()
    hits = [k for k, words in THEMES.items() if any(w in t for w in words)]
    return hits or ["other"]


def pull():
    frames = []
    for name, pkg in APPS.items():
        rows = reviews_all(pkg, lang="en", country="in", sort=Sort.NEWEST)
        df = pd.DataFrame(rows)
        if df.empty:
            continue
        df["app"] = name
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["themes"] = df["content"].apply(tag)
    return df


def summarize(df):
    cutoff = datetime.now() - timedelta(days=30)
    print("\n== Rating by app (all-time sample vs last 30 days) ==")
    recent = df[df["at"] >= cutoff]
    out = pd.DataFrame({
        "all_time": df.groupby("app")["score"].mean().round(2),
        "last_30d": recent.groupby("app")["score"].mean().round(2),
        "n_30d": recent.groupby("app")["score"].count(),
    })
    print(out)

    print("\n== Themes in 1-2 star reviews, last 90 days (% of those reviews) ==")
    low = df[(df["score"] <= 2) & (df["at"] >= datetime.now() - timedelta(days=90))]
    if len(low):
        counts = low.explode("themes")["themes"].value_counts()
        print((counts / len(low) * 100).round(1))

    print("\n== Employee app: rating by app version (n>=30), newest versions ==")
    emp = df[(df["app"] == "Employee") & df["appVersion"].notna()]
    byv = emp.groupby("appVersion")["score"].agg(["mean", "count"])
    print(byv[byv["count"] >= 30].sort_index().tail(8).round(2))

    print("\n== Reply coverage on 1-3 star reviews (last 30 days) ==")
    r = recent[recent["score"] <= 3]
    if len(r):
        print(f"{r['replyContent'].notna().mean():.0%} replied")


if __name__ == "__main__":
    data = pull()
    data.to_csv("reviews.csv", index=False)
    summarize(data)
