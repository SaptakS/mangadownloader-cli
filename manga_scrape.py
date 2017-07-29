import os
import requests
import re

from io import BytesIO
from bs4 import BeautifulSoup as bs
from difflib import SequenceMatcher as sm
from requests.exceptions import ConnectionError
from PIL import Image

# uncomment this code for using proxy
#proxy = "http://<username>:<password>@<host>:<port>"
#proxyDict = {
#              "http": proxy,
#              "https": proxy,
#              "ftp": proxy
#            }

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                     'AppleWebKit/537.11 (KHTML, like Gecko) '
                     'Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,'
                 'application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def getsize(url):
    if not url.startswith("data:"):
        response = requests.head(url)
        if 'content-length' in response.headers:
            return int(response.headers['content-length'])
    return 0

def findNextURL(imageUrl):

    return imageUrl.parent["href"]


def saveImg(data, base_host, base_url, base_path, image_title):
    maxval = 0
    maxurl = ""
    imglinks = data.findAll("img")
    for link in imglinks:
        img_size = getsize(link['src'].strip())
        sequence_match_ratio = 0
        if 'alt' in link.attrs:
            sequence_match_ratio = sm(None,
                                  str(link['alt']),
                                  base_url.replace("http", "")).ratio()
        if sequence_match_ratio > maxval and img_size > 99999:
            maxval = sm(None, str(link['alt']), base_url).ratio()
            maxl = link
            maxurl = link['src'].strip()

    if "http" not in str(maxurl):
        maxurl = base_host.split("//")[0] + maxurl

    try:
        # uncomment if proxy settings
        # image = requests.get(maxurl, proxies=proxyDict)

        # comment if proxy settings
        image = requests.get(maxurl)
        print("Images Saved Successfully")
    except:
        print ("Error")
        exit(0)

    file = open(os.path.join(base_path, "%s.jpg") % image_title, 'wb')
    try:
        Image.open(BytesIO(image.content)).save(file, 'JPEG')
    except IOError as e:
        print("Couldnt Save:", e)

    finally:
        file.close()

    return maxl


def linkData(base_url):
    try:
        # uncomment if proxy settings
        # r = requests.get(base_url, proxies=proxyDict)

        # comment if proxy settings
        r = requests.get(base_url)

        data = bs("".join(r.text), "html.parser")

        return data
    except ConnectionError:
        print("Link read error")


def main(base_url, base_path, total_img):
    base_host = re.split(r"/", base_url)[0] + "//" + re.split(r"/", base_url)[2]

    image_title = 0

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    imageUrl = saveImg(linkData(base_url), base_host,
                       base_url, base_path, image_title)

    ctr = 0
    while ctr < total_img - 1:
        image_title = image_title + 1
        next_rel = findNextURL(imageUrl)
        if not "://" in next_rel:
            if next_rel.startswith("/"):
                base_url = base_host + next_rel
            else:
                base_url = re.sub(r"\w+.html", next_rel, base_url)
        else:
            base_url = next_rel

        print("Next page is", base_url)
        imageUrl = saveImg(linkData(base_url), base_host,
                           base_url, base_path, image_title)
        ctr = ctr + 1
    print("Total Pages Downloaded: ", (ctr + 1))

BASE_PATH = input("Enter Name of the Folder to save in:")
BASE_URL = input("Enter the First Page URL:")
TOTAL_IMG = int(input("Enter total images to download:"))
main(BASE_URL, BASE_PATH, TOTAL_IMG)
