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


def scrape_doctolib(query, location, max_results, start_date, end_date,
                    assurance, consultation, price_min, price_max, address_filter): 


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
    

    # métier
    
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



    #liste des filstres

    if assurance:
        try:
            if assurance.lower() == "secteur 1":
                driver.find_element(By.XPATH, "//label[contains(., 'Secteur 1')]").click()
            elif assurance.lower() == "secteur 2":
                driver.find_element(By.XPATH, "//label[contains(., 'Secteur 2')]").click()
            elif assurance.lower() == "non conventionné":
                driver.find_element(By.XPATH, "//label[contains(., 'Non conventionné')]").click()
        except Exception as e:
            print(f"Erreur en sélectionnant l'assurance : {e}")
       
    if consultation:
        try:
            if consultation.lower() == "visio":
                driver.find_element(By.XPATH, "//label[contains(., 'Consultation vidéo')]").click()
            elif consultation.lower() == "sur place":
                driver.find_element(By.XPATH, "//label[contains(., 'En cabinet')]").click()
        except Exception as e:
            print(f"Erreur en sélectionnant le type de consultation : {e}")

            if start_date or end_date:
                try:
                    import datetime
                    from datetime import datetime as dt

                    # Exemple : 'Disponibilités le ven. 12 sept. à 09:00'
                    dispo_date_match = re.search(r"(\d{1,2}) (\w+) à", availability)
                    if dispo_date_match:
                        day = dispo_date_match.group(1)
                        month_str = dispo_date_match.group(2).lower()
                        month_dict = {
                            "janv.": 1, "févr.": 2, "mars": 3, "avr.": 4, "mai": 5,
                            "juin": 6, "juil.": 7, "août": 8, "sept.": 9,
                            "oct.": 10, "nov.": 11, "déc.": 12
                        }
                        month = month_dict.get(month_str)
                        if not month:
                            continue

                        year = datetime.datetime.now().year
                        date_obj = dt(year, month, int(day))

                        if start_date:
                            start = dt.strptime(start_date, "%d/%m/%Y")
                            if date_obj < start:
                                continue
                        if end_date:
                            end = dt.strptime(end_date, "%d/%m/%Y")
                            if date_obj > end:
                                continue
                except Exception as e:
                    print(f"Erreur lors du filtrage par date : {e}")



    
    time.sleep(60)
    results = []
    doctors = driver.find_elements(By.CSS_SELECTOR, "div.dl-search-result")[:max_results]

    for doc in doctors:
        try:
            name = doc.find_element(By.CSS_SELECTOR, "h3.dl-search-result-name").text
            try:
                availability = doc.find_element(By.CSS_SELECTOR, ".dl-search-result-availability").text
            except:
                availability = "Non dispo"
            consultation_type = "Vidéo" if "vidéo" in doc.text.lower() else "Sur place"
            try:
                sector = doc.find_element(By.CSS_SELECTOR, ".dl-search-result-sector").text
            except:
                sector = "Non précisé"
            try:
                price = doc.find_element(By.CSS_SELECTOR, ".dl-search-result-price").text
            except:
                price = "N/A"
            try:
                address = doc.find_element(By.CSS_SELECTOR, ".dl-text.dl-text-body.dl-text-regular").text
            except:
                address = "Non précisée"

            
            if price != "N/A":
                try:
                    price_val = int(price.split("€")[0].strip())
                    if (price_min and price_val < price_min) or (price_max and price_val > price_max):
                        continue
                except:
                    pass
            if address_filter and address_filter.lower() not in address.lower():
                continue

            results.append({
                "Nom": name,
                "Disponibilité": availability,
                "Consultation": consultation_type,
                "Secteur": sector,
                "Prix": price,
                "Adresse": address,
            })
        except:
            continue

    driver.quit()
    return results


def save_csv(data, filename="doctolib.csv"):
    if not data:
        print("Aucun médecin trouvé.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Doctolib for doctors based on criteria.")

    parser.add_argument("--query", required=True, help="Requête médicale (ex: dermatologue)")
    parser.add_argument("--location", required=True, help="Lieu de recherche (ex: 75015, Paris)")
    parser.add_argument("--max", type=int, default=10, help="Nombre max de médecins")
    parser.add_argument("--start", help="Date début (JJ/MM/AAAA)")
    parser.add_argument("--end", help="Date fin (JJ/MM/AAAA)")
    parser.add_argument("--assurance", choices=["secteur 1", "secteur 2", "non conventionné"], help="Type d'assurance")
    parser.add_argument("--consultation", choices=["visio", "sur place"], help="Type de consultation")
    parser.add_argument("--price-min", type=int, help="Prix minimum (€)")
    parser.add_argument("--price-max", type=int, help="Prix maximum (€)")
    parser.add_argument("--address-filter", help="Filtre d'adresse (ex: Vaugirard, 75015, Boulogne)")
    args = parser.parse_args()


    data = scrape_doctolib(
        args.query, args.location, args.max, args.start, args.end,
        args.assurance, args.consultation, args.price_min, args.price_max, args.address_filter
    )
    save_csv(data)

driver.quit()