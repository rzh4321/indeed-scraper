## Jobs Scraper

The module scraper.py enables you to web scrape job postings from indeed.com or ziprecruiter.com. Both require the packages Beautiful Soup and Selenium These can be installed as follows:

```bash
pip install beautifulsoup4
pip install selenium
```

To install all packages:

```bash
pip install -r requirements.txt
```

To use this module, import the scraper.py file and call either the function "find_jobs_from_indeed()" or "find_jobs_from_ziprecruiter()". 

find_jobs_from_indeed() take in several arguments: the search query, location, an array containing all items you want included in the result, date posted, and sort. The "date posted" and "sort" filters are turned off by default. For the array parameter, see function documentation for the values it could take.

find_jobs_from_ziprecruiter() take in several arguments: the search query, location, an array containing all items you want included in the result, date posted, and radius. The "date posted" and "radius" filters are turned off by default. For the array parameter, see function documentation for the values it could take.

## Examples
```python
"""
Find jobs in ZipRecruiter with search "engineer" in location "brooklyn". The job 
title, company name, job link, job type, and salary are extracted. Show only 
postings within the last 5 days and located within 10 miles.
"""
desired_characs = ['title', 'company', 'links', 'type', 'salary']
extracted_info = find_jobs_from_ziprecruiter('engineer', 'brooklyn', desired_characs, 5, 10)

"""
Find jobs in Indeed with search "engineer" in location "brooklyn". The job title, 
company name, job link, post date, and salary are extracted. The age of listing 
is "last" (default value). The sort parameter is "date" (default is "relevance").
"""
desired_characs = ['title', 'company', 'links', 'date_listed', 'salary']
extracted_info = find_jobs_from_indeed('engineer', 'brooklyn', desired_characs, 'last', 'date')
```