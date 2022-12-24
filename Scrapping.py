import csv
import requests
from bs4 import BeautifulSoup

# Links para extraer las búsquedas de cada país
links = {
        "Argentina":
            {
            "Presencial": "https://www.linkedin.com/jobs/search/?currentJobId=3409620559&f_WT=1&geoId=100446943&keywords=data%20analyst&location=Argentina&refresh=true&sortBy=R&sortBy=R&start=",
            "Remoto":"https://www.linkedin.com/jobs/search/?currentJobId=3410677451&f_WT=2&geoId=100446943&keywords=data%20analyst&location=Argentina&refresh=true&sortBy=R&start=",
            "Híbrido": "https://www.linkedin.com/jobs/search/?currentJobId=3402549146&f_WT=3&geoId=100446943&keywords=data%20analyst&location=Argentina&refresh=true&sortBy=R&start="}
        }

# Función para scrapping
def create_job_csv(country_links: dict, country: str):
    # Crear csv para guardar los datos
    with open('Datasets/linkedin-jobs-'+country+'.csv', mode='w', encoding='UTF-8') as file:
        writer = csv.writer(file)
        # Columnas extraídas
        writer.writerow(['title', 'company', 'description', 'onsite_remote',
                        'salary', 'location', 'criteria', 'posted_date', 'link'])

        # Pasando de página
        def linkedin_scraper(webpage, page_number, onsite_remote):
            count = 0
            next_page = webpage + str(page_number)
            response = requests.get(str(next_page))
            soup = BeautifulSoup(response.content, 'html.parser')
            
            jobs = soup.find_all(
                'div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
            for job in jobs:
                job_criteria = []
                job_title = job.find(
                    'h3', class_='base-search-card__title').text.strip()
                job_company = job.find(
                    'h4', class_='base-search-card__subtitle').text.strip()
                job_location = job.find(
                    'span', class_='job-search-card__location').text.strip()
                job_datetime = job.find(
                    'time', class_='job-search-card__listdate')['datetime'] if job.find(
                    'time', class_='job-search-card__listdate') is not None else job.find(
                    'time', class_='job-search-card__listdate--new')['datetime']
                job_salary = job.find('span', class_='job-search-card__salary-info').text.strip(
                ) if job.find('span', class_='job-search-card__salary-info') is not None else "NaN"

                job_link = job.find('a', class_='base-card__full-link')['href']
                resp = requests.get(job_link)
                sp = BeautifulSoup(resp.content, 'html.parser')

                # Save requests as html pages to help view classes for scraping
                #if count == 0 and country == 'africa':
                #    with open('scrap_page_view/job-list.html', mode='w', encoding="utf-8") as job_list:
                #        job_list.write(str(response.content))
                #        job_list.close()
                #    with open('scrap_page_view/job.html', mode='w', encoding="utf-8") as job_detail:
                #        job_detail.write(str(resp.content))
                #        job_detail.close()
                #count += 1

                job_desc = sp.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5').text.strip(
                ) if sp.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5') is not None else "Nan"

                criteria = sp.find_all(
                    'li', class_='description__job-criteria-item')
                for criterion in criteria:
                    feature = criterion.find(
                        'h3', class_='description__job-criteria-subheader').text.strip()
                    value = criterion.find(
                        'span', class_='description__job-criteria-text description__job-criteria-text--criteria').text.strip()
                    job_criteria.append({feature: value})

                writer.writerow([job_title, job_company, job_desc, onsite_remote, job_salary,
                                job_location, job_criteria, job_datetime, job_link])
                print(' Data updated')

            if page_number < 500:
                # Pasar a la página siguiente
                page_number = page_number + 25
                linkedin_scraper(webpage, page_number, onsite_remote)

        for work_type in country_links:
            linkedin_scraper(country_links[work_type], 0, work_type)

for country in links:
    create_job_csv(links[country], country)

