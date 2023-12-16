from requests import get
from bs4 import BeautifulSoup
import urllib
import cloudscraper
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
import os
import re

def find_jobs_from_indeed(search, location, desired_characs, fromage='last', sort='relevance', filename="results.xls"):
    """
    desired_characs = ['title', 'company', 'links', 'date_listed', 'type']
    fromage = 1,3,7,14
    sort = relevance,date
    """
    list_of_jobs_ul = get_indeed_soup(search, location, fromage, sort)
    if not list_of_jobs_ul:
        raise Exception(f'NO RESULTS WITH SEARCH "{search}"')
    return extract_job_information_indeed(list_of_jobs_ul, desired_characs)

def get_indeed_soup(search, location, fromage, sort):
    params = {'q' : search, 'l' : location, 'fromage' : fromage, 'sort' : sort}
    url = ('https://www.indeed.com/jobs?' + urllib.parse.urlencode(params))
    print('url is ', url)
    scraper = cloudscraper.create_scraper()
    page = scraper.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    list_of_jobs = soup.select('#mosaic-provider-jobcards ul')
    return list_of_jobs[0] if list_of_jobs else None

def extract_job_information_indeed(list_of_jobs_ul, desired_characs):
    cols = desired_characs
    extracted_info = [[] for i in range(len(desired_characs))]



    for job_li in list_of_jobs_ul:
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

    return extracted_info


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
        print(job_title_elements[0].text.strip())
        return job_title_elements[0].text.strip()
    
def extract_company_indeed(job_li):
    company_elements = job_li.select('[data-testid="company-name"]')
    if company_elements:
        return company_elements[0].text.strip()


## ==========================================================================================
def find_jobs_from_ziprecruiter(search, location, desired_characs, days='anytime', radius='any', filename="results.xls"):
    """
    desired_characs = ['title', 'company', 'links', 'type']
    days=30,10,5,1
    radius=5,10,25,50,100
    """
    driver = webdriver.Chrome()
    list_of_jobs = get_ziprecruiter_soup(search, location, days, radius, driver)
    print(f'len of list of jobs if {len(list_of_jobs)}')
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
titles, companies, dates = extracted_info[0], extracted_info[1], extracted_info[3]
while len(titles) != len(companies) or len(companies) != len(dates):
    extracted_info = find_jobs_from_indeed('engineer', 'brooklyn', desired_characs)
    titles, companies, dates = extracted_info[0], extracted_info[1], extracted_info[3]

#find_jobs_from_ziprecruiter('engineer', 'brooklyn', desired_characs)
    

# print('cols is ', cols)
# print('extracted info is ', extracted_info)
# print(f'titles are {extracted_info[0]}')
print(f'len of titles is {len(extracted_info[0])}')
# print(f'companies are {extracted_info[1]}')
print(f'len of companies is {len(extracted_info[1])}')
print(f'len of dates is {len(extracted_info[3])}')