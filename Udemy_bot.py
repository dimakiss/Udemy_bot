from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import requests, threading,glob,sys
import bs4 as bs

### CONFIG ###

categories_list = [
    'business',
    'design',
    'development',
    'finance-and-accounting',
    'health-and-fitness',
    'it-and-software',
    'lifestyle',
    'marketing',
    'music',
    'office-productivity',
    'personal-development',
    'photography',
    'photography-and-video',
    'teaching-and-academics'
]
#Personal preference for example
#categories_list=[
#    'development',
#    'it-and-software'
#]
rating_stars = 4.2
rating_people = 200

#### END OF CONFIG ###

def url_is_new(url):
    '''
    Check if the course url is new
    :param url: url of the course
    :return: if the course url is new
    '''
    if url not in enrolled_urls:
        return True

def find_last_page(category):
    '''
    find the last page of the category
    :param category: the category to check
    '''
    url = f"https://www.udemyfreebies.com/course-category/{category}/"
    source = requests.get(url)
    soup = bs.BeautifulSoup(source.content, 'lxml')

    pagination = soup.find("ul", {"class": "theme-pagination"})
    pages = pagination.find_all("li")
    lastpage = int(pages[-2].text) + 1
    return lastpage

def check_category(category, lastpage):
    '''
    Finds course urls from categories
    :param category: the category to check
    :param lastpage: the last page of the category
    '''
    for l in range(1, lastpage):  # might needed pages update
        url = f"https://www.udemyfreebies.com/course-category/{category}/" + str(l)
        source = requests.get(url)
        soup = bs.BeautifulSoup(source.content, 'lxml')
        while (threading.activeCount() >= 100):
            sleep(1)
        threading.Thread(target=add_links, args=(soup,)).start()

def is_rate_valid(element):
    '''
    Finds if the current course meets the conditions
    :param element: the element of the relevant course
    :return: if the current course meets the conditions
    '''

    rate = element.find("div", {"class": "coupon-details-extra-3"}).find_all('p')[2].text
    rate = rate.split('Rate: ')[1]
    stars = float(rate.split('/')[0])
    people = int(rate.split('/')[1])
    return stars >= rating_stars and people >= rating_people


def is_valid_coupon(element):
    '''
    Checks if the coupon is not expired
    :param element: relevant element
    :return: if the coupon is not expired
    '''

    button = element.find("a", {"class": "button-icon"}).text
    return "Expired" not in button


def get_udemy_link(element):
    '''
    Gets the relevent link to the udemy course
    :param element: relevant element
    :return: the relevent link to the udemy course
    '''

    link1 = element.find("a", {"class": "button-icon"})['href']
    source = requests.get(link1)
    soup = bs.BeautifulSoup(source.content, 'lxml')
    return soup.find("a", {"class": "button-icon"})['href']


def add_links(soup):
    '''
    Check if the course meets the conditions
    :param soup:  relevent BeautifulSoup object
    :return:
    '''
    for i in soup.find_all("div", {"class": "col-md-4 col-sm-6"}):
        if is_valid_coupon(i):
            if is_valid_coupon(i) and is_rate_valid(i):
                potential_urls.append(get_udemy_link(i))
                print('\r', len(potential_urls), 'Potential Courses Scraped', end='', flush=True)


def find_potential_urls():
    '''
    Finds all relevent courses
    '''
    print("Looking for potential links")
    for cat in categories_list:
        check_category(cat, find_last_page(cat)) 

    while (threading.activeCount() != 1):
        sleep(1)
    print('\n')


def click():
    '''
    clicks on enroll button
    '''

    try:
        browser.find_element_by_xpath(
            "//div[contains(@class,'ud-component--course-landing-page-udlite--buy-button-cacheable')]").click()
        sleep(1)
    except:
        pass
    try:
        browser.find_element_by_class_name("slider-menu__buy-button").find_element_by_tag_name("button").click()
        sleep(2)
        browser.find_element_by_class_name("styles--complete-payment-container--3Jazs").find_element_by_tag_name(
            "button").click()
        sleep(1)
    except:
        pass


def is_account_exist(email, password):
    '''
    Checks if the credentials are correct
    :param email: users email
    :param password: users password
    :return: if the credentials are correct
    '''

    print("Checking if the email and password are correct")
    options = Options()
    # options.add_argument("--incognito")
    # options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    #browser.set_window_position(5000, 5000) make checking window invisible
    browser.get("https://www.udemy.com/join/login-popup/")
    sleep(1)
    browser.find_element_by_id("email--1").send_keys(email)
    sleep(1)
    browser.find_element_by_id("id_password").send_keys(password)
    sleep(1)
    temp_url = browser.current_url
    browser.find_element_by_id("submit-id-submit").click()
    sleep(4)
    is_exist = temp_url == browser.current_url
    browser.close()
    return is_exist


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Wrong input make sure you type you Email and Password")
        exit()
    elif is_account_exist(sys.argv[1], sys.argv[2]):
        print("There was a problem logging in. Check your email and password or create an account.")
        exit()

    email = sys.argv[1]
    password = sys.argv[2]

    enrolled_urls = []
    potential_urls = []
    if glob.glob("urls.txt"):
        with open("urls.txt") as f:
            enrolled_urls = f.read().split("\n")

    find_potential_urls()
    new_urls = []
    ###################
    # save urls
    f = open("urls.txt", "a")
    for u in potential_urls:
        if url_is_new(u):
            f.write(u + "\n")
            new_urls.append(u)
    f.close()
    ###################

    print("Found", len(new_urls), "new courses")
    options = Options()

    # options.add_argument("user-data-dir=/tmp/tarun")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    browser.get("https://www.udemy.com/join/login-popup/")
    sleep(1)
    browser.find_element_by_id("email--1").send_keys(email)
    sleep(1)
    browser.find_element_by_id("id_password").send_keys(password)
    sleep(1)
    browser.find_element_by_id("submit-id-submit").click()
    
    print("Adding the courses to your udemy account")
    course_count = 0
    for url in new_urls:
        try:
            browser.get(url)
            sleep(2)
            if "Free" in browser.find_element_by_xpath \
                        (
                        "//div[contains(@class, 'price-text--price-part--Tu6MH udlite-clp-discount-price udlite-heading-lg')]") \
                    .find_elements_by_xpath(".//span")[1].text:
                click()
                course_count += 1
        except:
            pass
    print("Done added " + str(course_count) + " courses")
    browser.close()
