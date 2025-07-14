print("SunilSen")
import requests
from bs4 import BeautifulSoup



def get_latest_sarkari_jobs():
    URL = "https://sarkariresult.com.cm/"
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    latest_jobs_p = soup.find("p", string=lambda text: text and "Latest Jobs" in text)

    if latest_jobs_p:
        job_list = latest_jobs_p.find_next("ul", class_=["wp-block-latest-posts_list", "6colm_box", "wp-block-latest-posts"])
        if job_list:
            jobs = job_list.find_all("a", class_="wp-block-latest-posts__post-title")
            job_output = ""
            for job in jobs[:10]:  # limit to first 10 jobs if too many
                job_output += f"{job.text.strip()}:\n{job['href']}\n\n"
            return job_output.strip()
        else:
            return "No job list found after 'Latest Jobs'."
    else:
        return "'Latest Jobs' section not found."# URL = "https://sarkariresult.com.cm/"  # Change if job listings are on a subpage
# HEADERS = {
#     "User-Agent": "Mozilla/5.0"
# }

# response = requests.get(URL, headers=HEADERS)
# soup = BeautifulSoup(response.content, "html.parser")

# # Step 1: Find the <p> tag that contains "Latest Jobs"
# latest_jobs_p = soup.find("p", string=lambda text: text and "Latest Jobs" in text)

# if latest_jobs_p:
#     # Step 2: Find the next <ul> that comes after this <p>
#     job_list = latest_jobs_p.find_next("ul", class_=["wp-block-latest-posts_list", "6colm_box", "wp-block-latest-posts"])
    
#     if job_list:
#         jobs = job_list.find_all("a", class_="wp-block-latest-posts__post-title")
#         for job in jobs:
#             print(job.text.strip(), "-", job['href'])
#     else:
#         print("Could not find <ul> after 'Latest Jobs' <p> tag.")
# else:
#     print("Could not find 'Latest Jobs' <p> tag.")


# Look for all job links inside the post list container
# job_list = soup.find("ul", class_=["wp-block-latest-posts_list", "6colm_box", "wp-block-latest-posts"])
# if not job_list:
#     print("Job list not found. Check HTML structure or class name.")
#     exit()

# jobs = job_list.find_all("a", class_="wp-block-latest-posts__post-title")

# for job in jobs:
#     title = job.get_text(strip=True)
#     link = job.get("href")
#     print(f"{title} - {link}")
