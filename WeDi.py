from __future__ import unicode_literals
import regex as re
import requests
from bs4 import BeautifulSoup
import os, sys, shutil
import youtube_dl
import platform
import subprocess
import time

class MyLogger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

class dummy:
    def __init__(self):
        pass
    def update_values(self, url='', dl='', perc='', size='', eta='', speed='', action=''):
        pass
    def set_stopevent(self):
        pass
    def add_to_list(self, name):
        pass
    def add_to_urls(self, urls):
        pass
    def remove_from_urls(self, url):
        pass

class services:
    def __init__(self, site, settings, GUI=None):
        self.site = site
        self.domain = self.extract_domain(site)
        self.path = settings['path']
        if GUI:
            self.gui = GUI
        else:
            self.gui = dummy()
        self.clean_up() #TODO remove
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
        self.vid_format = settings['videos']['format']
        self.vid_folder = ""
        self.aud_urls = []
        self.aud_run = settings['audios']['run']
        self.aud_types = settings['audios']['aud_types']
        self.aud_folder = ""
        self.dev_run = settings['dev']['run']
        self.dev_folder = ""

    def run(self):
        self.connect()
        self.urls = self.extract_urls()
        if self.img_run:
            self.gui.add_to_urls(set(self.img_urls))
        if self.doc_run:
            self.gui.add_to_urls(set(self.doc_urls))
        if self.vid_run:
            self.gui.add_to_urls(set(self.vid_urls))
        if self.aud_run:
            self.gui.add_to_urls(set(self.aud_urls))
        self.output_results()

    def my_hook(self, d):
        if d['status'] == 'finished':
            self.gui.update_values(url=d['filename'], dl=d['total_bytes'], perc='100.0%',
                size=d['total_bytes'], eta='0 Seconds', speed='0.0 KB/s',
                action='Done downloading, now converting...')
            self.gui.add_to_list(d['filename'])
            print('\nDone downloading, now converting...')
        else:
            self.gui.update_values(url=self.site, dl=d['downloaded_bytes'], perc=d['_percent_str'],
                 size=d['total_bytes'], eta=d['_eta_str'], speed=d['_speed_str'])
            print("Progress:" + d['_percent_str'], "of ~" + d['_total_bytes_str'],
                "at " + d['_speed_str'], "ETA " + d['_eta_str'], " "*5, end='\r')

    def extract_domain(self, site):
        domain = re.search('(http|ftp)s?[:\/\/]+[A-Za-z0-9\.]+\/', site)
        if not domain:
            return ""
        res = domain.group(0).split('://')
        protocol = res[0]
        domain = res[1]
        return (protocol, domain)

    def fix_url(self, url):
        if 'http' not in url and len(url) > 2:
            protocol = self.domain[0]
            domain_name = self.domain[1]
            if url[:2] == '//':
                return protocol + ':' + url
            if url[:1] == '/':
                url = url[1:]
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
        self.downloadpath = os.path.join(site_name, self.path)
        self.img_folder = os.path.join(self.downloadpath, "images")
        if not os.path.isdir(self.img_folder):
            os.makedirs(self.img_folder)
        self.doc_folder = os.path.join(self.downloadpath, "documents")
        if not os.path.isdir(self.doc_folder):
            os.makedirs(self.doc_folder)
        self.vid_folder = os.path.join(self.downloadpath, "videos")
        if not os.path.isdir(self.vid_folder):
            os.makedirs(self.vid_folder)
        self.aud_folder = os.path.join(self.downloadpath, "audios")
        if not os.path.isdir(self.aud_folder):
            os.makedirs(self.aud_folder)
        self.dev_folder = os.path.join(self.downloadpath, "dev")
        if not os.path.isdir(self.dev_folder):
            os.makedirs(self.dev_folder)

    def download_url(self, url, filename):
        self.gui.remove_from_urls(url)
        #try:
        with open(filename, "wb") as f:
            print("\nDownloading %s" % url)
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                start = time.clock()
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.flush()
                    if dl == total_length:
                        perc_str = '100.0%'
                        speed_str = '0.0 KB/s'
                        eta_str = '0 Seconds'
                    else:
                        perc_str = str(round(dl*100/total_length, 1)) + '%'
                        speed = dl/(time.clock() - start)
                        eta = int((total_length - dl) / speed)
                        if eta > 3600:
                            eta_str = str(round(eta / 3600, 2)) + ' Hours'
                        elif eta > 60:
                            eta_str = str(round(eta / 60, 2)) + ' Minutes'
                        else:
                            eta_str = str(eta) + ' Seconds'
                        if speed > 10**6:
                            speed_str = str(round(speed/10**6, 1)) + ' MB/s'
                        else:
                            speed_str = str(int(speed/1000)) + ' KB/s'
                    self.gui.update_values(url=url, dl=dl, perc=perc_str, size=total_length, eta=eta_str, speed=speed_str)
        self.gui.add_to_list(filename)
        # except:
        #     print("Falied to download!")

    def connect(self):
        try:
            self.response = requests.get(self.site, allow_redirects=True)
            # print(self.response.text)
            #print(self.response.headers)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            print("Couldn't establish a connection to: " + self.site)
            exit()

    def extract_urls(self):
        urls = re.findall('["\']((http|ftp)s?://.*?)["\']', self.response.text)
        for link in self.soup.find_all('a'):
            if 'href' in str(link):
                urls.append((link['href'], ""))
        urls.append((self.site, ""))
        urls = set(urls)
        for url in urls:
            url = url[0]
            for link in url.split(" "):
                link = self.fix_url(link)
                link = self.apply_special_rules(link)
                if (self.is_img_link(link)):
                    self.img_urls.append(link)
                elif (self.is_doc_link(link)):
                    self.doc_urls.append(link)
                elif (self.is_vid_link(link)):
                    self.vid_urls.append(link)
                elif (self.is_aud_link(link)):
                    self.aud_urls.append(link)
        self.extract_images()
        return urls

    def find_between(self, s, first, last):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def extract_images(self):
        res = re.findall(';pic=.*;', str(self.soup))
        for url in res:
            url = url[5:-1]
            url =  self.fix_url(url)
            url = self.apply_special_rules(url)
            self.img_urls.append(url)

        img_tags = self.soup.find_all('img')
        for img in img_tags:
            url = ''
            if ' src=' in str(img):
                url = img['src']
            elif ' data-src=' in str(img):
                url = img['data-src']
            url =  self.fix_url(url)
            url = self.apply_special_rules(url)
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
            else:
                filename = self.create_filename(output_dir, "noname." + types[0])
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

    def ydl_audios(self):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist':True,
                'outtmpl': self.aud_folder + '\%(title)s.%(ext)s',
                'logger': MyLogger(),
                'progress_hooks': [self.my_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.site])
        except:
            pass

    def ydl_video(self):
        ydl_opts = {
            'outtmpl': self.vid_folder + '\%(title)s.%(ext)s',
            'format': self.vid_format,
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
        }
        #try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.site])
 #      except:
  #         pass

    def rm_empty_dirs(self):
        if not os.listdir(self.vid_folder):
            os.rmdir(self.vid_folder)
        if not os.listdir(self.aud_folder):
            os.rmdir(self.aud_folder)
        if not os.listdir(self.doc_folder):
            os.rmdir(self.doc_folder)
        if not os.listdir(self.img_folder):
            os.rmdir(self.img_folder)
        if not os.listdir(self.dev_folder):
            os.rmdir(self.dev_folder)

    def output_results(self):
        self.create_dest_folders()
        if self.dev_run:
            self.output_dev()
            print()
        if self.img_run:
            self.download_links(self.img_urls, self.img_types, self.img_folder)
            print()
        if self.doc_run:
            self.download_links(self.doc_urls, self.doc_types, self.doc_folder)
            print()
        if self.vid_run:
            self.download_links(self.vid_urls, self.vid_types, self.vid_folder)
            print()
            print("Trying to extract video using youtube_dl...")
            self.ydl_video()
            print()
        if self.aud_run:
            self.download_links(self.aud_urls, self.aud_types, self.aud_folder)
            print()
            print("Trying to extract audios using youtube_dl...")
            self.ydl_audios()
            print()
        self.rm_empty_dirs()
        print("Done.")
        self.gui.set_stopevent()

    def open_path(self):
        if platform.system() == "Windows":
            os.startfile(self.downloadpath)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self.downloadpath])
        else:
            subprocess.Popen(["xdg-open", self.downloadpath])

    def clean_up(self):
        try:
            dirs = [os.path.join(self.path, d) for d in os.listdir(self.path)
                        if os.path.isdir(os.path.join(self.path, d))]
            for d in dirs:
                if d != os.path.join(self.path, '.git') and d != os.path.join(self.path, 'textures'):
                    shutil.rmtree(d)
        except:
            pass

