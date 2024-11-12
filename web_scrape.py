# coding: utf-8
from selenium import webdriver
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import re
import numpy as np
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import pandas
import csv


#driver = r"C:\\webdrivers.exe".replace("\\", "/")
# # Set webdriver path here, it may vary
#browser = webdriver.Chrome(options={driver_path:driver_path})
website_URL = "https://www.amazon.in/"
browser = webdriver.Chrome()
browser.get(website_URL)
time.sleep(9)

# Navigate to the product page
best_sellers_link = browser.find_element(By.LINK_TEXT, "Best Sellers")

# Alternatively, you can find the anchor tag by its attributes
best_sellers_link = browser.find_element(By.CSS_SELECTOR, 'a[href="/gp/bestsellers/?ref_=nav_cs_bestsellers"]')

# Perform actions with the anchor tag, such as clicking it
best_sellers_link.click()
time.sleep(1)

'''
# Find the anchor tag with the text "Books"
books_link = browser.find_element(By.LINK_TEXT, "Books")
books_link = browser.find_element(By.CSS_SELECTOR, 'a[href="/gp/bestsellers/books/ref=zg_bs_nav_books_0"]')
# Click on the "Books" link to navigate to the bestseller books section
books_link.click()
time.sleep(1)
'''
# Find the anchor tag with the text "Books"
clothes_link = browser.find_element(By.LINK_TEXT, "Clothing & Accessories")
clothes_link = browser.find_element(By.CSS_SELECTOR, 'a[href="/gp/bestsellers/apparel/ref=zg_bs_nav_apparel_0"]')
clothes_link.click()
time.sleep(1)

