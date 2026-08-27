# UIUC Research Park Job Monitor

A lightweight Python automation that monitors the University of Illinois Research Park job board and sends an email alert whenever a new job listing appears.

## What It Does

This project automatically:

- Checks the UIUC Research Park job board
- Extracts current job listing URLs
- Compares them against previously seen jobs
- Detects newly posted jobs
- Sends an email alert with the job title and direct link
- Stores seen jobs so duplicate alerts are avoided
- Runs automatically using GitHub Actions

## Job Board

This monitor watches:

https://researchpark.illinois.edu/work-here/careers/

## How It Works

The script keeps track of previously detected job listings in:

```text
seen_jobs.json
```

Each time the workflow runs:

1. The Research Park job board is fetched.
2. Job listing URLs are collected.
3. The current listings are compared against `seen_jobs.json`.
4. If a new listing is found, an email alert is sent.
5. The new listing is added to `seen_jobs.json`.

The first run establishes a baseline of existing jobs and does not send alerts for those listings.

## Email Alerts

When a new job is detected, the email includes:

- Number of new jobs detected
- Job title
- Direct link to the job posting
- Link to the Research Park job board

Example:

```text
🚨 1 New Research Park Job(s)

Software Engineering Intern

View job:
https://researchpark.illinois.edu/job/software-engineering-intern/
```

## Automation

GitHub Actions runs the monitor approximately every 5 minutes.

The workflow is located at:

```text
.github/workflows/monitor.yml
```

The schedule is configured with:

```yaml
schedule:
  - cron: "*/5 * * * *"
```

GitHub scheduled workflows may occasionally run a few minutes late depending on platform load.

## Project Structure

```text
research-park-job-monitor/
│
├── monitor.py
├── requirements.txt
├── seen_jobs.json
├── README.md
│
└── .github/
    └── workflows/
        └── monitor.yml
```

## Requirements

The project uses:

- Python 3
- Requests
- Beautiful Soup
- GitHub Actions
- Gmail SMTP

Python dependencies are stored in:

```text
requirements.txt
```

and include:

```text
requests
beautifulsoup4
```

## GitHub Secrets

The workflow requires three GitHub Actions secrets:

```text
EMAIL_ADDRESS
EMAIL_PASSWORD
TO_EMAIL
```

### EMAIL_ADDRESS

The Gmail account used to send alerts.

### EMAIL_PASSWORD

A Google App Password used for Gmail SMTP authentication.

Do not use your normal Google account password.

### TO_EMAIL

The email address that receives job alerts.

## Running Manually

The monitor can also be triggered manually through GitHub Actions:

```text
Actions
→ Monitor Research Park Jobs
→ Run workflow
```

## Preventing Duplicate Alerts

Previously detected job URLs are stored in:

```text
seen_jobs.json
```

A notification is only sent when a job URL appears that is not already stored in this file.

## Reliability

The script raises an error if no job listings are detected. This helps prevent the monitor from silently overwriting its stored job list if the Research Park website structure changes.

## Purpose

This project was created to automatically track new internship and job opportunities at the University of Illinois Research Park without repeatedly checking the job board manually.
