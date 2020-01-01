class Github:
    def apply_domian_rules(self, url):
        url = url.replace('https://github.com/', 'https://raw.github.com/')
        url = url .replace('blob/', '')
        return url
