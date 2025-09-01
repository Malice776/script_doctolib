import argparse
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager




def scrape_doctolib(query, location, max_results, start_date, end_date,
                    assurance, consultation, price_min, price_max, address_filter):
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.doctolib.fr/")

    # Accepter ou refuser les cookies.
    try:
        reject_btn = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-disagree-button")))
        reject_btn.click()
    except:
        pass

    # Requête médicale
    search_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iinput.searchbar-input.searchbar-place-input"))
    )
    search_input.clear()
    search_input.send_keys(query)
    time.sleep(1)
    search_input.send_keys(Keys.ENTER)

    # Localisation
    place_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input"))
    )
    place_input.clear()
    place_input.send_keys(location)
    place_input.send_keys(Keys.ENTER)

    time.sleep(3)  # attendre chargement

    # TODO : appliquer les filtres Selenium ici (assurance, visio/sur place, prix, dates, adresse)
    # ⚠️ Chaque filtre doit être mappé au bon bouton/checkbox dans l’UI

    # Extraction résultats
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

            # Appliquer filtres manuels Python (ex : prix ou adresse)
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

    parser = argparse.ArgumentParser(description="Scraper Doctolib avec Selenium")
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
    print("✅ Fichier doctolib.csv généré.")
