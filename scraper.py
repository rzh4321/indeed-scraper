from requests import get
from bs4 import BeautifulSoup
import urllib
import cloudscraper
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
import os
import re
import pandas as pd

def find_jobs_from_indeed(search, location, desired_characs, fromage='last', sort='relevance', filename="results.xlsx"):
    """
    desired_characs = ['title', 'company', 'links', 'date_listed', 'type']
    fromage = 1,3,7,14
    sort = relevance,date
    """
    driver = webdriver.Chrome()
    list_of_jobs_ul = get_indeed_soup(search, location, fromage, sort, driver)
    if not list_of_jobs_ul:
        raise Exception(f'NO RESULTS WITH SEARCH "{search}"')
    extracted_info, jobs_list, num_listings = extract_job_information_indeed(list_of_jobs_ul, desired_characs)
    titles, companies, links, dates = extracted_info[0], extracted_info[1], extracted_info[2], extracted_info[3]
    values_set = {len(titles), len(companies), len(links), len(dates)}
    # make sure each job has all the requested info
    while len(values_set) != 1:
        extracted_info, jobs_list, num_listings = extract_job_information_indeed(list_of_jobs_ul, desired_characs)
        titles, companies, dates = extracted_info[0], extracted_info[1], extracted_info[3]
        values_set = {len(titles), len(companies), len(links), len(dates)}

    save_jobs_to_excel(jobs_list, filename)
    print(f'{num_listings} new job postings retrieved from Indeed. Stored in {filename}.')
    return extracted_info

def save_jobs_to_excel(jobs_list, filename):
    jobs = pd.DataFrame(jobs_list)
    jobs.to_excel(filename)

def get_indeed_soup(search, location, fromage, sort, driver):
    params = {'q' : search, 'l' : location, 'fromage' : fromage, 'sort' : sort}
    url = ('https://www.indeed.com/jobs?' + urllib.parse.urlencode(params))
    print(f'URL IS {url}')
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    # scraper = cloudscraper.create_scraper()
    # page = scraper.get(url)
    # soup = BeautifulSoup(page.text, "html.parser")
    #list_of_jobs = soup.select_one('#mosaic-provider-jobcards > ul')
    list_of_jobs = soup.select('.css-5lfssm.eu4oa1w0')
    return list_of_jobs if list_of_jobs else None

def extract_job_information_indeed(list_of_jobs, desired_characs):
    cols = desired_characs
    extracted_info = [[] for i in range(len(desired_characs))]

    for job_li in list_of_jobs:
        if 'title' in desired_characs:
            titles = extracted_info[desired_characs.index('title')]
            title = extract_job_title_indeed(job_li)
            if title:
                titles.append(title)
        if 'company' in desired_characs:
            companies = extracted_info[desired_characs.index('company')]
            company = extract_company_indeed(job_li)
            if company:
                companies.append(company)
        if 'date_listed' in desired_characs:
            dates = extracted_info[desired_characs.index('date_listed')]
            date = extract_date_indeed(job_li)
            if date:
                dates.append(date)
        if 'links' in desired_characs:
            links = extracted_info[desired_characs.index('links')]
            link = extract_link_indeed(job_li)
            if link:
                links.append(link)


    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    num_listings = len(extracted_info[0])
    
    return extracted_info, jobs_list, num_listings

def extract_link_indeed(job_li):
    base_url = 'https://www.indeed.com'
    link = job_li.select_one('.jobTitle a')
    if link:
        relative_url = link['href']
        absolute_url = urllib.parse.urljoin(base_url, relative_url)
        return absolute_url



def extract_date_indeed(job_li):
    date = job_li.select_one('.date')
    pattern = r"(Posted|Active)"
    if date:
        match = re.search(pattern, date.text)
        
        if match:
            parts = date.text.split(match.group(1))
            cleaned_string = ' '.join(parts).strip()
            return cleaned_string


def extract_job_title_indeed(job_li):
    job_title_elements = job_li.select('.jobTitle span')
    if job_title_elements:
        return job_title_elements[0].text.strip()
    
def extract_company_indeed(job_li):
    company_elements = job_li.select('[data-testid="company-name"]')
    if company_elements:
        return company_elements[0].text.strip()


## ==========================================================================================
def find_jobs_from_ziprecruiter(search, location, desired_characs, days='anytime', radius='any', filename="results.xlsx"):
    """
    desired_characs = ['title', 'company', 'links', 'type']
    days=30,10,5,1
    radius=5,10,25,50,100
    """
    driver = webdriver.Chrome()
    list_of_jobs = get_ziprecruiter_soup(search, location, days, radius, driver)
    extract_job_information_ziprecruiter(list_of_jobs, desired_characs)


def get_ziprecruiter_soup(search, location, days, radius, driver):
    params = {'search' : search, 'location' : location, 'days' : days, 'radius' : radius}
    url = ('https://www.ziprecruiter.com/jobs-search?' + urllib.parse.urlencode(params))
    print('URL IS: ', url, '\n\n\n')
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    list_of_jobs = soup.find(attrs={"data-testid": "job-results-root"})
    return list_of_jobs

def extract_job_information_ziprecruiter(list_of_jobs, desired_characs):
    cols = desired_characs
    extracted_info = [[] for i in range(len(desired_characs))]

    for job_div in list_of_jobs:
        job_article = job_div.find('article')
        if job_article:
            job_info = job_article.find('div').find('div')
            if 'title' in desired_characs:
                titles = extracted_info[desired_characs.index('title')]
                title = extract_job_title_ziprecruiter(job_info)
                if title:
                    titles.append(title)
            if 'company' in desired_characs:
                companies = extracted_info[desired_characs.index('company')]
                company = extract_company_ziprecruiter(job_info)
                if company:
                    companies.append(company)

        
    # print('cols is ', cols)
    # print('extracted info is ', extracted_info)
    print(f'titles are {extracted_info[0]}')
    print(f'len of titles is {len(extracted_info[0])}')
    print(f'companies are {extracted_info[1]}')
    print(f'len of companies is {len(extracted_info[1])}')
        

def extract_job_title_ziprecruiter(job_info):
    job_title_elements = job_info.select('h2')
    if job_title_elements:
        return job_title_elements[0].text.strip()
    
def extract_company_ziprecruiter(job_info):
    companies_a_tag = job_info.select('h2 + div a')
    if companies_a_tag:
        return companies_a_tag[0].text.strip()


desired_characs = ['title', 'company', 'links', 'date_listed']
extracted_info = find_jobs_from_indeed('engineer', 'brooklyn', desired_characs)

#find_jobs_from_ziprecruiter('engineer', 'brooklyn', desired_characs)
    

# print('cols is ', cols)
# print('extracted info is ', extracted_info)
# print(f'titles are {extracted_info[0]}')
print(f'len of titles is {len(extracted_info[0])}')
# print(f'companies are {extracted_info[1]}')
print(f'len of companies is {len(extracted_info[1])}')
print(f'len of links is {len(extracted_info[2])}')

print(f'len of dates is {len(extracted_info[3])}')