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

To use this module, import the scraper.py file and call either the function "find_jobs_from_indeed()" or "find_jobs_from_ziprecruiter(). 

find_jobs_from_indeed() take in several arguments: the search query, location, an array containing all items you want included in the result, date posted, and sort. The "date posted" and "sort" filters are turned off by default. See function comments for the values it could take.

find_jobs_from_ziprecruiter() take in several arguments: the search query, location, an array containing all items you want included in the result, date posted, and radius. The "date posted" and "radius" filters are turned off by default. See function comments for the values it could take.