from requests import get
from bs4 import BeautifulSoup
import urllib
from selenium import webdriver
import re
import pandas as pd

def save_jobs_to_excel(jobs_list, filename):
    jobs = pd.DataFrame(jobs_list)
    jobs.to_excel(filename)

def find_jobs_from_indeed(search, location, desired_characs, fromage='last', sort='relevance', filename="results.xlsx"):
    """
    Searches Indeed for jobs and saves the results to an Excel file.

    Parameters:
    - search (str): Job title, keywords, or company.
    - location (str): Geographic location to filter job listings.
    - desired_characs (list of str): Characteristics to extract ('title', 'company', 'links', 'date_listed', 'salary').
    - fromage (str, optional): Age of listings ('1', '3', '7', '14', or 'last'). Default is 'last'.
    - sort (str, optional): Sort order ('relevance' or 'date'). Default is 'relevance'.
    - filename (str, optional): Name of the output Excel file. Default is 'results.xlsx'.
    
    Returns:
    None

    The function writes output to an Excel file and does not return any value.
    """
    driver = webdriver.Chrome()
    list_of_jobs_ul = get_indeed_soup(search, location, fromage, sort, driver)
    if not list_of_jobs_ul:
        raise Exception(f'NO RESULTS WITH SEARCH "{search}"')
    extracted_info, jobs_list, num_listings = extract_job_information_indeed(list_of_jobs_ul, desired_characs)

    save_jobs_to_excel(jobs_list, filename)
    print(f'{num_listings} new job postings retrieved from Indeed. Stored in {filename}.')
    return extracted_info

def get_indeed_soup(search, location, fromage, sort, driver):
    params = {'q' : search, 'l' : location, 'fromage' : fromage, 'sort' : sort}
    url = ('https://www.indeed.com/jobs?' + urllib.parse.urlencode(params))
    print(f'URL IS {url}')
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    list_of_jobs = soup.select('.css-5lfssm.eu4oa1w0')
    return list_of_jobs if list_of_jobs else None

def extract_job_information_indeed(list_of_jobs, desired_characs):
    cols = desired_characs
    extracted_info = [[] for i in range(len(desired_characs))]

    for job_li in list_of_jobs:
        # need this to filter out divs that arent job postings
        is_a_job = False
        if 'title' in desired_characs:
            titles = extracted_info[desired_characs.index('title')]
            title = extract_job_title_indeed(job_li)
            if title:
                titles.append(title)
                # if the div has a job title, its a job posting
                is_a_job = True
        if 'company' in desired_characs:
            companies = extracted_info[desired_characs.index('company')]
            company = extract_company_indeed(job_li)
            if company:
                companies.append(company)
            elif is_a_job:
                companies.append('N/A')
        if 'date_listed' in desired_characs:
            dates = extracted_info[desired_characs.index('date_listed')]
            date = extract_date_indeed(job_li)
            if date:
                dates.append(date)
            elif is_a_job:
                dates.append('N/A')
        if 'links' in desired_characs:
            links = extracted_info[desired_characs.index('links')]
            link = extract_link_indeed(job_li)
            if link:
                links.append(link)
            elif is_a_job:
                links.append('N/A')
        if 'salary' in desired_characs:
            salaries = extracted_info[desired_characs.index('salary')]
            salary = extract_salary_indeed(job_li)
            if salary:
                salaries.append(salary)
            elif is_a_job:
                salaries.append('N/A')


    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    num_listings = len(extracted_info[0])
    
    return extracted_info, jobs_list, num_listings

