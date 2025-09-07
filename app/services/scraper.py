import requests
import logging
from bs4 import BeautifulSoup

from app.core.logger import get_logger

logger = get_logger(__name__)

def scrape_jobs(skills: list[str]) -> list[dict]:
    jobs = []
    for skill in skills:
        url = f"https://www.indeed.com/jobs?q={skill}&l="
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        logger.info(f"Scraping {response}")
        soup = BeautifulSoup(response.text, "html.parser")

        for div in soup.find_all("div", class_="job_seen_beacon")[:5]:  # top 5 jobs
            title = div.find("h2").text.strip() if div.find("h2") else "No title"
            logger.info(f"title: {title}")
            company = div.find("span", class_="companyName").text.strip() if div.find("span", class_="companyName") else "Unknown"
            jobs.append({"skill": skill, "title": title, "company": company})

        logger.info(f"jobs: {jobs}")

    return jobs