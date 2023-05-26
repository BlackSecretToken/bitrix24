from django.shortcuts import render
import json
import base64
from fast_bitrix24 import Bitrix
from django.http import HttpResponse
import requests
import lxml.etree as ET
import decimal
from .models import Product, Product_Filter, Product_Filter_Group, Product_Picture, Product_Subcategory, SKU


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)

def test(request):
    bx24 = Bitrix('https://crm.grnstn.net/rest/245/jc6yzr6l1tvmih5t/')
    with open("c://1.jpg", 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        file_content = image_base64
        file_name = 'image.jpg'   

    print(file_content)

    bx24.call('crm.product.update',{
        'id': 298,
        'fields': {
            "PREVIEW_PICTURE": 
                {
                    'fileData': [
                        file_name, file_content
                    ]
                },
            "DETAIL_PICTURE": 
                 {
                    'fileData': [
                        file_name, file_content
                    ]
                }
            }
    })
    return HttpResponse('')  

def importProduct(request):
    bx24 = Bitrix24('https://crm.grnstn.net/rest/245/jibpk1zovvdu94it/')

    lang = 'de'
    data = json.loads(request.body.decode('utf-8'))
    importUrl = data.get('importUrl')
    response = requests.get(importUrl)
    text_data = response.text
    text_byte = text_data.encode('utf-8')
    root = ET.fromstring(text_byte)
    # get size of product
    export_data_date = root.find('export_data_date').text 
    file_version = root.find('file_version').text
    cnt_product = int(root.find('style_count').text)  
    styles = root.findall('style')

    ##### get price  ###############
    price_response = requests.get('https://300692-2-6n5hwe84:6fVeFb2F@ws.falk-ross.eu/ws/run/price.pl?format=xml&style=&action=get_price&ndp=1')
    price_text_data = price_response.text
    price_text_byte = price_text_data.encode('utf-8')
    price_root = ET.fromstring(price_text_byte)
    price_currency = price_root.find('currency').text
    price_exchange_rate = decimal.Decimal(price_root.find('exchange_rate').text)
    price_sku_list = price_root.find('sku_list')
    price_list = {}
    for price_sku in price_sku_list.findall('sku'):
        price_list[price_sku.find('sku_nr').text] = decimal.Decimal(price_sku.find('your_price').text )

    for i in range(1):
        style_nr = int(styles[i].find('style_nr').text )
        url_style_xml = styles[i].find('url_style_xml').text 
        
        ############## get Style data  #########################
        response = requests.get(url_style_xml)
        root_detail = ET.fromstring(response.text.encode('utf-8'))

        style_detail = root_detail.find('style')
        style_catalog_page = int(style_detail.find('style_catalog_page').text)
        supplier_code = style_detail.find('supplier_code').text
        supplier_article_code = style_detail.find('supplier_article_code').text
        brand_code = style_detail.find('brand_code').text
        brand_name = style_detail.find('brand_name').text

        style_name_info = style_detail.find('style_name')
        style_name_lang = style_name_info.find('language')
        style_name = style_name_lang.find(lang).text

        style_description_info = style_detail.find('style_description')
        style_description_lang = style_description_info.find('language')
        style_description = style_description_lang.find(lang).text

        style_category_list = style_detail.find('style_category_list')
        style_category_main_detail = style_category_list.find('style_category_main')
        style_category_main = style_category_main_detail.text 

        #####################  Save Product  ##########################
        product_exists = Product.objects.filter(style_nr=style_nr).exists()
        product_id = 0
        if product_exists:
            product = Product.objects.get(style_nr=style_nr)
            product.style_nr = style_nr
            product.style_catalog_page =style_catalog_page
            product.supplier_code =supplier_code
            product.supplier_article_code = supplier_article_code
            product.brand_code = brand_code
            product.brand_name = brand_name
            product.style_name = style_name
            product.style_description = style_description
            product.style_category_main = style_category_main
            product.save()
            product_id = product.id
        else:
            product = Product(style_nr = style_nr, style_catalog_page = style_catalog_page, supplier_code = supplier_code, supplier_article_code = supplier_article_code, brand_code = brand_code, brand_name = brand_name, style_name = style_name, style_description = style_description, style_category_main = style_category_main )
            product.save()
            product_id = product.id

        print('--------Product successfully saved to database')

        ### save product filter group ##############
        product_filter_group = Product_Filter_Group.objects.get_queryset()

        style_filter_list = style_detail.find('style_filter_list')
        
        for i in range(product_filter_group.count()):
            filter_data = []
            style_filter_group_list = style_filter_list.find(product_filter_group[i].filter_group+'_list')
            for style_color_group in style_filter_group_list.findall(product_filter_group[i].filter_group):
                filter_data.append(style_color_group.text)
            
            filter_data = ', '.join(str(x) for x in filter_data)

            ########## check exist ############################
            product_filter_exists = Product_Filter.objects.filter(product_id = product_id, filter_id = product_filter_group[i].id).exists()
            if product_filter_exists:
                product_filter = Product_Filter.objects.get(product_id = product_id, filter_id = product_filter_group[i].id)
                product_filter.filter_content = filter_data
                product_filter.save()
            else :
                product_filter = Product_Filter(product_id = product_id, filter_content = filter_data, filter_id = product_filter_group[i].id)
                product_filter.save()
            print('-------------- Product Filter Saved')
        
        ### save product subcategory  ################
        for style_category_sub in style_category_main_detail.findall('style_category_sub'):
            style_category_sub1= style_category_sub.find('language')
            category_name= style_category_sub1.find('de').text 
            product_subcategory = Product_Subcategory(product_id = product_id, category_name = category_name)
            product_subcategory.save()
            print('-------------- Product Subcategory Saved')

        ### upload image to local side ################
        style_picture_list = style_detail.find('style_picture_list')
        for style_picture in style_picture_list.findall('style_picture'):
            filename = style_picture.find('filename').text
            pos = style_picture.find('pos').text
            url = style_picture.find('url').text 
            product_picture = Product_Picture(filename = filename, pos = pos, url= url, local_url = '', product_id = product_id)
            product_picture.save()    

        ### Get stock data  ########
        stock_response = requests.get('https://300692-2-6n5hwe84:6fVeFb2F@ws.falk-ross.eu/webservice/R03_000/stockinfo/product/'+str(style_nr)+'?format=xml')
        stock_text_data = stock_response.text
        stock_text_byte = stock_text_data.encode('utf-8')
        stock_root = ET.fromstring(stock_text_byte)
        stock_product = stock_root.findall('product_variant')
        style_sku_list = style_detail.find('sku_list')
        style_sku = style_sku_list.findall('sku')
        cnt=0
        for stock_product_detail in stock_product:
            stock_g = stock_product_detail.find('g').find('Quantity').text 
            stock_y = stock_product_detail.find('g').find('Quantity').text 
            stock_b = stock_product_detail.find('g').find('Quantity').text
            style_sku_detail = style_sku[cnt]
            sku_artnum = style_sku_detail.find('sku_artnum').text
            sku_color_code = style_sku_detail.find('sku_color_code').text
            sku_color_name = style_sku_detail.find('sku_color_name').text
            sku_color_swatch = style_sku_detail.find('sku_color_swatch').text
            sku_color_swatch_url = style_sku_detail.find('sku_color_swatch_url').text
            sku_color_picture = style_sku_detail.find('sku_color_picture').text
            sku_size_code = style_sku_detail.find('sku_size_code').text
            sku_size_name = style_sku_detail.find('sku_size_name').text
            sku_size_order = style_sku_detail.find('sku_size_order').text
            sku_changed_date = style_sku_detail.find('sku_changed_date').text
            sku_closeout = style_sku_detail.find('sku_closeout').text
            sku_new = style_sku_detail.find('sku_new').text
            sku_ean = style_sku_detail.find('sku_ean').text
            sku_weight = style_sku_detail.find('sku_weight').text
            sku_coo = style_sku_detail.find('sku_coo').text
            sku_pieces_in_pack = style_sku_detail.find('sku_pieces_in_pack').text
            sku_pieces_in_carton = style_sku_detail.find('sku_pieces_in_carton').text
            
            sku_exists = SKU.objects.filter(sku_artnum=sku_artnum).exists()
            if sku_exists:
                sku_data = SKU.objects.get(sku_artnum=sku_artnum)
                sku_data.sku_artnum = sku_artnum
                sku_data.sku_color_code = sku_color_code,
                sku_data.sku_color_name = sku_color_name,
                sku_data.sku_color_swatch = sku_color_swatch,
                sku_data.sku_color_swatch_url = sku_color_swatch_url,
                sku_data.sku_color_picture = sku_color_picture,
                sku_data.sku_size_code = sku_size_code,
                sku_data.sku_size_name = sku_size_name,
                sku_data.sku_size_order = sku_size_order,
                sku_data.sku_changed_date = sku_changed_date,
                sku_data.sku_closeout = sku_closeout,
                sku_data.sku_new = sku_new,
                sku_data.sku_ean = sku_ean,
                sku_data.sku_weight = sku_weight,
                sku_data.sku_coo = sku_coo,
                sku_data.sku_pieces_in_pack = sku_pieces_in_pack,
                sku_data.sku_pieces_in_carton = sku_pieces_in_carton,
                sku_data.stock_g = stock_g,
                sku_data.stock_y = stock_y,
                sku_data.stock_b = stock_b,
                sku_data.price_exchange_rate = price_exchange_rate,
                sku_data.price_currency = price_currency,
                sku_data.price = price_list[sku_artnum],
                sku_data.product_id=product_id
                sku_data.save()
            else:
                sku_data = SKU(sku_artnum = sku_artnum, 
                           sku_color_code = sku_color_code,
                           sku_color_name = sku_color_name,
                           sku_color_swatch = sku_color_swatch,
                           sku_color_swatch_url = sku_color_swatch_url,
                           sku_color_picture = sku_color_picture,
                           sku_size_code = sku_size_code,
                           sku_size_name = sku_size_name,
                           sku_size_order = sku_size_order,
                           sku_changed_date = sku_changed_date,
                           sku_closeout = sku_closeout,
                           sku_new = sku_new,
                           sku_ean = sku_ean,
                           sku_weight = sku_weight,
                           sku_coo = sku_coo,
                           sku_pieces_in_pack = sku_pieces_in_pack,
                           sku_pieces_in_carton = sku_pieces_in_carton,
                           stock_g = stock_g,
                           stock_y = stock_y,
                           stock_b = stock_b,
                           price_exchange_rate = price_exchange_rate,
                           price_currency = price_currency,
                           price = price_list[sku_artnum],
                           product_id=product_id)
                sku_data.save()
            cnt = cnt + 1

        #### handle sku   ####################

        ##### stock product ##################
        # response = requests.get('https://300692-2-6n5hwe84:6fVeFb2F@ws.falk-ross.eu/webservice/R03_000/stockinfo/product/10209?format=xml')

        ##### stock price  ###################
        # response = requests.get('https://300692-2-6n5hwe84:6fVeFb2F@ws.falk-ross.eu/ws/run/price.pl?format=xml&style=&action=get_price&ndp=1')
    return HttpResponse(importUrl)  