from selenium import webdriver
driver=webdriver.Edge(executable_path='msedgedriver.exe')
driver.maximize_window()
driver.get('https://cn.bing.com/')