import json
import os
import smtplib
import requests

from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urljoin


URL = "https://researchpark.illinois.edu/?post_type=job_listing"
SEEN_FILE = "seen_jobs.json"

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]


def get_jobs():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 Chrome/151 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = {}

    # Research Park's WordPress job pages contain links to individual
    # job_listing posts. Grab those URLs as unique identifiers.
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = " ".join(link.stripped_strings).strip()

        if not text:
            continue

        # Individual Research Park posts normally stay on the same domain.
        if "researchpark.illinois.edu" in href:
            full_url = urljoin(URL, href)

            # Ignore navigation / pagination / generic pages
            ignored = [
                "/work-here/",
                "/companies/",
                "/events/",
                "/news/",
                "/resources/",
                "/about/",
                "/job-dashboard/",
                "/job-alerts/",
                "/post-a-job/",
            ]

            if any(x in full_url for x in ignored):
                continue

            # Job title links tend to be meaningful headings.
            if len(text) >= 4 and len(text) <= 200:
                parent = link.find_parent(["h1", "h2", "h3", "h4"])

                if parent:
                    jobs[full_url] = text

    return jobs


def load_seen_jobs():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as file:
        return set(json.load(file))


def save_seen_jobs(job_urls):
    with open(SEEN_FILE, "w") as file:
        json.dump(sorted(job_urls), file, indent=2)


def send_email(new_jobs):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"🚨 {len(new_jobs)} New Research Park Job(s)"
    message["From"] = EMAIL_ADDRESS
    message["To"] = TO_EMAIL

    text = "New Research Park job listings:\n\n"

    html = """
    <h2>🚨 New UIUC Research Park Jobs</h2>
    <p>The following job listings were just detected:</p>
    """

    for url, title in new_jobs.items():
        text += f"{title}\n{url}\n\n"

        html += f"""
        <div style="margin-bottom:20px;">
            <strong>{title}</strong><br>
            <a href="{url}">View job</a>
        </div>
        """

    text += "\nResearch Park Job Board:\n"
    text += "https://researchpark.illinois.edu/work-here/careers/"

    html += """
    <br>
    <a href="https://researchpark.illinois.edu/work-here/careers/">
        Open Research Park Job Board
    </a>
    """

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(
            EMAIL_ADDRESS,
            TO_EMAIL,
            message.as_string()
        )


def main():
    print("Checking Research Park...")

    current_jobs = get_jobs()

    if not current_jobs:
        raise RuntimeError(
            "No jobs were found. Site structure may have changed."
        )

    seen_jobs = load_seen_jobs()

    # IMPORTANT:
    # First run establishes the baseline and sends no emails.
    if not seen_jobs:
        print(f"First run. Saving {len(current_jobs)} existing jobs.")
        save_seen_jobs(current_jobs.keys())
        return

    new_urls = set(current_jobs.keys()) - seen_jobs

    if new_urls:
        new_jobs = {
            url: current_jobs[url]
            for url in new_urls
        }

        print(f"Found {len(new_jobs)} new job(s)!")

        for url, title in new_jobs.items():
            print(title, url)

        send_email(new_jobs)

    else:
        print("No new jobs.")

    # Always update database
    save_seen_jobs(current_jobs.keys())


if __name__ == "__main__":
    main()
