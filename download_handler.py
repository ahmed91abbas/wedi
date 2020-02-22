from __future__ import unicode_literals
import regex as re
import requests
from bs4 import BeautifulSoup
import os, sys, shutil
import youtube_dl
import subprocess
import time
from selenium import webdriver
import glob
import ntpath
import importlib

class MyLogger(object):
    def __init__(self):
        self.msgs = []
    def debug(self, msg):
        self.msgs.append(msg)
    def warning(self, msg):pass
    def error(self, msg):pass

class dummyGUI:
    def update_values(self, url='', dl='', perc='', size='', eta='', speed='', action=''):pass
    def set_stopevent(self, files=0, size=0, time=0):pass
    def add_to_list(self, name, replace=False):pass
    def add_to_urls(self, urls):pass
    def remove_from_urls(self, url):pass
    def update_action(self, text):pass
    def show_error(self, msg):pass

class services:
    def __init__(self, site, settings, GUI=None):
        self.url_regex = '(https?://[0-9A-Za-z-._~?/#]+)'
        self.relative_url_regex = '(?:src|alt|srcset)=[\"\']{1}(/[0-9A-Za-z-._~?/#]+)[\"\']{1}'
        os.environ['REQUESTS_CA_BUNDLE'] = os.path.join("certifi", "cacert.pem")
        self.settings = settings
        self.extensive = settings['extensive']
        if site[-1:] != '/':
            site = site + '/'
        self.site = site
        self.domain = self.extract_domain(self.site)
        self.path = settings['path']
        if GUI:
            self.gui = GUI
        else:
            self.gui = dummyGUI()
        self.urls = []
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

        self.force_stop = False
        self.skip = False
        self.finished_running = False

        self.domains_dict = self.init_domains_dict()

    def run(self):
        try:
            self.start_time = time.perf_counter()
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
            self.finished_running = True
        except:
            self.stop()
            self.finished_running = True

    def stop(self):
        self.urls = []
        self.img_urls = []
        self.doc_urls = []
        self.vid_urls = []
        self.aud_urls = []
        self.force_stop = True

    def init_domains_dict(self):
        domains = {}
        root = "domains"
        for filename in glob.glob(os.path.join(root, "*.py")):
            domain_name = ntpath.basename(filename).replace(".py", "")
            module_name = f'{root}.{domain_name}'
            class_name = module_name.replace(f"{root}.", "").capitalize()

            module = importlib.import_module(module_name)
            service = getattr(module, class_name)()

            domains[domain_name] = service
        return domains

    def my_hook(self, d):
        if self.force_stop or self.skip:
            raise Exception("Stopping...")
        if d['status'] == 'finished':
            self.gui.update_values(url=d['filename'], dl=d['total_bytes'], perc='100.0%',
                size=d['total_bytes'], eta='0 Seconds', speed='0.0 KB/s',
                action='Done downloading, now converting...')
            self.gui.add_to_list(d['filename'])
            print('\nDone downloading, now converting...')
        else:
            self.gui.update_values(dl=d['downloaded_bytes'], perc=d['_percent_str'],
                 size=d['total_bytes'], eta=d['_eta_str'], speed=d['_speed_str'])
            print("Progress:" + d['_percent_str'], "of ~" + d['_total_bytes_str'],
                "at " + d['_speed_str'], "ETA " + d['_eta_str'], " "*5, end='\r')

    def extract_domain(self, site):
        domain = re.search(r'https?:\/\/[-_A-Za-z0-9\.]+\/?', site)
        if not domain:
            return ""
        res = domain.group(0).split('://')
        protocol = res[0]
        domain = res[1]
        if domain[-1:] != '/':
            domain += '/'
        return (protocol, domain)

    def fix_url(self, url):
        if url[-1:] == '/':
            url = url[:-1]

        if re.match(self.url_regex, url):
            return url

        if len(url) > 2 and url[0] == '/':
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

        return None

    def get_domain_name(self, url):
        domain = self.extract_domain(url)[1].replace("www.", "")
        return ".".join(domain.split(".")[:-1])

    def apply_domain_special_rules(self, url):
        domain_name = self.get_domain_name(url)
        if domain_name in self.domains_dict:
            return self.domains_dict[domain_name].apply_domian_rules(url, self.settings)
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
        self.downloadpath = os.path.join(self.path, site_name)
        if len(self.downloadpath) > 200:
            self.downloadpath = self.downloadpath[:200] + '_'
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

    def exit_with_error(self, error_message):
        self.stop()
        print(error_message)
        self.gui.show_error(error_message)

    def get_executable_driver_path(self, browser):
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2":
            firefox_driver_path = os.path.join('drivers', 'geckodriver_linux')
            chrome_driver_path = os.path.join('drivers', 'chromedriver_linux')
        elif _platform == "darwin":
            firefox_driver_path = os.path.join('drivers', 'geckodriver_mac')
            chrome_driver_path = os.path.join('drivers', 'chromedriver_mac')
        elif _platform == "win32" or _platform == "win64":
            firefox_driver_path = os.path.join('drivers', 'geckodriver_win.exe')
            chrome_driver_path = os.path.join('drivers', 'chromedriver_win.exe')

        msg = "%s webdriver is missing! Try reinstalling the program."
        if browser == "firefox":
            if not os.path.isfile(firefox_driver_path):
                self.exit_with_error(msg %browser.capitalize())
            return firefox_driver_path
        elif browser == "chrome":
            if not os.path.isfile(chrome_driver_path):
                self.exit_with_error(msg %browser.capitalize())
            return chrome_driver_path
        else:
            self.exit_with_error("%s webdriver is not supported" %browser)

    def get_firefox_driver(self):
        executable_path = self.get_executable_driver_path("firefox")
        try:
            from selenium.webdriver.firefox.options import Options
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            driver = webdriver.Firefox(executable_path=executable_path, firefox_options=firefox_options)
            return driver
        except:
            return None

    def get_chrome_driver(self):
        chrome_driver_path = self.get_executable_driver_path("chrome")
        try:
            from selenium.webdriver.chrome.options import Options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=chrome_options)
            return driver
        except:
            return None

    def connect_extensive(self):
        driver = self.get_firefox_driver()
        if not driver:
            driver = self.get_chrome_driver()
        if not driver:
            msg = "To use extensive run either Firefox or Chrome browser should be installed!"
            self.exit_with_error(msg)

        try:
            driver.get(self.site)
            self.page_source = driver.page_source
            driver.stop_client()
            driver.close()
            driver.quit()
            self.soup = BeautifulSoup(self.page_source, 'html.parser')
            self.response = requests.get(self.site, allow_redirects=True)
        except:
            msg = "Couldn't establish a connection to: " + self.site
            if len(msg) > 100:
                msg = msg[:97] + "..."
            self.exit_with_error(msg)

    def connect_normal(self):
        try:
            self.response = requests.get(self.site[:-1], allow_redirects=True, stream=True)
            content_type = self.response.headers.get('Content-Type').split(";")[0]
            if content_type != "text/html":
                self.page_source = ""
            else:
                self.page_source = self.response.text
            self.soup = BeautifulSoup(self.page_source, 'html.parser')
        except:
            msg = "Couldn't establish a connection to: " + self.site
            if len(msg) > 100:
                msg = msg[:97] + "..."
            self.exit_with_error(msg)

    def connect(self):
        msg = 'Establishing connection to ' + self.site
        if len(msg) > 100:
            msg = msg[:97] + "..."
        self.gui.update_action(msg)
        if self.extensive:
            self.connect_extensive()
        else:
            self.connect_normal()

    def extract_urls(self):
        self.gui.update_action("Extracting the urls from the website...")
        results = []
        urls = set()
        urls.update(re.findall(self.url_regex, self.page_source))
        urls.update(re.findall(self.relative_url_regex, self.page_source))
        for link in self.soup.find_all('a', href=True):
            urls.add(link['href'])
        urls.add(self.site)
        urls = set(urls)
        for url in urls:
            if self.force_stop:
                return
            url = self.fix_url(url)
            if not url:
                continue
            url = self.apply_domain_special_rules(url)
            results.append(url)
            if self.is_media_url(url, self.img_types):
                self.img_urls.append(url)
            elif self.is_media_url(url, self.doc_types):
                self.doc_urls.append(url)
            elif self.is_media_url(url, self.vid_types):
                self.vid_urls.append(url)
            elif self.is_media_url(url, self.aud_types):
                self.aud_urls.append(url)

        image_urls = self.extract_images()
        self.img_urls += image_urls
        urls.update(image_urls)

        self.vid_urls.append(self.site)

        return results

    def extract_images(self):
        results = re.findall(';pic=(.*);', str(self.soup))
        results = list(map(self.fix_url, results))

        img_tags = self.soup.find_all('img')
        for img in img_tags:
            if self.force_stop:
                return
            url = ''
            if ' src=' in str(img):
                url = img['src']
            elif ' data-src=' in str(img):
                url = img['data-src']
            url =  self.fix_url(url)
            if not url:
                continue
            results.append(url)
        return results

    def is_media_url(self, url, media_types):
        for media_type in media_types:
            extension = ""
            if len(url) > len(media_type):
                extension = url[-len(media_type)-1:]
            if ('.' + media_type) == extension:
                return True
        return False

    def create_filename(self, path, filename):
        tokens_to_be_replaced = ['*', '\\', '/', ':', '<', '>', '|', '?', '"', '\'']
        filename = self.multi_replace(tokens_to_be_replaced, '_', filename)
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

    def download_url(self, url, filename):
        self.gui.remove_from_urls(url)
        try:
            with open(filename, "wb") as f:
                print("\nDownloading %s" % url)
                response = requests.get(url, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None: # no content length header
                    self.gui.update_values(url=url)
                    f.write(response.content)
                else:
                    dl = 0
                    start = time.perf_counter()
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        if self.force_stop or self.skip:
                            f.close()
                            raise Exception("Stopping...")
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
                            speed = dl/(time.perf_counter() - start)
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
        except:
            self.skip = False
            self.delete_file(filename)
            msg = 'Failed to download ' + url
            if len(msg) > 100:
                msg = msg[:97] + "..."
            self.gui.update_action(msg)
            print(msg)

    def download_links(self, urls, types, output_dir):
        urls = set(urls)
        for url in urls:
            if self.force_stop:
                return
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

    def ffmpeg_convert(self, in_file, out_file):
        #TODO support for linux and Mac
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2": # linux
            print("Converting in Linux is not supported yet!")
        elif _platform == "darwin": # MAC OS X
            print("Converting in MAC OS is not supported yet!")
        elif _platform == "win32" or _platform == "win64": # Windows
            ffmpeg_exe = "ffmpeg_win\\bin\\ffmpeg.exe"
            params = [ffmpeg_exe, '-i', in_file, out_file]
            subprocess.call(params, shell=False, close_fds=True)

    def ydl_download_audio_urls(self):
        if self.force_stop:
            return
        try:
            logger = MyLogger()
            filepath = os.path.join(self.aud_folder, '%(title)s.%(ext)s')
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist':True,
                'outtmpl': filepath,
                'logger': logger,
                'progress_hooks': [self.my_hook],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.site])
            msgs = logger.msgs
            for msg in msgs:
                if "[download] Destination: " in msg:
                    filename = msg[24:]
                    name = os.path.splitext(filename)[0]
                    extension = os.path.splitext(filename)[1]
                    if extension != ".mp3":
                        new_name = name + ".mp3"
                        self.ffmpeg_convert(filename, new_name)
                        self.gui.add_to_list(new_name, replace=True)
                        os.remove(filename)
                    break
        except Exception as e:
            self.skip = False
            self.gui.update_action(str(e))
            print(str(e))

    def get_youtube_dl_download_url(self, url):
        try:
            response = youtube_dl.YoutubeDL().extract_info(url, download=False)
        except:
            self.gui.remove_from_urls(url)
            return None
        if "url" in response:
            return response["url"]
        if "entries" in response:
            return response["entries"][-1]['formats'][-1]['url']
        if "formats" in response:
            return response['formats'][-1]['url']

    def filter_youtube_dl_urls(self):
        results = {}
        for url in self.vid_urls:
            if self.force_stop:
                return
            download_url = self.get_youtube_dl_download_url(url)
            if download_url:
                if download_url[-1:] == '/':
                    basename = ntpath.basename(download_url[:-1])
                else:
                    basename = ntpath.basename(download_url)
                results[basename] = {
                    "url": url,
                    "download_url": download_url
                }
        return results

    def ydl_download_video_urls(self):
        results = self.filter_youtube_dl_urls()
        filepath = os.path.join(self.vid_folder, '%(title)s.%(ext)s')
        ydl_opts = {
            'outtmpl': filepath,
            'format': self.vid_format,
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
        }
        for value in results.values():
            if self.force_stop:
                return
            try:
                url = value["url"]
                self.gui.remove_from_urls(url)
                self.gui.update_values(url=url)
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                self.skip = False
                self.gui.update_action(str(e))
                print(str(e))

    def output_dev(self):
        if self.force_stop:
            return
        #General information about main url
        filename = os.path.join(self.dev_folder, 'mainURL.txt')
        with open(filename, 'wb') as f:
            line = self.site + "\n\n"
            f.write(line.encode('utf-8'))
            f.write("Headers:\n".encode('utf-8'))
            for head in self.response.headers:
                line = head + ": " + str(self.response.headers[head]) + "\n"
                f.write(line.encode('utf-8'))
            self.gui.add_to_list(filename)
        #Dump of the source code
        filename = os.path.join(self.dev_folder, 'source.html')
        with open(filename, 'wb') as f:
            f.write(self.soup.prettify().encode("utf-8"))
            self.gui.add_to_list(filename)
        #All the found urls
        filename = os.path.join(self.dev_folder, 'allURLs.txt')
        with open(filename, 'wb') as f:
            for url in set(self.urls):
                line = url + '\n'
                f.write(line.encode('utf-8'))
            self.gui.add_to_list(filename)
        if (len(self.img_urls) != 0):
            filename = os.path.join(self.dev_folder, 'imgURLs.txt')
            with open(filename, 'wb') as f:
                for url in set(self.img_urls):
                    line = url + '\n'
                    f.write(line.encode('utf-8'))
                self.gui.add_to_list(filename)
        if (len(self.doc_urls) != 0):
            filename = os.path.join(self.dev_folder, 'docURLs.txt')
            with open(filename, 'wb') as f:
                for url in set(self.doc_urls):
                    line = url + '\n'
                    f.write(line.encode('utf-8'))
                self.gui.add_to_list(filename)
        if (len(self.vid_urls) != 0):
            filename = os.path.join(self.dev_folder, 'vidURLs.txt')
            with open(filename, 'wb') as f:
                for url in self.vid_urls:
                    line = url + '\n'
                    f.write(line.encode('utf-8'))
                self.gui.add_to_list(filename)
        if (len(self.aud_urls) != 0):
            filename = os.path.join(self.dev_folder, 'audURLs.txt')
            with open(filename, 'wb') as f:
                for url in set(self.aud_urls):
                    line = url + '\n'
                    f.write(line.encode('utf-8'))
                self.gui.add_to_list(filename)
        scripts = self.soup.find_all('script')
        if scripts:
            filename = os.path.join(self.dev_folder, 'scripts.html')
            with open(filename, 'wb') as f:
                for script in scripts:
                    line = "\n" + script.prettify() + "\n" + "*"*80
                    f.write(line.encode('utf-8'))
                self.gui.add_to_list(filename)

    def output_results(self):
        self.create_dest_folders()
        if self.dev_run:
            self.gui.update_action("Extracting the webpage information...")
            self.output_dev()
            print()
        if self.img_run:
            self.download_links(self.img_urls, self.img_types, self.img_folder)
            print()
        if self.doc_run:
            self.download_links(self.doc_urls, self.doc_types, self.doc_folder)
            print()
        if self.vid_run:
            print("Trying to extract video using youtube_dl...")
            self.gui.update_action("Trying to extract video using youtube_dl...")
            self.ydl_download_video_urls()
            print()
        if self.aud_run:
            self.download_links(self.aud_urls, self.aud_types, self.aud_folder)
            print()
            print("Trying to extract audios using youtube_dl...")
            self.gui.update_action("Trying to extract audio using youtube_dl...")
            self.ydl_download_audio_urls()
            print()
        self.rm_empty_dirs()
        print("Done.")
        self.gui.update_values(url=self.site, action="Done.")
        nbr_files, total_size = self.get_folder_info(self.downloadpath)
        runtime = time.perf_counter() - self.start_time
        self.gui.set_stopevent(files=nbr_files, size=total_size, time=runtime)

    def open_path(self):
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2": # linux
            subprocess.Popen(["xdg-open", self.downloadpath])
        elif _platform == "darwin": # MAC OS X
            subprocess.Popen(["open", self.downloadpath])
        elif _platform == "win32" or _platform == "win64": # Windows
            os.startfile(self.downloadpath)

    def get_folder_info(self, path):
        total_size = 0
        nbr_files = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                nbr_files += 1
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return nbr_files, total_size

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

    def delete_file(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    site = 'https://www.blocket.se/malmo/Mini_Cooper_Clubman_Pepper_120hk_6_vaxl_82169382.htm?ca=23_11&w=0'
    site = 'https://m2.ikea.com/se/sv/campaigns/nytt-laegre-pris-pub3c9e0c81' #js rendered page
    site = "https://www.youtube.com/watch?v=JR0BYMDWmVo"
    site = 'http://cs.lth.se/edan20/'
    site = 'https://www.bytbil.com/'
    site = "https://www3059.playercdn.net/1p-dl/0/-Yr5ejWImiGKNAQLwzX1Lw/1546394162/181101/498FWSRGZAZLCRFC4PCAP.mp4?name=anime_105980.mp4-720.mp4"
    site = "https://www.eit.lth.se/fileadmin/eit/courses/etsf10/ht18/Exercises/KRplusextraTut3solutions.pdf"
    site = 'https://www.dplay.se/videos/stories-from-norway/stories-from-norway-102'
    site = 'https://www.nordea.se/'
    site = "https://www.rapidvideo.com/e/FYOIHWGHES"
    site = "https://soundcloud.com/jahseh-onfroy/bad"
    site = "https://www.youtube.com/watch?v=VWIHxYvo6dk"
    site = "https://www09.gogoanimes.tv/tonari-seki-kun-episode-1"
    site = "https://www09.gogoanimes.tv/hetalia-axis-powers-episode-1"
    site = "https://github.com/harvitronix/neural-network-genetic-algorithm" #debugg docs
    site = "https://vidstream.co/download?id=MTE0MTM0&typesub=Gogoanime-SUB&title=Tate+no+Yuusha+no+Nariagari+Episode+8"
    site = "https://www.rapidvideo.com/d/G0MW1FLIA5"
    site = 'https://www.youtube.com/watch?v=zmr2I8caF0c' #small

    path = "wedi_downloads"
    extensive = False
    img_types = ['jpg', 'jpeg', 'png', 'gif', 'svg']
    doc_types = ['txt', 'py', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
    vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp', 'webm', 'ogg']
    aud_types = ['mp3', 'aac', 'wma', 'wav', 'm4a']
    img_settings = {'run':False, 'img_types':img_types}
    doc_settings = {'run':False, 'doc_types':doc_types}
    vid_settings = {'run':True, 'vid_types':vid_types, 'format':'best'}
    aud_settings = {'run':False, 'aud_types':aud_types}
    dev_settings = {'run':True}
    settings = {'path':path, 'extensive':extensive, 'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audios':aud_settings, 'dev':dev_settings}
    services = services(site, settings)
    services.run()
