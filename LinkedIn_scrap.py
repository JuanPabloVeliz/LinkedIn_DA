import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

## Job position to search
position = "Data Analyst"

## Data to format link to linkedin model

position = position.replace(' ', "%20")

countries_id = {
    "Argentina": "100446943", 
    "Brazil": "106057199",
    "Colombia": "100876405",
    "México": "103323778",
    "Chile": "104621616",
    "USA": "103644278",
    "Uruguay": "100867946",
    "Paraguay": "104065273",
    "Bolivia": "104379274",
    "Ecuador": "106373116",
    "Perú": "102927786"
    }

onsite_remote = {
    "Onsite": "1",
    "Remote": "2",
    "Hibrid": "3"
    }


## Create csv file to output scrape
with open("Datasets/linkedin-jobs.csv", mode="w", encoding="UTF-8") as file:
    writer = csv.writer(file)
    
    writer.writerow(["country", "title", "company", "location", "onsite_remote", "salary",
                     "description", "criteria", "posted_date","link"])

    for country_name, country_id in countries_id.items():
        local = country_id
        

        for wfh_type, wfh_id in onsite_remote.items():
            wfh = wfh_id

            raw_link = f"https://www.linkedin.com/jobs/search/?f_WT={wfh}&geoId={local}&keywords={position}&refresh=true&sortBy=R&start="
            #https://www.linkedin.com/jobs/search/?f_WT=1&geoId=100446943&keywords=data%20analyst&refresh=true&sortBy=R&start=
            job_id_list = []
            
            ## Scrape listed jobs
            def scrape_page(raw_link, job_count, page_count):

                page = raw_link + str(job_count)
                response_jobs_list = requests.get(page)
                soup_jobs_list = BeautifulSoup(response_jobs_list.content, "html.parser")

                # Find all <div> tag with the specified CSS class "title" 
                jobs = soup_jobs_list.find_all(
                    "div", 
                    class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card"
                    )
                print("Scraping ", wfh_type, "jobs in ", country_name, ", page ", page_count, ". Please wait.")
                
                
                # Loop jobs list and extract data
                for job in jobs:

                    job_link = job.find("a", class_="base-card__full-link")["href"]

                    job_id = job_link[job_link.find("?")-10:job_link.find("?")]

                    if job_id in job_id_list:
                        continue

                    job_id_list.append(job_id)

                    job_title = job.find("h3", class_="base-search-card__title").text.strip()
                    job_company = job.find("h4", class_="base-search-card__subtitle").text.strip()
                    job_location = job.find("span", class_="job-search-card__location").text.strip()
 

                    job_date = job.find(
                        "time", class_="job-search-card__listdate")["datetime"] if job.find("time", class_="job-search-card__listdate") is not None else job.find(
                        "time", class_="job-search-card__listdate--new")["datetime"]

                    job_salary= job.find(
                        "span", class_="job-search-card__salary-info").text.strip() if job.find("span", class_="job-search-card__salary-info") is not None else "N/A" 
                    
                    ## Go to job link and extract specific data
                    response_job = requests.get(job_link)
                    soup_job = BeautifulSoup(response_job.content, "html.parser")

                    job_description = soup_job.find("div", class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5").text.strip() if soup_job.find("div", class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5") is not None else "N/A"

                    job_criteria = []
                    
                    criteria_items = soup_job.find_all("li", class_="description__job-criteria-item")

                    for item in criteria_items:
                        item_name = item.find("h3", class_="description__job-criteria-subheader").text.strip()
                        item_def = item.find("span", class_="description__job-criteria-text description__job-criteria-text--criteria").text.strip()
                        job_criteria.append({item_name:item_def})

                    writer.writerow([country_name, job_title, job_company, job_location, wfh, job_salary,
                                job_description, job_criteria, job_date, job_link])
                    
                    job_count += 1
                    
                print(job_count," jobs data retrieved.")
                
                page_count += 1
                if job_count < 100 and page_count < 51:
                    scrape_page(raw_link, job_count, page_count)
            
            scrape_page(raw_link, 0, 1)

print("Done.")

#----------------------#

## Model to scrap
#with open(r"Scrap Page Views/job-list.html", mode='w', encoding="utf-8") as job_list:
#    job_list.write(str(soup))
#    job_list.close()

#response_job = requests.get(r"https://ar.linkedin.com/jobs/view/data-analyst-at-bbva-en-argentina-3424412411?refId=bc5mnZu%2FXTh3D%2FXkXkzN%2BQ%3D%3D&trackingId=L8IQnzsnpyaF9GjEiIsDLQ%3D%3D&position=1&pageNum=0&trk=public_jobs_jserp-result_search-card")
#soup_job = BeautifulSoup(response_job.content, "html.parser")
#
#with open(r"Scrap Page Views/job.html", mode='w', encoding="utf-8") as job:
#    job.write(str(soup_job))
#    job.close()
