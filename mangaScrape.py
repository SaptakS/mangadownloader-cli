import os
import urllib2
import requests
from BeautifulSoup import BeautifulSoup as bs
import re
from difflib import SequenceMatcher as sm
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError


proxy = "http://<username>:<password>@<host>:<port>"
proxyDict = {
              "http": proxy,
              "https": proxy,
              "ftp": proxy
            }

proxy_support = urllib2.ProxyHandler(proxyDict)
opener = urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def findNextURL(imageUrl):

    return imageUrl.parent["href"]


def saveImg(data):
    maxval = 0
    maxurl = ""
    imglinks = data.findAll("img")
    check_link = BASE_HOST.split("//")[1]
    if len(check_link.split('.')) > 2:
        check_link = check_link.split('.')[1] + "." + check_link.split('.')[2]
    for link in imglinks:
        if check_link in str(link['src']) and sm(None, str(link['src']), BASE_URL.replace("http", "")).ratio() > maxval:
            maxval = sm(None, str(link['src']), BASE_URL).ratio()
            maxl = link
            maxurl = link['src']
    if maxurl == '':
        for link in imglinks:
            if sm(None, str(link['src']), BASE_URL.replace("http", "")).ratio() > maxval:
                maxval = sm(None, str(link['src']), BASE_URL).ratio()
                maxl = link
                maxurl = link['src']

    if "http" not in str(maxurl):
        maxurl = BASE_HOST.split("//")[0] + maxurl

    try:
        image = requests.get(maxurl, proxies=proxyDict)
        print "Images Saved Successfully"
    except:
        print "Error        "
        exit(0)

    file = open(os.path.join(BASE_PATH, "%s.jpg") % IMAGE_TITLE, 'wb')
    try:
        Image.open(StringIO(image.content)).save(file, 'JPEG')
    except IOError, e:
        print "Couldnt Save:", e

    finally:
        file.close()

    return maxl


def linkData(url):
    try:
        #req = urllib2.Request(BASE_URL, headers=hdr)
        #resp = urllib2.urlopen(req).read()
        r = requests.get(BASE_URL, proxies=proxyDict)

        data = bs("".join(r.text))

        return data
    except urllib2.HTTPError, e:
        print e.fp.read()


BASE_PATH = raw_input("Enter Name of the Folder to save in:")
BASE_URL = raw_input("Enter the First Page URL:")
BASE_HOST = re.split(r"/", BASE_URL)[0] + "//" + re.split(r"/", BASE_URL)[2]
BASE_CHECK_LINK = BASE_URL
#print BASE_HOST
TOTAL_IMG = int(raw_input("Enter total images to download:"))
IMAGE_TITLE = 0

if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

imageUrl = saveImg(linkData(BASE_URL))
#print imageUrl.parent['href']

ctr = 0
while ctr < TOTAL_IMG - 1:
    IMAGE_TITLE = IMAGE_TITLE + 1
    next_rel = findNextURL(imageUrl)
    #print next_rel
    if not "://" in next_rel:
        if next_rel.startswith("/"):
            BASE_URL = BASE_HOST + next_rel
        else:
            BASE_URL = re.sub(r"\w+.html", next_rel, BASE_URL)
    print "Next page is", BASE_URL
    imageUrl = saveImg(linkData(BASE_URL))
    ctr = ctr + 1
print "Total Pages Downloaded: ", (ctr + 1)
