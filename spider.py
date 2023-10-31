import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class Monitor:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        #chrome_options = Options()
        #chrome_options.add_argument('--headless')
        self.driver = webdriver.Firefox()
        self.driver.get("https://sdm.hk.esixcloud.net:20001/ui#/main-page")
        self.driver.implicitly_wait(0.5)

    def login(self):
        username = self.driver.find_element(by=By.XPATH, value="//input[@class='ant-input ant-input-lg'][@placeholder='' and @type='text']")
        password = self.driver.find_element(by=By.XPATH, value="//input[@class='ant-input ant-input-lg'][@placeholder='' and @type='password']")
        login_button = self.driver.find_element(by=By.XPATH, value="//button[@class='ant-btn ant-btn-primary ant-btn-lg ant-btn-primary' and @type='submit']")
        username.send_keys(self.username)
        password.send_keys(self.password)
        login_button.submit()
        time.sleep(3)
        if self.driver.title == 'SD-M Center':
            return 'Error: login failed'
        return 'Success'

    def get_device_status(self):
        result = self.check_login()
        if result.startswith('Error'):
            return [result]
        status = self.driver.find_elements(by=By.XPATH, value="//span[@class='ant-badge-status-text']")
        status_value = [one.text for one in status]
        return status_value
    
    def check_login(self):
        title = self.driver.title
        if title == 'SD-M Center':
            login_result = self.login()
            return login_result
        return 'Success'

