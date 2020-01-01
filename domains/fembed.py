import os
import requests
import urllib.request


class Fembed:

    def extract_digits(self, data):
        return int(''.join(filter(str.isdigit, data)))

    def get_urls_by_ascending_quality_order(self, data):
        data = [value["file"] for value in sorted(data, key=lambda item: self.extract_digits(item["label"]))]
        return data

    def get_redirected_url(self, url):
        response = urllib.request.urlopen(url)
        return response.geturl()

    def apply_domian_rules(self, url, settings):
        media_id = os.path.basename(url)
        url = "https://gcloud.live/api/source/" + media_id
        response = requests.post(url)
        if response.status_code != requests.codes["ok"] or not response.json()["success"]:
            return url
        urls = self.get_urls_by_ascending_quality_order(response.json()["data"])
        
        if settings["videos"]["format"] == "worst": 
            url = urls[0]
        else:
            url = urls[len(urls)-1]
        url = self.get_redirected_url(url)
        return url
