import regex as re
import requests
from bs4 import BeautifulSoup
import os
import shutil
import wget
#import youtube-dl TODO
'''
second layer video and audio download using youtube dl
download sound with highest quilety
make quility options for video download
'''

class services:
    def __init__(self, site, settings):
        self.site = site
        self.domain = self.extract_domain(site)
        self.path = settings['path']
        self.img_urls = []
        self.img_run = settings['images']['run']
        self.img_types = settings['images']['img_types']
        self.img_folder = ""
        self.doc_urls = []
        self.doc_run = settings['documents']['run']
        self.doc_types = settings['documents']['doc_types']
        self.doc_folder = ""
        self.vid_urls = []
        self.vid_run = settings['videos']['run']
        self.vid_types = settings['videos']['vid_types']
        self.vid_folder = ""
        self.aud_urls = []
        self.aud_run = settings['audio']['run']
        self.aud_types = settings['audio']['aud_types']
        self.aud_folder = ""
        self.dev_run = settings['dev']['run']
        self.dev_folder = ""
        self.connect()
        self.urls = self.extract_urls()

    def extract_domain(self, site):
        domain = re.search('(http|ftp)s?[:\/\/]+[A-Za-z0-9\.]+\/', site)
        if not domain:
            return ""
        res = domain.group(0).split('://')
        protocol = res[0]
        domain = res[1]
        return (protocol, domain)

    def fix_url(self, url):
        if 'http' not in url:
            if url[:1] == '/':
                url = url[1:]
            protocol = self.domain[0]
            domain_name = self.domain[1]
            x = len(domain_name)
            if len(url) > x and url[:x] == domain_name:
                return protocol + '://' + url
            return protocol + '://' + domain_name + url
        return url

    def apply_special_rules(self, url):
        if ("github" in self.domain[1]):
            url = url.replace('https://github.com/', 'https://raw.github.com/')
            url = url .replace('blob/', '')
            return url
        return url

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
        if (len(self.img_urls) != 0 and self.img_run) :
            self.img_folder = os.path.join(path, "images")
            if not os.path.isdir(self.img_folder):
                os.makedirs(self.img_folder)
        if (len(self.doc_urls) != 0 and self.doc_run) :
            self.doc_folder = os.path.join(path, "documents")
            if not os.path.isdir(self.doc_folder):
                os.makedirs(self.doc_folder)
        if (len(self.vid_urls) != 0 and self.vid_run) :
            self.vid_folder = os.path.join(path, "videos")
            if not os.path.isdir(self.vid_folder):
                os.makedirs(self.vid_folder)
        if (len(self.aud_urls) != 0 and self.aud_run) :
            self.aud_folder = os.path.join(path, "audio")
            if not os.path.isdir(self.aud_folder):
                os.makedirs(self.aud_folder)
        if (self.dev_run) :
            self.dev_folder = os.path.join(path, "dev")
            if not os.path.isdir(self.dev_folder):
                os.makedirs(self.dev_folder)

    def download_url(self, url, filename):
        try:
            print("\n", url)
            wget.download(url, filename)
        except:
            print("Falied to download!")

    def connect(self):
        try:
            self.response = requests.get(self.site, allow_redirects=True)
            # print(self.response.text)
            #print(self.response.headers)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            print("Couldn't establish a connection to: " + self.site)

    def extract_urls(self):
        urls = re.findall('["\']((http|ftp)s?://.*?)["\']', self.response.text)
        for link in self.soup.find_all('a'):
            if 'href' in str(link):
                urls.append((link['href'], ""))
        urls = set(urls)
        for url in urls:
            url = url[0]
            for link in url.split(" "):
                link = self.fix_url(link)
                link = self.apply_special_rules(link)
                if (self.is_img_link(link)):
                    self.img_urls.append(link)
                if (self.is_doc_link(link)):
                    self.doc_urls.append(link)
        self.extract_images()
        return urls

    def extract_images(self):
        img_tags = self.soup.find_all('img')

        for img in img_tags:
            url = ''
            if ' src=' in str(img):
                url = img['src']
            elif ' data-src=' in str(img):
                url = img['data-src']
            url =  self.fix_url(url)
            url = self.apply_special_rules(url)
            if (self.is_img_link(url)):
                self.img_urls.append(url)

    def is_img_link(self, url):
        for img_type in self.img_types:
            if ('.' + img_type) in url:
                return True
        return False

    def is_doc_link(self, url):
        for doc_type in self.doc_types:
            if ('.' + doc_type) in url[-len(doc_type) - 1:]:
                return True
        return False

    def is_vid_link(self, url):
        for vid_type in self.vid_types:
            if ('.' + vid_type) in url[-len(vid_type) - 1:]:
                return True
        return False

    def is_aud_link(self, url):
        for aud_type in self.aud_types:
            if ('.' + aud_type) in url[-len(aud_type) - 1:]:
                return True
        return False

    def create_filename(self, path, filename):
        filename = os.path.join(path, filename)
        while os.path.exists(filename):
            temp = os.path.basename(filename).split('.')
            ftype = temp[len(temp)-1]
            name = '.'.join(temp[:-1])
            match = re.findall('[(][0-9]+[)].' + ftype, filename)
            if match:
                nbr = int(re.sub('[^0-9]','', match[0])) + 1
                filename = filename.replace(match[0], '')
                filename = filename + '(' + str(nbr) +').' + ftype
            else:
                filename = name + '(1).' + ftype
                filename = os.path.join(path, filename)
        return filename

    def download_links(self, urls, types, output_dir):
        urls = set(urls)
        for url in urls:
            regex = r'/([^/]*[.]('
            for t in types:
                regex += t + '|'
            regex = regex[:-1] + '))'
            filename = re.findall(regex, url, re.IGNORECASE)
            if filename != None and len(filename) != 0:
                filename = filename[len(filename)-1][0]
                filename = self.create_filename(output_dir, filename)
                self.download_url(url, filename)

    def output_dev(self):
        with open(os.path.join(self.dev_folder, 'mainURL.txt'), 'w') as f:
            f.write(self.site + "\n\n")
            f.write("Headers:\n")
            for head in self.response.headers:
                f.write(head + ": " + str(self.response.headers[head]) + "\n")
        with open(os.path.join(self.dev_folder, 'source.html'), 'wb') as f:
            f.write(self.soup.prettify().encode("utf-8"))
        if (len(self.img_urls) != 0):
            with open(os.path.join(self.dev_folder, 'imgURLs.txt'), 'w') as f:
                for url in set(self.img_urls):
                    f.write(url + "\n")
        if (len(self.doc_urls) != 0):
            with open(os.path.join(self.dev_folder, 'docURLs.txt'), 'w') as f:
                for url in set(self.doc_urls):
                    f.write(url + "\n")
        if (len(self.vid_urls) != 0):
            with open(os.path.join(self.dev_folder, 'vidURLs.txt'), 'w') as f:
                for url in set(self.vid_urls):
                    f.write(url + "\n")
        if (len(self.aud_urls) != 0):
            with open(os.path.join(self.dev_folder, 'audURLs.txt'), 'w') as f:
                for url in set(self.aud_urls):
                    f.write(url + "\n")

    def output_results(self):
        self.create_dest_folders()
        if self.img_run:
            self.download_links(self.img_urls, self.img_types, self.img_folder)
        if self.doc_run:
            self.download_links(self.doc_urls, self.doc_types, self.doc_folder)
        if self.vid_run:
            self.download_links(self.vid_urls, self.vid_types, self.vid_folder)
        if self.aud_run:
            self.download_links(self.aud_urls, self.aud_types, self.aud_folder)
        if self.dev_run:
            self.output_dev()

    def clean_up(self):
        try:
            dirs = [os.path.join(self.path, d) for d in os.listdir(self.path)
                        if os.path.isdir(os.path.join(self.path, d))]
            for d in dirs:
                if d != os.path.join(self.path, '.git'):
                    shutil.rmtree(d)
        except:
            pass

if __name__ == "__main__":
    site = 'https://youtube.com/'
    path = "."
    img_types = ['jpg', 'jpeg', 'png', 'gif']
    doc_types = ['py', 'txt', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
    vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp']
    aud_types = ['mp3', 'aac', 'wma', 'wav']
    img_settings = {'run':False, 'img_types':img_types}
    doc_settings = {'run':False, 'doc_types':doc_types}
    vid_settings = {'run':False, 'vid_types':vid_types}
    aud_settings = {'run':False, 'aud_types':aud_types}
    dev_settings = {'run':True}
    settings = {'path':path, 'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audio':aud_settings, 'dev':dev_settings}
    services = services(site, settings)
    services.clean_up() #TODO remove
    services.output_results()