def scrape_product_details(num_products):
    wait = WebDriverWait(browser, 10)  # Adjust the timeout as needed
    
    for i in range(0, num_products + 1):
        xpath = '//*[@id="p13n-asin-index-' + str(i) + '"]'
        
        try:
            # Wait for the clothes item to be clickable
            clothes_item = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            clothes_item.click()
            
            time.sleep(1)  # Add a short delay for the page to load

            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract product details
            product_title_element = soup.find('span', {'id': 'productTitle'})
            product_name = product_title_element.text.strip() if product_title_element else "Null"
            
            # Extract other product details similarly...
            product_subtitle_element = soup.find('span', {'id': 'productSubtitle'})
            product_subtitle = product_subtitle_element.text.strip() if product_subtitle_element else " "

            price_parent_element = soup.find('div', class_='a-section a-spacing-none aok-align-center aok-relative')
            symbol = "Rs."  # Example symbol if found
            if price_parent_element:
                # If the element is found, proceed to extract the price
                price_element = price_parent_element.find('span', class_='a-price-whole')
                price = price_element.text.strip() if price_element else "Null"
            else:
                # Handle case when element is not found
                price = "Null"

            # Extract the discount percentage
            discount_parent_element = soup.find('div', class_='a-section a-spacing-none aok-align-center aok-relative')

            if discount_parent_element:
                discount_element = discount_parent_element.find('span', class_='a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage')
                discount = discount_element.text.strip() if discount_element else "Null"
            else:
                discount = "Null"
            
                                
            # Extract the MRP price
            mrp_parent_element = soup.find('div', class_='a-section a-spacing-small aok-align-center')

            if mrp_parent_element:
                mrp_element = mrp_parent_element.find('span', class_='a-offscreen')
                mrp_price = mrp_element.text.strip() if mrp_element else "Null"
                # Replace the currency symbol
                mrp_price = mrp_price.replace('₹', 'Rs.')
            else:
                mrp_price = "Null"
            
            mrp_price_numeric = int(mrp_price.replace('Rs.', '').replace(',', ''))
            # Check if both price and discount are not "Null"
            if price != "Null" and discount != "Null":
                # Convert price and discount to numbers for calculation
                price_numeric = int(price.replace('Rs.', '').replace(',', ''))                   
                # Calculate the discount price
                discount_amount = (mrp_price_numeric - price_numeric)
                # Format the discount price with currency symbol and decimal places
                
            
            # Find the parent element containing the author information
            author_parent_element = soup.find('div', id='bylineInfo_feature_div')

            # Check if the parent element exists and then find the author element within it
            if author_parent_element:
                author_element = author_parent_element.find('a', class_='a-link-normal')
                # Extract the author's name if the author element is found
                author_name = author_element.text.strip() if author_element else "Null"
            else:
                author_name = "Null"
            
            if "Visit the" in author_name:
                author_name = author_name.replace("Visit the", "").replace("Store", "").strip()
                
            elif "Brand: " in author_name:
                author_name = author_name.replace("Brand: ", "").strip()
                

            # Rating of the Book
            # Find the parent element containing the average customer reviews
            reviews_parent_element = soup.find('div', id='averageCustomerReviews')

            # Check if the parent element exists and then find the elements within it
            if reviews_parent_element:
                # Extract the average rating
                average_rating_element = reviews_parent_element.find('span', class_='a-size-base a-color-base')
                Rating_of_5stars = average_rating_element.text.strip() if average_rating_element else "Null"

                # Extract the number of ratings
                num_ratings_element = reviews_parent_element.find('span', id='acrCustomerReviewText')
                num_ratings = num_ratings_element.text.strip() if num_ratings_element else "Null"

                # Check if there are digits in the 'num_ratings' string before extracting
                if re.search(r'\d+', num_ratings):
                    ratings_integer = int(re.search(r'\d+', num_ratings).group())
                else:
                    ratings_integer = 0

            sales_parent_tag = soup.find('div', id = "socialProofingAsinFaceout_feature_div")
            if sales_parent_tag:
                sales_parent = sales_parent_tag.find('span',id="social-proofing-faceout-title-tk_bought")
                if sales_parent:
                    sales_data_element = sales_parent.find('span',class_="a-text-bold")
                    sales_data = sales_data_element.text.strip() if sales_data_element else "null"       

            Current_Url = browser.current_url
            # Find the index of "/dp/" in the URL
            index_dp = Current_Url.find("/dp/") + len("/dp/")

            # Extract the substring after "/dp/"
            product_code = Current_Url[index_dp:].split("/")[0]
          
            amazon_reviews = "https://www.amazon.in/product-reviews/" + str(product_code)

            reviews_url = amazon_reviews           
            browser.get(reviews_url)
            time.sleep(4)

            page_source = browser.page_source
            soup2 = BeautifulSoup(page_source, 'html.parser')
            star_parent = soup2.find('table', class_= 'a-normal a-align-center a-spacing-base')

            # Extract additional information
            product_details = {}
            product_details_elements = soup.find_all('div', class_='a-fixed-left-grid product-facts-detail')
            for detail in product_details_elements:
                key_element = detail.find('span', class_='a-color-base')
                value_element = detail.find('span', class_='a-color-base', recursive=False)
                if key_element and value_element:
                    key = key_element.text.strip()
                    value = value_element.text.strip()
                    product_details[key] = value
            
                 
            if star_parent:
                percentage_tags = soup2.find_all('a', class_='a-link-normal')
                # Extract percentage values from the text of each Tag object
                percentages = []
                for tag in percentage_tags:
                    text = tag.get_text(strip=True)  # Get text content of the tag
                    percentage_match = re.search(r'\d+%', text)  # Find percentage pattern in the text
                    if percentage_match:
                        percentages.append(percentage_match.group())  # Add matched percentage to the list

                five_star_percent = percentages[0]
                four_star_percent = percentages[1]
                three_star_percent = percentages[2]
                two_star_percent = percentages[3]
                one_star_percent = percentages[4]
                  
            browser.back()

            five_star_num = int(five_star_percent[:-1])  # Remove "%" symbol at the
            four_star_num = int(four_star_percent[:-1])
            three_star_num = int(three_star_percent[:-1])
            two_star_num = int(two_star_percent[:-1])
            one_star_num = int(one_star_percent[:-1])  

            # Calculate the number of ratings for each star category
            five_star_ratings = (five_star_num / 100) * int(ratings_integer)
            four_star_ratings = (four_star_num / 100) * int(ratings_integer)
            three_star_ratings = (three_star_num / 100) * int(ratings_integer)
            two_star_ratings = (two_star_num / 100) * int(ratings_integer)
            one_star_ratings = (one_star_num / 100) * int(ratings_integer)

            # Get the current date
            current_date = datetime.now()

            # Subtract one month from the current date
            last_month_date = current_date - timedelta(days=current_date.day)

            # Get the name of the last month
            last_month_name = last_month_date.strftime('%B')
          
                                  
            # Define the fields and data to be written
            fields = ['Product Title', 'Brand', 'Product Price', 'Discount Percentage', 'Discount Amount', 'Product MRP','Ratings of 5 stars', 'Number of Ratings','Sales last month','5 stars in %','4 stars in %','3 stars in %','2 stars in %','1 star in %','5 star','4 star','3 star', '2 star','1 star']
            
            mydict = {'Product Title': f'{product_name} {product_subtitle}',
                    'Brand': f'{author_name}',
                    'Product Price': f'{symbol}{price}',
                    'Discount Percentage': f'{discount}',
                    'Discount Amount': f'-Rs{discount_amount}',
                    'Product MRP': f'{mrp_price}',
                    'Ratings of 5 stars': f'{Rating_of_5stars}',                                     
                    'Number of Ratings': f'{ratings_integer}',
                    'Sales last month': f'{sales_data} in {last_month_name}',
                    '5 stars in %' : f'{five_star_percent}',
                    '4 stars in %' : f'{four_star_percent}',
                    '3 stars in %' : f'{three_star_percent}',
                    '2 stars in %' : f'{two_star_percent}',
                    '1 star in %'  : f'{one_star_percent}',
                    '5 star' : f'{five_star_ratings}',
                    '4 star' : f'{four_star_ratings}',
                    '3 star' : f'{three_star_ratings}',
                    '2 star' : f'{two_star_ratings}',
                    '1 star' : f'{one_star_ratings}',
                                               
                    }

            # Name of CSV file
            filename = "clothes.csv"

            # Writing to CSV file
            with open(filename, 'a', newline='') as csvfile:
                # Creating a CSV writer object
                writer = csv.DictWriter(csvfile, fieldnames=fields)

                # Check if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()  # Write the header if the file is empty

                # Writing data row
                writer.writerow(mydict)  # Write product details to CSV file
            
                
        except Exception as e:
            print(f"Error occurred while scraping product {i}: {e}")
            
        finally:
            browser.back()  # Go back to the previous page to scrape the next product

# Example usage:
num_products = 49
scrape_product_details(num_products)
time.sleep(1)

# Find the next page link
next_page_link = browser.find_element(By.XPATH, '//li[@class="a-last"]/a')
# Click on the next page link to navigate to the next page
next_page_link.click()
time.sleep(1)

num_products = 49
scrape_product_details(num_products)

# Close the webdriver after scrape
browser.quit()
