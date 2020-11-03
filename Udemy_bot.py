from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import requests,threading,glob
import bs4 as bs

def is_rate_valid(element):
    '''
    Finds if the current course meets the conditions
    :param element: the element of the relevant course
    :return: if the current course meets the conditions
    '''

    rate=element.find("div",{"class":"coupon-details-extra-3"}).find_all('p')[2].text
    rate=rate.split('Rate: ')[1]
    stars=float(rate.split('/')[0])
    people=int(rate.split('/')[1])
    return stars>=4.2 and people>=200

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

    link1=element.find("a", {"class": "button-icon"})['href']
    source = requests.get(link1)
    soup = bs.BeautifulSoup(source.content, 'lxml')
    return soup.find("a",{"class":"button-icon"})['href']

def add_links(soup):
    '''
    Cheack if the course meets the conditions
    :param soup:  relevent BeautifulSoup object
    :return:
    '''
    for i in soup.find_all("div", {"class": "col-md-4 col-sm-6"}):
        if is_valid_coupon(i):
            if is_valid_coupon(i) and is_rate_valid(i):
                potential_urls.append(get_udemy_link(i))


def find_potential_urls():
    '''
    Finds all relevent courses
    '''
    print("Looking for potential links")
    for l in range(1, 217): #might needed pages update
        url = "https://www.udemyfreebies.com/course-category/it-and-software/" + str(l)
        source = requests.get(url)
        soup = bs.BeautifulSoup(source.content, 'lxml')
        while (threading.activeCount() >= 100):
            sleep(1)
        threading.Thread(target=add_links, args=(soup,)).start()

    # you can add more categorys
    for l in range(1, 305): #might needed pages update
        url = "https://www.udemyfreebies.com/course-category/development/" + str(l)
        source = requests.get(url)
        soup = bs.BeautifulSoup(source.content, 'lxml')
        while (threading.activeCount() >= 100):
            sleep(1)
        threading.Thread(target=add_links, args=(soup,)).start()

    while (threading.activeCount() != 1):
        sleep(1)


def click():
    '''
    clicks on enroll button
    '''

    try:
        browser.find_element_by_xpath("//div[contains(@class,'ud-component--course-landing-page-udlite--buy-button-cacheable')]").click()
        sleep(1)
    except:
        pass
    try:
        browser.find_element_by_class_name("slider-menu__buy-button").find_element_by_tag_name("button").click()
        sleep(2)
        browser.find_element_by_class_name("styles--complete-payment-container--3Jazs").find_element_by_tag_name("button").click()
        sleep(1)
    except:
        pass


if __name__ == '__main__':

    potential_urls = []
    if glob.glob("urls.txt"):
        with open("urls.txt") as f:
            potential_urls=f.read().split("\n")
    else:
        find_potential_urls()

    ###################
    # save urls
    f = open("urls.txt", "a")
    for u in potential_urls:
        f.write(u + "\n")
    f.close()
    ###################

    print("found ", len(potential_urls), " urls")
    options = Options()
    # options.add_argument("user-data-dir=/tmp/tarun")
    browser = webdriver.Chrome(chrome_options=options)
    browser.get("https://www.udemy.com/join/login-popup/")
    sleep(1)
    browser.find_element_by_id("email--1").send_keys("EMAIL")
    sleep(1)
    browser.find_element_by_id("id_password").send_keys("PASSWORD")
    sleep(1)
    browser.find_element_by_id("submit-id-submit").click()

    print("saving the courses to your udemy account")
    course_count=0
    for url in potential_urls:
        try:
            browser.get(url)
            sleep(2)
            click()
            course_count+=1
        except:
            pass
    print("Done added "+str(course_count)+" courses")
    browser.close()
