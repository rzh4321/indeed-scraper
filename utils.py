from requests import get
from bs4 import BeautifulSoup
import urllib
import cloudscraper
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os

def find_jobs_from_indeed(search, location, desired_characs, fromage='last', sort='relevance', filename="results.xls"):
    """
    desired_characs = ['titles', 'companies', 'links', 'date_listed', 'type']
    fromage = 1,3,7,14
    sort = relevance,date
    """
    list_of_jobs_ul = get_indeed_soup(search, location, fromage, sort)
    extract_job_information_indeed(list_of_jobs_ul, desired_characs)

def get_indeed_soup(search, location, fromage, sort):
    params = {'q' : search, 'l' : location, 'fromage' : fromage, 'sort' : sort}
    url = ('https://www.indeed.com/jobs?' + urllib.parse.urlencode(params))
    scraper = cloudscraper.create_scraper()
    page = scraper.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    list_of_jobs = soup.select('#mosaic-provider-jobcards ul')[0]
    return list_of_jobs

def extract_job_information_indeed(list_of_jobs_ul, desired_characs):
    for job_li in list_of_jobs_ul:
        title = extract_job_title_indeed(job_li)
        if title:
            print(title)

def extract_job_title_indeed(job_li):
    job_title_elements = job_li.select('.jobTitle span')
    if job_title_elements:
        return job_title_elements[0].text.strip()


## ==========================================================================================
def find_jobs_from_ziprecruiter(search, location, desired_characs, days='anytime', radius='any', filename="results.xls"):
    """
    desired_characs = ['titles', 'companies', 'links', 'type']
    days=30,10,5,1
    radius=5,10,25,50,100
    """
    location_of_driver = os.getcwd()
    driver = webdriver.Chrome()
    list_of_jobs = get_ziprecruiter_soup(search, location, days, radius, driver)
    print(f'len of list of jobs if {len(list_of_jobs)}')
    extract_job_information_ziprecruiter(list_of_jobs, desired_characs)


def get_ziprecruiter_soup(search, location, days, radius, driver):
    params = {'search' : search, 'location' : location, 'days' : days, 'radius' : radius}
    url = ('https://www.ziprecruiter.com/jobs-search?' + urllib.parse.urlencode(params))
    print('URL IS: ', url, '\n\n\n')
    driver.get(url)
    # list_of_jobs = driver.find_element_by_css_selector('[data-testid="job-results-root"]')
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    list_of_jobs = soup.find(attrs={"data-testid": "job-results-root"})
    return list_of_jobs

def extract_job_information_ziprecruiter(list_of_jobs, desired_characs):
    for job_div in list_of_jobs:
        job_article = job_div.find('article')
        if job_article:
            job_info = job_article.find('div').find('div')
            title = extract_job_title_ziprecruiter(job_info)
            if title:
                print(title)
            else:
                print('NO TITLE. job_div is ', job_div, '==================================================================\n\n')

def extract_job_title_ziprecruiter(job_info):
    job_title_elements = job_info.select('h2')
    if job_title_elements:
        return job_title_elements[0].text.strip()


desired_characs = ['titles', 'companies', 'links', 'date_listed']
# find_jobs_from_indeed('indeed', 'engineer', 'brooklyn', desired_characs)
find_jobs_from_ziprecruiter('engineer', 'brooklyn', desired_characs)