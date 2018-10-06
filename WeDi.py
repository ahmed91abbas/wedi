import regex as re
import requests
from bs4 import BeautifulSoup
import os

class services:
    def __init__(self, site, path):
        self.site = site
        self.create_dest_folders(path)
        self.img_urls = []
        self.connect()
        self.extract_urls()

    def create_dest_folders(self, path):
        self.img_folder = os.path.join(path, "images")
        if not os.path.isdir(self.img_folder):
            os.makedirs(self.img_folder)

    def connect(self):
        response = requests.get(self.site)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def extract_urls(self):
        self.urls = self.soup.find_all('a')
        #add image urls
        suff = ['jpg', 'jpeg', 'png', 'gif']
        for tag in self.urls:
            if ('href=' in str(tag)):
                url = tag['href']
                if (len(url) > 4 and (url[-4:] in suff or url[-3:] in suff)):
                    self.img_urls.append(url)

    def extract_images(self):
        img_tags = self.soup.find_all('img')

        for img in img_tags:
            print(img)
            if ' src=' in str(img):
                self.img_urls.append(img['src'])
            elif ' data-src=' in str(img):
                self.img_urls.append(img['data-src'])


    def output_results(self):
        #output for images
        for url in self.img_urls:
            print(url)
            filename = re.search(r'/([\w_-]+[.](jpg|gif|png|jpeg))', url)
            if filename == None:
                filename = re.sub('[^0-9a-zA-Z]+', '', url) + ".jpg"
            else:
                filename = filename.group(1)
            filename = os.path.join(self.img_folder, filename)
            with open(filename, 'wb') as f:
                if 'http' not in url:
                    url = '{}{}'.format(self.site, url)
                response = requests.get(url)
                f.write(response.content)

if __name__ == "__main__":
    site = 'https://twitter.com/Maserati_HQ?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor'
    services = services(site, "")
    services.extract_images()
    services.output_results()

