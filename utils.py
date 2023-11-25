from requests import get
from bs4 import BeautifulSoup
import urllib
import cloudscraper

def find_jobs_from(website, search, location, desired_characs, fromage='last', sort='relevance', filename="results.xls"):
    """
    desired_characs = ['titles', 'companies', 'links', 'date_listed']
    fromage = 1,3,7,14,last
    sort = relevance,date
    """
    if website.lower() == 'indeed':
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

desired_characs = ['titles', 'companies', 'links', 'date_listed']
find_jobs_from('indeed', 'engineer', 'brooklyn', desired_characs)