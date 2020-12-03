from selenium import  webdriver

driver = webdriver.Chrome(executable_path="./chromeDriver/chromedriver.exe")

driver.get("http://www.baidu.com")