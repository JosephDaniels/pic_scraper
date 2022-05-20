#!/bin/python3
""" Created from Alan Wong's excellent website scraper!!!

This is for use specifically with the website safebooru.


    Version date: May 20th, 2022
    Licence: MIT
"""

import shutil
import logging
import time

import requests
from bs4 import BeautifulSoup

START_PAGE_NUM = 1
MAX_SEARCH_PAGES = 2  # set this to the max pages to scan
SEARCH_URL = "https://safebooru.org/index.php?page=post&s=list&tags=elf+sword+shield+armor&pid="
IMAGE_PAGE_URL = "https://safebooru.org/index.php?page=post&s=view&id="

pid_increment = 40  # Safebooru uses 40 pictures per page.

# auth_token = open("eventbrite_api_key.txt", "r").read() # need a developer API key from Eventbrite to scan for event details
# my_headers = {'Authorization': f'Bearer {auth_token}'}

logging.basicConfig(filename='scrape.log', level=logging.WARNING)


def save_image(url):
    print(url)
    r = requests.get(url, stream=True)
    filename = "saved_images/"+url.split("/")[-1]
    print(filename)
    if r.status_code == 200: # All Good
        print("Image is good!")
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    print("Saved %s" % (filename))

def get_page(n):
    # get the html for the page n of the search
    response = requests.get(SEARCH_URL + str(n))
    raw_html = response.text
    soup = BeautifulSoup(raw_html, features='html.parser')
    return soup

def get_image_page(image_id):
    # get the html for the page n of the search
    cookies = {"resize-original":"1","resize-notification":"1"}
    response = requests.get(IMAGE_PAGE_URL+image_id, cookies=cookies)
    raw_html = response.text
    soup = BeautifulSoup(raw_html, features='html.parser')
    return soup

def scan_for_images(soup):
    ## Thumbnails Page / Many Images
    content_div = soup.find_all("div", class_="content")[0]
    #print(content_div)
    spans = content_div.find_all("span")
    print (len(spans)) # Shows us the amount of images
    found_image_urls = []
    for span in spans:
        image_id = span['id'].strip('s')
        print (image_id) # Get all ids minus "s"
        ## This is where the page that actually hosts the image is OPEN
        image_page_soup = get_image_page(image_id) #Open image page as soup
        image_content_div = image_page_soup.find_all("div", class_="content")[0]
        image_span = image_content_div.find_all("img")[0]
        image_url = image_span['src']
        if image_url.find("sample"):
            #Do a conversion
            image_url = image_url.replace("//samples","//images")
            image_url = image_url.replace("/sample_","/")
            image_url = image_url.split("?")[0]
        found_image_urls.append(image_url)
    print (found_image_urls)
    for url in found_image_urls:
        print (url)
        save_image(url)


##########
# MAIN
##########
def main():
    pics = []
    # capture the the events from Eventbrite
    page_num = START_PAGE_NUM
    do_loop = True
    while do_loop and page_num < MAX_SEARCH_PAGES:
        pid = (START_PAGE_NUM - 1) * 40
        soup = get_page(pid)
        scan_for_images(soup)
        if (pid) > 0:  # no more search results
            do_loop = False
        else:  # process the page for entries
            time.sleep(2)
            page_num += 1
    print("End of pages")

if __name__ == "__main__":
    main()