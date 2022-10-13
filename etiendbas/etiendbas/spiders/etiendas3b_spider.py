from unicodedata import category
import scrapy
import datetime
import json
import re




class ElektraSpider(scrapy.spiders.SitemapSpider):
    name = "elektra"
    sitemap_urls = ['https://www.etiendas3b.com.mx/sitemap-tiendas3b.xml']
    sitemap_rules = [('/producto', 'parse')]


    def parse(self, response):
        print(response)
        ans = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
        try:
            json_file = json.loads(ans)
        except Exception as e:
            with open("error.txt", "a") as f:
                f.write(str(e) + "\n")
            return

        try:
            item = dict()
            item['Date'] = datetime.datetime.now().strftime("%d/%m/%Y")
            item['Canal'] = 'Etiendas3b'
            breadcrumb_list = response.xpath('//div[contains(@class,"feature")]//text()').extract()
            category = ''
            sub_category = ''
            sub_category_2 = ''

            for i in range(len(breadcrumb_list)):
                if(breadcrumb_list[i] == 'Categorías: '):
                    catgories_array = breadcrumb_list[i+1].split(',', 4)
                    category = catgories_array[0].strip()
                    sub_category = '' if(len(catgories_array) == 1 ) else catgories_array[1].strip()
                    sub_category_2 = '' if(len(catgories_array) < 3 ) else catgories_array[2].strip()
                    break

            # breadcrumb_json = {x:y for x,y in enumerate(breadcrumb_list)}
            # item['Category'] = breadcrumb_list
            item['Category'] = category
            item['Subcategory'] = sub_category
            item['Subcategory2'] = sub_category_2
            # item['Subcategory3'] = breadcrumb_json.get(3)
            brand_name = json_file['brand']
            item['Marca'] = brand_name if brand_name else ''
            item['Modelo'] = json_file['name'].split(',', 1)[0]
            item['SKU'] =  json_file['sku']
            upc = response.xpath('//div[contains(@class,"text-light-slate")]//text()').extract_first()
            item['UPC'] = upc.strip()
            item['Item'] = json_file['name']
            item['Item Characteristics'] = json_file.get('description')
            item['URL SKU'] = response.url
            item['Image'] = json_file.get('image')
            item['Price'] = json_file['offers']['price']
            item['Sales Price'] = json_file['offers']['price']
            item['Shipment Cost'] = ''
            item['Sales Flag'] = response.xpath("//span[contains(@class,'savingsPercentage')]/text()").extract_first()
            item['Store ID'] = ''
            item['Store Name'] = ''
            item['Store Address'] = ''
            item['Stock'] = 'InStock' if json_file['offers']['availability'].find('InStock') != -1 else 'Sold Out'
            item['UPC WM'] = item['UPC'][-12:]
            item['Final Price'] =json_file['offers']['price']
            # with open('another_log.txt','a') as new_error:
            #     new_error.write(item + '\n')
        except Exception as e:
            with open('another_error.txt','a') as new_error:
                new_error.write(str(e) + '\n')
        yield item
