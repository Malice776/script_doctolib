from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
 



def save_csv(data, filename="doctolib.csv"):
    if not data:
        print("Aucun médecin trouvé.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def scrape_doctolib(query, location):

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
    

    # localisation   
    
    place_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchbar-input.searchbar-query-input"))
    )
    place_input.clear()
    place_input.send_keys(query)
    time.sleep(1)
    place_input.send_keys(Keys.ENTER)

    
    # localisation   

    place_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input"))
    )
    place_input.clear()
    place_input.send_keys(location)
    time.sleep(1)
    place_input.send_keys(Keys.ENTER)
    place_input.send_keys(Keys.ENTER)


    time.sleep(1) # attendre chargement
    

    place_input2 = wait.until(
    EC.presence_of_element_located((By.XPATH, "//button[.//span[normalize-space()='Filtres']]"))
)
    place_input2.click()

    time.sleep(60)
 


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Doctolib for doctors based on criteria.")

    parser.add_argument("--query", required=True, help="Requête médicale (ex: dermatologue)")
    parser.add_argument("--location", required=True, help="Lieu de recherche (ex: 75015, Paris)")
    args = parser.parse_args()


    data = scrape_doctolib(
        args.query, args.location
    )
    save_csv(data)

driver.quit()