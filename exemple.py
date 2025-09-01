from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
 
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://www.doctolib.fr/")
 
wait = WebDriverWait(driver, 10)
 
try :
 
    reject_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "didomi-notice-disagree-button"))
    )
    reject_btn.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "didomi-notice-disagree-button")))
except:
    pass
 
place_input = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input"))
)
place_input.clear()
place_input.send_keys("75001")
wait.until(
    EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input"), "75001")
)
place_input.send_keys(Keys.ENTER)
 
time.sleep(60)
 
driver.quit()