def extract_salary_indeed(job_li):
    salary_div = job_li.select_one('.salary-snippet-container div')
    if salary_div:
        return salary_div.text.strip()

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
            if 'Employer' in cleaned_string:
                cleaned_string = cleaned_string[10:]
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
    Retrieves job listings from ZipRecruiter based on search criteria and exports them to an Excel file.

    Parameters:
    - search (str): Search term for job titles, keywords, or companies.
    - location (str): Location to focus the job search.
    - desired_characs (list of str): Job attributes to collect ('title', 'company', 'links', 'type').
    - days (str or int, optional): Number of days to look back for job postings ('30', '10', '5', '1', or 'anytime'). Default is 'anytime'.
    - radius (str or int, optional): Search radius in miles ('5', '10', '25', '50', '100', or 'any'). Default is 'any'.
    - filename (str, optional): File name for the saved Excel results. Default is 'results.xlsx'.

    Returns:
    None

    Saves the job listings to the specified Excel file without returning a value.
    """
    driver = webdriver.Chrome()
    list_of_jobs = get_ziprecruiter_soup(search, location, days, radius, driver)
    extracted_info, jobs_list, num_listings = extract_job_information_ziprecruiter(list_of_jobs, desired_characs)
    save_jobs_to_excel(jobs_list, filename)
    print(f'{num_listings} new job postings retrieved from ZipRecruiter. Stored in {filename}.')
    return extracted_info

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
            is_a_job = False
            job_info = job_article.find('div').find('div')
            if 'title' in desired_characs:
                titles = extracted_info[desired_characs.index('title')]
                title = extract_job_title_ziprecruiter(job_info)
                if title:
                    titles.append(title)
                    is_a_job = True

            if 'company' in desired_characs:
                companies = extracted_info[desired_characs.index('company')]
                company = extract_company_ziprecruiter(job_info)
                if company:
                    companies.append(company)
                elif is_a_job:
                    companies.append('N/A')

            if 'type' in desired_characs:
                types = extracted_info[desired_characs.index('type')]
                type = extract_type_ziprecruiter(job_info)
                if type:
                    types.append(type)
                elif is_a_job:
                    types.append('N/A')

            if 'links' in desired_characs:
                links = extracted_info[desired_characs.index('links')]
                link = extract_link_ziprecruiter(job_info)
                if link:
                    links.append(link)
                elif is_a_job:
                    links.append('N/A')

            if 'salary' in desired_characs:
                salaries = extracted_info[desired_characs.index('salary')]
                salary = extract_salary_ziprecruiter(job_info)
                if salary:
                    salaries.append(salary)
                elif is_a_job:
                    salaries.append('N/A')



        
    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    num_listings = len(extracted_info[0])
    
    return extracted_info, jobs_list, num_listings

def extract_salary_ziprecruiter(job_info):
    pattern = re.compile(r'\s/\s(?:yr|hr)')
    salary = job_info.find('p', text=pattern)
    return salary.text

def extract_link_ziprecruiter(job_info):
    link_elements = job_info.select('a')
    if link_elements:
        return link_elements[0]['href']

def extract_type_ziprecruiter(job_info):
    pattern = re.compile(r'^(Per diem|Full-time|Temporary|Contract|Part-time)$')
    type = job_info.find('p', text=pattern)
    if type:
        return type.text

def extract_job_title_ziprecruiter(job_info):
    job_title_elements = job_info.select('h2')
    if job_title_elements:
        return job_title_elements[0].text.strip()
    
def extract_company_ziprecruiter(job_info):
    companies_a_tag = job_info.select('h2 + div a')
    if companies_a_tag:
        return companies_a_tag[0].text.strip()


# desired_characs = ['title', 'company', 'links', 'date_listed', 'salary']
# extracted_info = find_jobs_from_indeed('engineer', 'brooklyn', desired_characs, 'last', 'date')

# desired_characs = ['title', 'company', 'links', 'type', 'salary']
# extracted_info = find_jobs_from_ziprecruiter('engineer', 'brooklyn', desired_characs, 5, 10)
    

# print('cols is ', cols)
# print('extracted info is ', extracted_info)
# print(f'titles are {extracted_info[0]}')
# print(f'len of titles is {len(extracted_info[0])}')
# print(f'companies are {extracted_info[1]}')
# print(f'len of companies is {len(extracted_info[1])}')
# print(f'len of links is {len(extracted_info[2])}')
# print(f'len of types is {len(extracted_info[3])}')

# print(f'len of dates is {len(extracted_info[3])}')
# print(f'len of salaries is {len(extracted_info[4])}')
# print(extracted_info[2])
# print(extracted_info[4])