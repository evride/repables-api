
import requests
from selenium import webdriver
from PIL import Image
#from Screenshot import Screenshot_clipping
import time
from utils import saveS3File
from pathlib import Path

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")


# initiating the webdriver. Parameter includes the path of the webdriver.

def render_model(filename: str, fileType: str):
    url = "http://render-model/?file=files/" + filename + "&type=" + fileType
    filenameBase = str(int(time.time() * 1000))
    rendered_files = [
        { "filename": filenameBase + '_large.png', "width":1440, "height":1080, "type": "large"},
        { "filename": filenameBase + '_medium.png', "width":1280, "height":960, "type": "medium"},
        { "filename": filenameBase + '_small.png', "width":640, "height":480, "type": "small"},
        { "filename": filenameBase + '_thumbnail.png', "width":320, "height":240, "type": "thumbnail"}
    ]
    driver = webdriver.Chrome(options=chrome_options)#'./chromedriver')
    driver.set_window_size(1440, 1080)
    driver.get(url)
    time.sleep(2)
    print(url)
    for render in rendered_files:
        driver.set_window_size(render["width"], render["height"])
        time.sleep(0.5)
        driver.save_screenshot("images/" + render['filename'])
        saveS3File("images/" + render['filename'], "images/" + render['filename'])
        Path("images/" + render['filename']).unlink()
    driver.close()
    return rendered_files
