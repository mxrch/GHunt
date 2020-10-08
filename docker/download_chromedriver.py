import chromedriver_autoinstaller
import os
import stat

from chromedriver_autoinstaller.utils import get_chrome_version, get_major_version
from selenium import webdriver


dir_path = os.path.dirname(os.path.realpath(__file__))
chrome_major_version = get_major_version(get_chrome_version())
final_chromedriver_path = dir_path + '/' + 'chromedriver'

print(f'Downloading ChromeDriver for the installed Chrome version ({chrome_major_version})...')
chromedriver_autoinstaller.install(True)
os.rename(dir_path + '/' + chrome_major_version + '/chromedriver', final_chromedriver_path)
st = os.stat(final_chromedriver_path)
os.chmod(final_chromedriver_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.rmdir(dir_path + '/' + chrome_major_version)

print('ChromeDriver download was successful.')
