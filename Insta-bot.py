import requests
import os
import configparser
import sys
import wget
import autoit
from lxml import html
from bs4 import BeautifulSoup as bs
from time import sleep
from selenium import webdriver

config = configparser.ConfigParser()
config.read('config.ini')

username = config['instagram']['username']
password = config['instagram']['password']
caption = config['instagram']['caption']
image_path = config['instagram']['pictures-folder-path']
postdelay = int(config['instagram']['post-delay'])
chromedriver = config['instagram']['chrome-driver-path']

scrape = config['web-scraping']['scrape-reddit']
reddit = config['web-scraping']['reddit-url']


main_url = "https://www.instagram.com"

mobile_emulation = {"deviceName": "Pixel 2"}
opts = webdriver.ChromeOptions()
opts.add_experimental_option("mobileEmulation", mobile_emulation)

main_url = "https://www.instagram.com"

image_urls = []

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'csv=1; edgebucket=xZW3uNicVrcgvQUq4s; over18=1; reddaid=ZX5YFVMR5TYPNOQB; pc=bk; _recentclicks2=t3_ikpb4a%2Ct3_ilcbbw%2Ct3_imtxs2%2Ct3_imv5n7%2Ct3_iobbw1; loid=00000000007ycpm4q1.2.1599110022644.Z0FBQUFBQmZaNDhhVlNmUkhLWUlkXzA1UUxxZHQ0dEZ1TnhxbDQtaEprU29TY1RaVm5kYlVrLXV6WDN6M3YzTENuaHh1QlNHYW50MzlmZXM2NTJEZDRYWkNzVkdfMDFyNDB5Z05TQnF5cGgxXzlXd2kwMXgzQll4UGExUEhPZ3BUaUdsU2NjYUhhMjM; G_ENABLED_IDPS=google; g_state={"i_p":1603146027183,"i_l":3}; token_v2=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDI1NDc4MDEsInN1YiI6Ii1tM3UwSURPaE9XRHU4RXhoQnZWTFFnaUY1NE0iLCJsb2dnZWRJbiI6ZmFsc2UsInNjb3BlcyI6WyIqIiwiZW1haWwiXX0.oh0V8ocHLjk4EHe-nU12XynzZIrctts9u6idVjjOOp0; d2_token=3.11eb59721bd2bcc392d90603bedcd050641fb134e853ec3baacaf2fe7543c3a8.eyJhY2Nlc3NUb2tlbiI6Ii1hc25idDFXcEVuTlhSaFB4aVhDNmsxLThETEUiLCJleHBpcmVzIjoiMjAyMC0xMC0xM1QwMDoyNDo1OS4wMDBaIiwibG9nZ2VkT3V0Ijp0cnVlLCJzY29wZXMiOlsiKiIsImVtYWlsIl19; recent_srs=t5_iq3gi%2Ct5_2qizd%2Ct5_2x7he%2Ct5_74is2%2Ct5_rvesz%2Ct5_2r8ot%2Ct5_pc3t3%2Ct5_2rjvi%2Ct5_2rct2%2Ct5_2sey6; session_tracker=Os6k6c7fEp2Zue1cVS.0.1602547844760.Z0FBQUFBQmZoUENFSXQwMjc0RWJnSDhZM0ZxZFNyV25EekZINDFEbEFlRTFlRlNpR1hUbDlUSlZSS3htOEQ1TlFfWk45M25hQ01WbmtQSDNTWXk1V3duVnk4T2dBQ0wtancwN3hLN2hCX2x4TXVRQ3dGOVh3SVh0VC1JSHc2ZTJWNXBRazZqTllnOGc; session=3b59ccc50f720b1058b97bb49d489c527744a447gASVSQAAAAAAAABKhvCEX0dB191G7eAVJX2UjAdfY3NyZnRflIwoOTE0YzkzMjFhMTVjYmMwM2EzNzBlOGNmNDg2MGUyNjA5M2JlYTY1MJRzh5Qu',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    'referer': 'https://www.reddit.com'
}

def save_image(image_file): 
    wget.download(image_file, "pictures")
    print('\nImage Successfully Downloaded')

