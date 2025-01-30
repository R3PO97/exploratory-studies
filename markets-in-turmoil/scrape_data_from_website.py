from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_page(driver):
    results = []
    
    boxes = driver.find_elements(By.CLASS_NAME, "FluidCell-module_wrapper__XokYW")
    logging.info(f"Found {len(boxes)} boxes")
    
    main_tab = driver.current_window_handle # Store main tab
    
    for i, box in enumerate(boxes):
        try:
            # Scroll into view before clicking (boxes load dynamically)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", box)
            time.sleep(1) 
            
            # Open the link in a new tab
            ActionChains(driver).key_down(Keys.CONTROL).click(box).key_up(Keys.CONTROL).perform()
            logging.info(f"Opened box {i+1} in a new tab")
            
            # Switch to the new tab
            WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[1])
            
            # Wait for content to load
            wait = WebDriverWait(driver, 5)
            
            try:
                title = wait.until(EC.presence_of_element_located((By.XPATH, "//section/div[2]/div[1]/h1"))).text
                logging.info(f"Extracted Title: {title}")
            except Exception as e:
                title = "N/A"
                
            try:
                span_data = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/main/section/section/div[2]/div[6]/div/div[1]/div/span"))).text
                logging.info(f"Extracted Date: {span_data}")
            except Exception as e:
                span_data = "N/A"
            
            results.append({"title": title, "span_data": span_data})
            
            # Close the new tab and switch back to the original tab
            driver.close()
            driver.switch_to.window(main_tab)
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"Error on box {i+1}: {e}")
    return results

def main():
    # Setup WebDriver
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("-profile")
    options.add_argument("/home/mr-nice/snap/firefox/common/.mozilla/firefox/kqdwkkkk.default")

    
    driver = webdriver.Firefox(service=Service("/usr/local/bin/geckodriver"), options=options)
    driver.get("link_with_search_results")
    time.sleep(5) 
    
    all_results = []
    page_count = 0  
    
    while page_count < 2:  # Stop after visiting second page (current number of pages: 2)
        all_results.extend(scrape_page(driver))
        
        # Find and click the 'Next' button
        try:
            next_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/section/div[3]/div/div/nav/ul/button/div/span")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)

            ActionChains(driver).move_to_element(next_button).click().perform()
            time.sleep(5)

            page_count += 1
        except Exception as e:
            break
    
    driver.quit()
    
    # Save to CSV
    df = pd.DataFrame(all_results)
    df.to_csv("scraped_data.csv", index=False)

if __name__ == "__main__":
    main()
