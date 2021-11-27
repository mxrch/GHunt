from webdriver_manager.chrome import ChromeDriverManager

ChromeDriverManager(path="/usr/src/app").install()
print('ChromeDriver download was successful.')
