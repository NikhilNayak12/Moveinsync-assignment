# MoveInSync Play Store Ratings Pulse

A small script that answers "How are our Play Store ratings?" on demand, for every MoveInSync Android app. Built as part of my Forward Deployed Engineer case study submission.

## Why this exists

The ratings question will be asked repeatedly, not once. The Play Store headline is an all-time average, so it hides a recent drop after a bad release. This script reports the recent picture, shows which complaint themes drive low ratings, and flags which app version caused a dip.

## What it does

1. Pulls all public reviews for four apps: Employee (`com.moveinsync.ets`), Field (`field.moveinsync.ets`), Driver Onboarding (`com.moveinsync.driver.dco`), Workplace (`com.workinsync.meeting`).
2. Tags each review with themes using transparent keyword rules: tracking/GPS, No-Show, booking/UI, crash/performance, ops/late cab, support ignored, login/OTP.
3. Saves everything to `reviews.csv` and prints a summary:
   - Rating by app, all-time sample vs last 30 days, with review counts
   - Theme share among 1 to 2 star reviews in the last 90 days
   - Employee app rating by version (versions with 30+ reviews), to catch release regressions
   - Reply coverage on 1 to 3 star reviews in the last 30 days

## Run it

```bash
pip install google-play-scraper pandas
python ratings_pulse.py
```

Output: `reviews.csv` plus the summary in your terminal. Run it weekly and compare with the previous run.

## Limits (please read)

- Keyword tagging is a first pass. A review can match several themes, and the word lists will produce some false matches. Next step: replace `tag()` with an LLM classifier.
- It uses public review data only. It cannot see crash rates, ANRs or install-level rating by version from Play Console. Those should be added as inputs when Console access exists.
- Scraping the Play Store is unofficial and may break if Google changes its page structure. For production, use the Google Play Developer API's reviews endpoint, which returns recent reviews for your own apps.
- Written for English reviews from India (`lang="en"`, `country="in"`). Change these in `pull()` to cover other markets.

## Planned next steps

- LLM-based theme tagging with one-line summaries per theme
- Post the weekly summary to Slack
- Alert when the 7-day average rating drops by 0.2 or more
- Add Apple App Store reviews

## Context

Full diagnosis and prioritised action plan are in the accompanying document and slide deck.