def return_links(page):
    page = requests.get(page)
    if page.status_code == 200:
        page = html.fromstring(page.text)
        urls = page.xpath('//a/@href')
        return urls
    else:
        print('Bad response from server.')
        sys.exit()

def return_image_links(page):
    page = requests.get(page, headers = headers)
    if page.status_code == 200:
        soup = bs(page.text, "html.parser")
        img_tags = soup.select('img[alt="Post image"]')
        for img_tag in img_tags:
            if img_tag in image_urls:
                useless = 0
            else:
                image_urls.append(img_tag['src'])
        return image_urls
    else:
        print('Bad response from reddit server.')
        sys.exit()

def get_top_pics(subreddit):
    urls = return_image_links(subreddit)
    print('Saving ' + str(len(urls)) + ' images...')
    count = 0
    for i in urls:
        count+=1
        save_image(i)

def post(image, driver):
    driver.get(main_url)
    sleep(4)
    login_button = driver.find_element_by_xpath("//button[contains(text(),'Log In')]")
    login_button.click()
    sleep(3)
    username_input = driver.find_element_by_xpath("//input[@name='username']")
    username_input.send_keys(username)
    password_input = driver.find_element_by_xpath("//input[@name='password']")
    password_input.send_keys(password)
    password_input.submit()
    sleep(4)
    try:
        sleep(2)
        not_now_btn = driver.find_element_by_xpath("//a[contains(text(),'Not Now')]")
        not_now_btn.click()
    except:
        pass
    try: 
        sleep(2)
        close_noti_btn = driver.find_element_by_xpath("//button[contains(text(),'Not Now')]")
        close_noti_btn.click()
        sleep(2)
    except:
        pass
    sleep(3) 
    close_addHome_btn = driver.find_element_by_xpath("//button[contains(text(),'Cancel')]")
    close_addHome_btn.click()
    sleep(1)
    sleep(3)
    try: 
        sleep(2)
        close_noti_btn = driver.find_element_by_xpath("//button[contains(text(),'Not Now')]")
        close_noti_btn.click()
        sleep(2)
    except:
        pass
    new_post_btn = driver.find_element_by_xpath("//div[@role='menuitem']").click()
    sleep(1.5)
    autoit.win_active("Open") 
    sleep(2)
    autoit.control_send("Open","Edit1",image_path+image)
    sleep(1.5)
    autoit.control_send("Open","Edit1","{ENTER}")
    sleep(2)
    next_btn = driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
    sleep(1.5)
    caption_field = driver.find_element_by_xpath("//textarea[@aria-label='Write a caption…']")
    caption_field.send_keys(caption)
    share_btn = driver.find_element_by_xpath("//button[contains(text(),'Share')]").click()
    sleep(10)
    driver.close()

def login():
    login_button = driver.find_element_by_xpath("//button[contains(text(),'Log In')]")
    login_button.click()
    sleep(3)
    username_input = driver.find_element_by_xpath("//input[@name='username']")
    username_input.send_keys(username)
    password_input = driver.find_element_by_xpath("//input[@name='password']")
    password_input.send_keys(password)
    password_input.submit()

def close_reactivated(driver):
    try:
        sleep(2)
        not_now_btn = driver.find_element_by_xpath("//a[contains(text(),'Not Now')]")
        not_now_btn.click()
    except:
        pass

def close_notification(driver):
    try: 
        sleep(2)
        close_noti_btn = driver.find_element_by_xpath("//button[contains(text(),'Not Now')]")
        close_noti_btn.click()
        sleep(2)
    except:
        pass

def close_add_to_home(driver):
    sleep(3) 
    close_addHome_btn = driver.find_element_by_xpath("//button[contains(text(),'Cancel')]")
    close_addHome_btn.click()
    sleep(1)

if __name__ == '__main__':
    counter = 0
    img_list = []
    if (scrape == 'yes'):
        get_top_pics(reddit)
    for root, directories, files in os.walk(image_path):
        for name in files:
            img_list.append(name)
    while counter < len(img_list):
        image = img_list[counter]
        driver = webdriver.Chrome(executable_path=chromedriver,options=opts)
        post(image, driver)
        counter+=1
        sleep(postdelay)
