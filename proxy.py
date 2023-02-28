from selenium import webdriver



def create_dict(proxies):
    proxy_dict = []
    for proxy in proxies:
        proxy_dict.append({'http': "http://" + proxy, 'https': "http://" + proxy})
    return proxy_dict


class ProxyDriver:
    def __init__(self, proxies, driver_path):
        self.proxies = create_dict(proxies)
        self.current_proxy = 0
        self.driver_path = driver_path
        self.driver = None

    def next(self):
        self.driver.quit()
        self.current_proxy += 1
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={self.proxies[self.current_proxy]}')
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=self.driver_path)

    def start(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={self.proxies[self.current_proxy]}')
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=self.driver_path)

    def get(self, url):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()