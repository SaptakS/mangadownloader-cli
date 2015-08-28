import os
import urllib2
import requests
from BeautifulSoup import BeautifulSoup as bs
import re
from difflib import SequenceMatcher as sm
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError

def findNextURL(imageUrl):
    
    return imageUrl.parent['href']

def saveImg(data):
    
    maxval = 0
    maxurl = ""
    imglinks = data.findAll("img")
    for link in imglinks:
        if sm(None, str(link['src']), BASE_URL).ratio() > maxval:
            maxval = sm(None, str(link['src']),BASE_URL).ratio()
            maxl = link
            maxurl = link['src']
    try:
        image = requests.get(maxurl)
    except:
        print "Error        "
    
    file = open(os.path.join(BASE_PATH, "%s.jpg") % IMAGE_TITLE, 'wb')
    try:
        Image.open(StringIO(image.content)).save(file, 'JPEG')
    except IOError, e:
        print "Couldnt Save:"
        
    finally:
        file.close()
    
    return maxl
    
def linkData(url):
    req = urllib2.Request(BASE_URL)
    resp = urllib2.urlopen(req).read()
    
    data = bs("".join(resp))
    
    return data
    
BASE_PATH = raw_input("Enter Name of the Folder to save in:")    
BASE_URL = raw_input("Enter the First Page URL:")
BASE_HOST = re.split(r"/",BASE_URL)[0] + "//" + re.split(r"/",BASE_URL)[2]
print BASE_HOST
TOTAL_IMG = int(raw_input("Enter total images to download:"))
IMAGE_TITLE = 0

if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

imageUrl = saveImg(linkData(BASE_URL))
#print imageUrl.parent['href']

ctr = 0
while ctr < TOTAL_IMG - 1:
    IMAGE_TITLE = IMAGE_TITLE + 1
    BASE_URL = findNextURL(imageUrl)
    if not "://" in BASE_URL:
        BASE_URL = BASE_HOST + BASE_URL
    print "Next page is", BASE_URL
    imageUrl = saveImg(linkData(BASE_URL))
    ctr = ctr + 1
    



