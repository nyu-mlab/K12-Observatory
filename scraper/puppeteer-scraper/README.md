# Scraper based on the Puppeteer headless browser.

Owner: Spriha

Recommended code base:
https://github.com/nyu-mlab/k12-school-security-privacy/blob/main/sqlite_school_scraper/src/scraper.py

Objectives: Given the K12 district websites in /raw-input-data, the scraper visits all the home pages and subsequent pages using the Puppeteer headless browser.

Outputs
`/shared/tim/puppeteer-scraper/raw-results/[date]/[district_name]/[pages].db` (as SQLite format)
