from playwright.sync_api import sync_playwright
import pandas as pd
import time, sqlite3

def create_school(con, website):
    """
    Create a new school into the schools table
    :param conn:
    :param project:
    """
    sql = ''' INSERT INTO school(TimeStamp,Website,Content)
              VALUES(?,?,?) '''
    cur = con.cursor()
    cur.execute(sql, website)
    con.commit()
    return None

con = sqlite3.connect("schoolwebsites.db")
SchoolList = pd.read_csv('K12SIX-SchoolDistrictswIncidents.csv')
for website in SchoolList['Website']:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        date_time = time.strftime("%Y-%m-%d %H:%M:%S")
        page.goto(website)
        school = (date_time, website, page.content())
        create_school(con, school)
        browser.close()