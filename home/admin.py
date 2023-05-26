from django.contrib import admin

# Register your models here.
from .models import Product, Product_Filter, Product_Filter_Group, Product_Picture,Product_Subcategory,SKU

admin.site.register(Product)
admin.site.register(Product_Filter_Group)
admin.site.register(Product_Filter)
admin.site.register(Product_Picture)
admin.site.register(Product_Subcategory)
admin.site.register(SKU)

