import regex as re
import requests
from bs4 import BeautifulSoup
import os

class services:
    def __init__(self, site, path):
        self.site = site
        self.path = path
        self.img_urls = []
        self.img_types = ['jpg', 'jpeg', 'png', 'gif']
        self.connect()
        self.extract_urls()

    def multi_replace(self, tokens_to_be_replaced, replace_with, text):
        for token in tokens_to_be_replaced:
            text = text.replace(token, replace_with)
        while(text[:1] == replace_with):
            text = text[1:]
        while(text[-1:] == replace_with):
            text = text[:-1]
        return text

    def create_dest_folders(self):
        tokens_to_be_replaced = ['https://', 'http://', 'www.', '*', '\\', '/', ':', '<', '>', '|', '?', '"', '\'']
        site_name = self.multi_replace(tokens_to_be_replaced, '_', self.site)
        path = os.path.join(site_name, self.path)
        if (len(self.img_urls) != 0) :
            self.img_folder = os.path.join(path, "images")
            if not os.path.isdir(self.img_folder):
                os.makedirs(self.img_folder)

    def connect(self):
        self.response = requests.get(self.site)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def extract_urls(self):
        self.urls = re.findall('["\']((http|ftp)s?://.*?)["\']', self.response.text)
        #add image urls
        for url in self.urls:
            url = url[0]
            for link in url.split(" "):
                if (self.is_img_link(link)):
                    self.img_urls.append(link)

    def extract_images(self):
        img_tags = self.soup.find_all('img')

        for img in img_tags:
            url = ''
            if ' src=' in str(img):
                url = img['src']
            elif ' data-src=' in str(img):
                url = img['data-src']
            if (self.is_img_link(url)):
                self.img_urls.append(url)

    def is_img_link(self, url):
        for img_type in self.img_types:
            if ('.' + img_type) in url:
                return True
        return False

    def create_filename(self, path, filename):
        filename = os.path.join(path, filename)
        while os.path.exists(filename):
            temp = os.path.basename(filename).split('.')
            ftype = temp[len(temp)-1]
            name = '.'.join(temp[:-1])
            if len(name) > 3 and name[-1:] == ')' and name[-3:-2] == '(': #TODO fails in case > 9
                counter = int(name[-2:-1]) #TODO try expect
                counter += 1
                name = name[:-2] + str(counter) + ')'
                filename = name + '.' + ftype
            else:
                filename = name + '(1).' + ftype
            filename = os.path.join(path, filename)
        return filename

    def output_results(self):
        self.create_dest_folders()
        #output for images
        self.img_urls = set(self.img_urls)
        counter = 0
        for url in self.img_urls:
            print(url)
            # regex = r'/([\w_-]+[.]('
            # for img_type in self.img_types:
            #     regex += img_type + '|'
            # regex = regex[:-1] + r')'
            # filename = re.search(regex, url, re.IGNORECASE)
            filename = re.search(r'/([\w_-]+[.](jpg|gif|png|jpeg))', url, re.IGNORECASE) #TODO makes it dynamic
            if filename == None:
                filename = re.sub('[^0-9a-zA-Z]+', '', url) + ".jpg"
            else:
                filename = filename.group(1)
            filename = self.create_filename(self.img_folder, filename)
            with open(filename, 'wb') as f:
                if 'http' not in url:
                    url = '{}{}'.format(self.site, url)
                response = requests.get(url)
                f.write(response.content)
            counter +=1
            if counter == 3:
                break

if __name__ == "__main__":
    site = 'https://www.youtube.com/'
    services = services(site, "")
    services.extract_images()
    services.output_results()

