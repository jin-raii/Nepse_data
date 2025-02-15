
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import sys

def search(driver, date):
    """
    Date in mm/dd/yyyy
    """
    try:
        driver.get("https://merolagani.com/Floorsheet.aspx")
        try:
            alert = driver.switch_to.alert
            print(f'Alert detected {alert.text}')
            alert.dismis()
        except Exception as e:
            pass
        date_element_path = '/html/body/form/div[4]/div[4]/div/div/div[1]/div[4]/input'
        search_element_path2 = '/html/body/form/div[4]/div[4]/div/div/div[2]/a[1]'
        date_input = driver.find_element(By.XPATH, date_element_path)
        search_btn = driver.find_element(By.XPATH, search_element_path2)
        date_input.send_keys('02/13/2025')
        print(search_btn)
        search_btn.click()
    except Exception as e:
        print(e)
    # if driver.find_elements(By.XPATH, "//*[contains(text(), 'Could not find floorsheet matching the search criteria')]"):
    #     print("No data found for the given search.")
    #     print("Aborting script ......")
    #     sys.exit()


def get_page_table(driver, table_class):
    soup = BeautifulSoup(driver.page_source,'html')
    table = soup.find("table", {"class":table_class})
    tab_data = [[cell.text.replace('\r', '').replace('\n', '') for cell in row.find_all(["th","td"])]
                        for row in table.find_all("tr")]
    df = pd.DataFrame(tab_data)
    return df


def scrape_data(driver, date):
    start_time = datetime.now()
    search(driver,'02/13/2025')
    df = pd.DataFrame()
    while True:
        page_table_df = get_page_table(driver, table_class="table table-bordered table-striped table-hover sortable")
        print(type(page_table_df))
        
        if page_table_df is not None and not page_table_df.empty:
            df = pd.concat([df, page_table_df], ignore_index=True)
        print(df.head())
        try:
            next_btn = driver.find_element(By.LINK_TEXT, 'Next')
            driver.execute_script("arguments[0].click();", next_btn)
        except NoSuchElementException:
            break
    print(f"Time taken to scrape: {datetime.now() - start_time}")    
    return df

def clean_df(df):
    new_df = df.drop_duplicates(keep='first')
    new_header = new_df.iloc[0]
    new_df = new_df[1:]
    new_df.columns = new_header 
    new_df.drop(["#"], axis=1, inplace=True)
    new_df["Rate"] = new_df["Rate"].apply(lambda x:float(x.replace(",", "")))
    new_df["Amount"] = new_df["Amount"].apply(lambda x:float(x.replace(",", ""))) 
    return new_df


options = Options()
options.headless = True
options.add_argument('--disable-notifications')
driver = webdriver.Chrome(options=options)

date = datetime.today().strftime('%m/%d/%Y') 
search(driver, '02/13/2025') 
df = scrape_data(driver, date) 
final_df = clean_df(df) 

final_df.head()

file_name = date.replace("/", "_")
final_df.to_csv(f"data/{file_name}.csv", index=False) 

