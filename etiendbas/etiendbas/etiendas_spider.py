from unicodedata import category
import scrapy
import requests
import datetime
import json
import re

class EtiendasSpider(scrapy.spiders.SitemapSpider):
    name = "elektra"
    sitemap_urls = ['https://www.etiendas3b.com.mx/sitemap-tiendas3b.xml']
    sitemap_rules = [('/categoria', 'parse')]

    headers = {
        'authority': 'tiendas3b.api.t3b.katapultcommerce.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        'origin': 'https://www.etiendas3b.com.mx',
        'referer': 'https://www.etiendas3b.com.mx/',
        'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42',
    }

    def get_address(self):
        json_data = {
            'address': 'Coahuila 187',
            'city': 'Ciudad de México',
            'zipCode': '06700',
        }

        response = requests.post('https://tiendas3b.api.t3b.katapultcommerce.com/api/alliances/b61cfe54-0cb5-4370-8b1d-27a43224ab0c/geocoding/', headers=EtiendasSpider.headers, json=json_data)

        return response.json()
    
    def get_store(self):
        json_data = self.get_address()

        response = requests.post('https://tiendas3b.api.t3b.katapultcommerce.com/api/alliances/b61cfe54-0cb5-4370-8b1d-27a43224ab0c/stores/nearest/', headers=EtiendasSpider.headers, json=json_data)

        return response.json()

    def parse(self, response):
        try:
            category = response.url.rsplit('/', 1)[-1]
            store_data = self.get_store()
            store_json_data = {
                "storeIds": store_data['storesForSearch'],
                "storesForSearch": store_data['storesForSearch'],
                "categories_slug":[category,]
            }
            print(store_json_data)
            products = requests.post('https://tiendas3b.api.t3b.katapultcommerce.com/api/alliances/b61cfe54-0cb5-4370-8b1d-27a43224ab0c/products/query_search/?page=1&per-page=1000', headers=EtiendasSpider.headers, json=store_json_data)

            products_json = products.json()['queryResult']['records']
        except Exception as e:
            with open("error.txt", "a") as f:
                f.write(str(e) + "\n")
            return
        
        for product in products_json:
            try:
                item = dict()
                item['Date'] = datetime.datetime.now().strftime("%d/%m/%Y")
                item['Canal'] = 'Etiendas3b'
                catgories_array = product['categories']
                category = catgories_array[0].strip()
                sub_category = '' if(len(catgories_array) == 1 ) else catgories_array[1].strip()
                sub_category_2 = '' if(len(catgories_array) < 3 ) else catgories_array[2].strip()
                item['Category'] = category
                item['Subcategory'] = sub_category
                item['Subcategory2'] = sub_category_2
                item['Marca'] = product['productBrand']
                item['Modelo'] = product['productName'].split(',', 1)[0]
                item['SKU'] =  product['productSku']
                item['UPC'] = product['productUpc']
                item['Item'] = product['productName']
                # item['Item Characteristics'] = json_file.get('description')
                item['URL SKU'] = 'https://www.etiendas3b.com.mx/producto/'+product['productSlug']
                item['Image'] = [product['productImage'],]
                item['Price'] = product['productPrice']
                item['Sales Price'] = product['productPumValue']
                # item['Shipment Cost'] = ''
                item['Sales Flag'] = product['productPromotionElement']
                item['Store ID'] = store_data['storesForSearch']
                item['Store Name'] = ''
                item['Store Address'] = ''
                item['Stock'] = product['isActive']
                item['UPC WM'] = product['productUpc']
                item['Final Price'] = product['productPrice']
                
                yield item
                
            except Exception as e:
                with open('another_error.txt','a') as new_error:
                    new_error.write(str(e) + '\n')