if __name__ == "__main__":
    site = 'https://www.dplay.se/videos/stories-from-norway/stories-from-norway-102'
    site = 'https://www1.gogoanime.sh/boruto-naruto-next-generations-episode-77'
    site = 'https://www.youtube.com/watch?v=bugktEHP1n0'
    site = 'https://www.stackoverflow.com' #error
    site = 'http://cs.lth.se/edan20/'
    site = 'https://www.youtube.com/watch?v=zmr2I8caF0c' #small
    site = 'https://www.bytbil.com/skane-lan/personbil-v50-topp-skick-med-1-arsgaranti-2089-12646959' #cannot find all images
    path = "."
    img_types = ['jpg', 'jpeg', 'png', 'gif']
    doc_types = ['txt', 'py', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
    vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp', 'webm', 'ogg']
    aud_types = ['mp3', 'aac', 'wma', 'wav', 'm4a']
    img_settings = {'run':True, 'img_types':img_types}
    doc_settings = {'run':False, 'doc_types':doc_types}
    vid_settings = {'run':False, 'vid_types':vid_types, 'format':'best'}
    aud_settings = {'run':False, 'aud_types':aud_types}
    dev_settings = {'run':True}
    settings = {'path':path, 'openfolder':False, 'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audios':aud_settings, 'dev':dev_settings}
    services = services(site, settings)
    services.run()

