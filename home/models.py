from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    style_nr = models.IntegerField(unique= True)
    style_catalog_page = models.IntegerField()
    supplier_code = models.CharField(max_length=20)
    supplier_article_code = models.CharField(max_length=20)
    brand_code = models.CharField(max_length = 20)
    brand_name = models.CharField(max_length = 20)
    style_name = models.CharField(max_length = 255)
    style_description = models.TextField()
    style_category_main = models.CharField(max_length = 50)

class Product_Filter_Group(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    filter_group = models.CharField(max_length=50)   

class Product_Filter(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    filter_content = models.CharField(max_length = 250)
    filter_id = models.BigIntegerField()
    product_id = models.BigIntegerField()

class Product_Picture(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    product_id = models.BigIntegerField()
    filename = models.CharField(max_length=250)
    pos = models.IntegerField()
    url = models.CharField(max_length=250)
    local_url = models.CharField(max_length=250)

class Product_Subcategory(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    product_id = models.BigIntegerField()
    category_name = models.CharField(max_length=250)

class SKU(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    sku_artnum = models.IntegerField()
    sku_color_code = models.CharField(max_length = 20)
    sku_color_name = models.CharField(max_length = 50)
    sku_color_swatch = models.CharField(max_length = 100)
    sku_color_swatch_url = models.CharField(max_length = 250)
    sku_color_swatch_local = models.CharField(max_length = 100)
    sku_color_picture = models.CharField(max_length = 100)
    sku_color_picture_url = models.CharField(max_length = 250)
    sku_color_picture_local = models.CharField(max_length = 100)
    sku_size_code = models.CharField(max_length = 50)
    sku_size_name = models.CharField(max_length = 50)
    sku_size_order = models.IntegerField()
    sku_changed_date = models.CharField(max_length = 50)
    sku_closeout = models.CharField(max_length = 50)
    sku_new = models.CharField(max_length = 50)
    sku_ean = models.CharField(max_length = 50)
    sku_weight = models.CharField(max_length = 50)
    sku_coo = models.CharField(max_length = 50)
    sku_pieces_in_pack = models.IntegerField()
    sku_pieces_in_carton = models.IntegerField()
    price_currency = models.CharField(max_length = 50)
    price_exchange_rate = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_g = models.IntegerField()
    stock_y = models.IntegerField()
    stock_b = models.IntegerField()
    product_id = models.BigIntegerField()

