from django import forms
from django.contrib import admin

from dal import autocomplete

from .models import (Supplier, Tax, ProductType, Product, Item, Fee, Discount, TaxCharge, Gratuity, PaymentMethodType,
                     PaymentMethod, Payment, Receipt)


class ItemAdminForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("__all__")
        widgets = {
            "product": autocomplete.ModelSelect2(url="mizer_product_search")
        }


class ReceiptAdminForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ("__all__")
        widgets = {
            "supplier": autocomplete.ModelSelect2(url="mizer_supplier_search")
        }


class ItemTabularAdmin(admin.TabularInline):
    form = ItemAdminForm
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


class PaymentTabularAdmin(admin.TabularInline):
    model = Payment
    extra = 0


class ReceiptAdmin(admin.ModelAdmin):
    form = ReceiptAdminForm
    inlines = [
        ItemTabularAdmin,
        FeeTabularAdmin,
        DiscountTabularAdmin,
        TaxChargeTabularAdmin,
        GratuityTabularAdmin,
        PaymentTabularAdmin,
        ]
    date_hierarchy = "date"
    list_display = ("when", "supplier", "subtotal_usd", "tax_usd", "discount_usd", "tip_usd", "total_usd", "status")
    list_display_links = ("when", "supplier")
    list_filter = ("date", "supplier")


admin.site.register(Supplier)
admin.site.register(Tax)
admin.site.register(ProductType)
admin.site.register(Product)
admin.site.register(PaymentMethodType)
admin.site.register(PaymentMethod)
admin.site.register(Receipt, ReceiptAdmin)
