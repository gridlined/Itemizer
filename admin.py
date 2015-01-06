from django.contrib import admin

from models import Supplier, Tax, ProductType, Product, Item, Fee, Discount, TaxCharge, Gratuity, Receipt


class ItemTabularAdmin(admin.TabularInline):
    model = Item
    extra = 1


class FeeTabularAdmin(admin.TabularInline):
    model = Fee
    extra = 0


class DiscountTabularAdmin(admin.TabularInline):
    model = Discount
    extra = 0


class TaxChargeTabularAdmin(admin.TabularInline):
    model = TaxCharge
    extra = 1


class GratuityTabularAdmin(admin.TabularInline):
    model = Gratuity
    extra = 0


class ReceiptAdmin(admin.ModelAdmin):
    inlines = [
        ItemTabularAdmin,
        FeeTabularAdmin,
        DiscountTabularAdmin,
        TaxChargeTabularAdmin,
        GratuityTabularAdmin,
        ]
    list_display = ("when", "supplier", "subtotal_usd", "tax_usd", "discount_usd", "tip_usd", "total_usd")
    list_display_links = ("when", "supplier")
    list_filter = ("date", "supplier")


admin.site.register(Supplier)
admin.site.register(Tax)
admin.site.register(ProductType)
admin.site.register(Product)
admin.site.register(Receipt, ReceiptAdmin)
