# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import pymysql
from selenium.webdriver import ActionChains


def connect_sql():
    db = pymysql.connect(
        host='localhost',
        port=1108,
        user='root',
        passwd='root',
        db='goal',
        charset='utf8'
    )
    return db


def write_a_unit(data_unit):
    database = connect_sql()
    cursor = database.cursor()
    print (data_unit)
    sql = "INSERT INTO reviews(app_name, comment, date, rating, helpful) " \
          "VALUES('%s', '%s', '%s', '%d', '%d')" % (data_unit['name'], data_unit['content'], data_unit['date'],
                                                    data_unit['rating'], data_unit['helpful'])
    try:
        cursor.execute(sql)
        database.commit()
    except:
        database.rollback()
    database.close()


def getDriver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    # prefs = {"profile.managed_default_content_settings.images": 2,'permissions.default.stylesheet':2}
    # chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=r'chromedriver\chromedriver.exe')
    return driver


def get_date(date):
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
             'November', 'December']
    s = date.split()
    m_count = 1
    for m in month:
        if s[0] == m:
            break
        m_count = m_count + 1
    d_count = s[1].replace(',', '')
    d = ''
    if len(d_count) == 1:
        d = '0' + d_count
    else:
        d = d_count
    y = s[2]
    m = str(m_count)
    if len(m) == 1:
        m = '0' + m
    return y + '-' + m + '-' + d


def get_star(star):
    s_star = star[6:7]
    i_star = int(s_star)
    return i_star


def get_helpful(helpful):
    try:
        i_helpful = int(helpful)
    except:
        i_helpful = 0
    return i_helpful


# Crawl reviews according to Newest
def choosePageRule(driver):
    try:
        # Expand the drop-down box
        # driver.find_element_by_xpath("//div[@class='jgvuAb Eic1df']").click()
        show_div = driver.find_elements_by_xpath("//span[@class = 'DPvwYc']")
        show_div[0].click()
        time.sleep(3)
        # find and click Newest button
        ele = driver.find_element_by_xpath("//div[@class='OA0qNb ncFHed']")
        ActionChains(driver).move_to_element_with_offset(ele, 10, 40).click().perform()
    except:
        print("select \"Most relevant\"")
    time.sleep(2)
    pass


def getReview(driver, page_num):
    js = "window.scrollTo(0,document.body.scrollHeight)"
    t = 2
    time.sleep(3)
    choosePageRule(driver)
    for i in range(page_num):
        print ("Crawling page %d" % (i,))
        driver.execute_script(js)  # Scroll to the bottom of the page
        time.sleep(t)
        button = driver.find_elements_by_xpath("//span[@class = 'RveJvd snByac']")  # "show more" button
        if len(button) > 0:
            button[0].click()  # click the "show more" button
            time.sleep(t)
    name_div = driver.find_element_by_xpath("//h1[@class='AHFaub']/span")
    full_div = driver.find_elements_by_xpath("//div[@class='zc7KVe']")
    for div in full_div:
        t = div.find_element_by_xpath(".//span[@jsname='fbQN7e']")
        driver.execute_script("arguments[0].style.display = 'block'", t)
        t1 = div.find_element_by_xpath(".//span[@jsname='bN97Pc']")
        # reviewer_name = div.find_element_by_xpath(".//span[@class='X43Kjb']")
        date = div.find_element_by_xpath(".//span[@class='p2TkOb']")
        rating = div.find_element_by_xpath(".//div[@class='pf5lIe']/div").get_attribute("aria-label")
        helpful = div.find_element_by_xpath(".//div[@class='jUL89d y92BAb']")
        standard_helpful = get_helpful(helpful.text)
        standard_date = get_date(date.text)
        standard_rating = get_star(rating)
        review = ''
        if t.text == '':
            review = t1.text
        else:
            review = t.text
        review = review.replace("'", "''")
        review_unit ={'name': name_div.text, 'content': review, 'date': standard_date, 'rating': standard_rating, 'helpful': standard_helpful}
        # write_a_unit(review_unit)
        print (review_unit)


if __name__ == "__main__":
    app_url = "https://play.google.com/store/apps/details?id=com.mapswithme.maps.pro&hl=en&showAllReviews=true"
    page_num = 2
    driver = getDriver()
    driver.get(app_url)
    time.sleep(3)
    getReview(driver, page_num)