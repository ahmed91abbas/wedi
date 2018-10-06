import regex as re
import requests
from bs4 import BeautifulSoup
import os

class services:
    def __init__(self, site, path):
        self.site = site
        self.create_dest_folders(path)
        self.img_urls = []
        self.img_types = ['jpg', 'jpeg', 'png', 'gif']
        self.connect()
        self.extract_urls()

    def create_dest_folders(self, path):
        self.img_folder = os.path.join(path, "images")
        if not os.path.isdir(self.img_folder):
            os.makedirs(self.img_folder)

    def connect(self):
        self.response = requests.get(self.site)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def extract_urls(self):
        # self.urls = self.soup.find_all('a')
        self.urls = re.findall('["\']((http|ftp)s?://.*?)["\']', self.response.text)
        #add image urls
        for url in self.urls:
            url = url[0]
            if (len(url) > 4 and (url[-4:] in self.img_types or url[-3:] in self.img_types)):
                self.img_urls.append(url)

    def extract_images(self):
        img_tags = self.soup.find_all('img')

        for img in img_tags:
            url = ''
            if ' src=' in str(img):
                url = img['src']
            elif ' data-src=' in str(img):
                url = img['data-src']
            if (len(url) > 4 and (url[-4:] in self.img_types or url[-3:] in self.img_types)):
                self.img_urls.append(url)

    def output_results(self):
        #output for images
        self.img_urls = set(self.img_urls)
        for url in self.img_urls:
            print(url)
            filename = re.search(r'/([\w_-]+[.](jpg|gif|png|jpeg))', url)
            if filename == None:
                print(url)
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
    site = 'https://www.youtube.com/watch?v=GhlLy2elSlI'
    services = services(site, "")
    services.extract_images()
    services.output_results()

