from datetime import date
from decimal import Decimal
from math import ceil
from os import path
from re import sub

from django.db import models
from django.core.validators import MinValueValidator


class utils():
    @staticmethod
    def to_usd(num):
        """Return a USD formatted string for the given numeric value
        
        >>> utils.to_usd(1)
        "$1.00"
        >>> utils.to_usd(5.2)
        "$5.20"
        >>> utils.to_usd(8.387)
        "$8.39"
        >>> utils.to_usd(4.961)
        "$4.96"
        >>> utils.to_usd(1234567890.12)
        "$1234567890.12"
        >>> utils.to_usd(-987.654)
        "-$987.65"
        """
        usd = "$%2.2f" % num
        if num < 0:
            usd = "-$%2.2f" % (num * -1)
        return usd

    @staticmethod
    def datestamp(date=date.today()):
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def clean_dirname(name):
        name = "%s" % name # ensure a string
        return sub(r"[^a-z0-9_-]", "_", name.lower())

    @staticmethod
    def build_image_path(filename, *args):
        """
        >>> utils.build_image_path("/path/to/image.gif")
        "/path/to/image.gif"
        >>> utils.build_image_path("/path/to/image.gif", "new")
        "new.gif"
        >>> utils.build_image_path("/path/to/image.gif", "new", "path", "parts")
        "new/path/parts.gif"
        >>> utils.build_image_path("/path/to/image.gif", "/new", "/path", "/parts")
        "/new/path/parts.gif"
        >>> utils.build_image_path("/path/to/image.gif", "/new", "/path", "/parts.jpg")
        "/new/path/parts.jpg.gif"
        """
        if args:
            (root, ext) = path.splitext(filename)
            arg_list = list(args)
            last_arg = arg_list.pop()
            arg_list.append("%s%s" % (last_arg, ext))
            args = tuple(arg_list)
            filename = path.join(*args)
        return filename

    @staticmethod
    def product_image_path(product, filename):
        """/path/to/media/product/12345/YYYY-mm-dd_productname"""
        product_name = utils.clean_dirname(product.name)
        datestamp = utils.datestamp()
        id = str(product.pk)
        representation = "%s_%s" % (datestamp, product_name)
        return utils.build_image_path(filename, "product", id, representation)

    @staticmethod
    def receipt_image_path(receipt, filename):
        """/path/to/media/receipt/YYYY/mm/dd/12345_suppliername_andcity"""
        year = receipt.date.strftime("%Y")
        month = receipt.date.strftime("%m")
        day  = receipt.date.strftime("%d")
        supplier = utils.clean_dirname(receipt.supplier)
        representation = "%i_%s" % (receipt.pk, supplier)
        return utils.build_image_path(filename, "receipt", year, month, day, representation)


class Tax(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "taxes"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    street = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def locality(self):
        return "%s, %s" % (self.city, self.state)

    def __str__(self):
        repr = self.name
        if (self.city):
            repr = "%s (%s)" % (self.name, self.locality())
        return repr

    class Meta:
        ordering = ("name", "state", "city",)


class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField("UPC / SKU / Product Code", max_length=25, null=True, blank=True)
    image = models.ImageField(upload_to=utils.product_image_path, null=True, blank=True)
    types = models.ManyToManyField("ProductType")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class PaymentMethodType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class PaymentMethod(models.Model):
    bank = models.CharField(max_length=100)
    last4 = models.CharField("Last 4", max_length=4, blank=True, null=True)
    type = models.ForeignKey("PaymentMethodType")

    def __str__(self):
        number = ""
        type = ""
        if self.last4:
            number = " x%s" % self.last4
        if self.bank != self.type:
            type = " (%s)" % self.type
        return "%s%s%s" % (self.bank, number, type)

    class Meta:
        ordering = ("bank", "type", "last4",)


class Payment(models.Model):
    receipt = models.ForeignKey("Receipt", related_name="payments")
    payment_method = models.ForeignKey("PaymentMethod")
    amount = models.DecimalField(
        default=1,
        max_digits=8,
        decimal_places=2)  # up to 999999.99


class Receipt(models.Model):
    supplier = models.ForeignKey("Supplier")
    date = models.DateField(null=False, blank=False, default=date.today)
    time = models.TimeField(null=True, blank=True)
    image = models.ImageField(upload_to=utils.receipt_image_path,
                              null=True, blank=True)

    @property
    def subtotal(self):
        cost = 0
        for item in self.items.all():
            cost += item.cost
        return cost

    def subtotal_usd(self):
        return utils.to_usd(self.subtotal)
    subtotal_usd.short_description = "Subtotal (USD)"

    @property
    def tax(self):
        cost = 0
        for tax in self.taxes.all():
            cost += tax.amount
        return cost

    def tax_usd(self):
        return utils.to_usd(self.tax)
    tax_usd.short_description = "Tax (USD)"

    @property
    def discount(self):
        amount = 0
        for coupon in self.discounts.all():
            amount += coupon.amount
        return amount

    def discount_usd(self):
        return utils.to_usd(self.discount)
    discount_usd.short_description = "Discount (USD)"

    @property
    def fee(self):
        amount = 0
        for fee in self.fees.all():
            amount += fee.amount
        return amount

    def fee_usd(self):
        return utils.to_usd(self.fee)
    fee_usd.short_description = "Fees (USD)"

    @property
    def tip(self):
        amount = 0
        for tip in self.gratuities.all():
            amount += tip.amount
        return amount

    def tip_usd(self):
        return utils.to_usd(self.tip)
    tip_usd.short_description = "Tip (USD)"

    @property
    def total(self):
        return (self.subtotal
                + self.fee
                - self.discount
                + self.tax
                + self.tip)

    def total_usd(self):
        return utils.to_usd(self.total)
    total_usd.short_description = "Total (USD)"

    @property
    def when(self):
        when = "%s" % self.date
        if self.time:
            when = "%s %s:%s%s" % (
                when,
                self.time.strftime("%I").lstrip("0"),
                ("%i" % self.time.minute).rjust(2, "0"),
                self.time.strftime("%p").lower())
        return when

    def status(self):
        status = ""
        if (self.payments.count() > 0):
            paid = self.payments.all().aggregate(total=models.Sum(models.F('amount')))
            total = paid["total"]
            if total < self.total:
                status = "Underpaid"
            elif total > self.total:
                status = "Overpaid"
            elif total < 0:
                status = "Refunded"
            else:
                status = "Paid"

        return status

    def __str__(self):
        return "%s - %s - %s (%s)" % (self.when, self.supplier, self.total_usd(), self.status())

    class Meta:
        ordering = ('-date', '-time',)


class Item(models.Model):
    product = models.ForeignKey("Product", related_name="purchases")
    receipt = models.ForeignKey("Receipt", related_name="items")
    quantity = models.DecimalField(
        default=1,
        max_digits=9,
        decimal_places=3)  # up to 999999.999
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)  # up to 999999.99

    def unit_price_usd(self):
        return utils.to_usd(self.unit_price)
    unit_price.short_description = "Unit Price (USD)"

    @property
    def cost(self):
        hundred = Decimal(100)
        cost = self.unit_price * self.quantity
        rounded = round(cost, 2)
        return rounded

    def cost_usd(self):
        return utils.to_usd(self.cost)
    cost_usd.short_description = "Cost (USD)"

    def __str__(self):
        return "%.2f of %s for %s" % (self.quantity, self.product.name, self.cost_usd())


class Fee(models.Model):
    receipt = models.ForeignKey("Receipt", related_name="fees")
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(null=True, default=1)
    amount = models.DecimalField(max_digits=6, decimal_places=2) # up to 999999.99

    def amount_usd(self):
        return utils.to_usd(self.amount)
    amount_usd.short_description = "Amount (USD)"

    @property
    def cost(self):
        return self.amount * self.quantity

    def cost_usd(self):
        return utils.to_usd(self.cost)
    cost_usd.short_description = "Cost (USD)"

    def __str__(self):
        return "%d of %s for %s" % (self.quantity, self.name, self.cost_usd())


class Discount(models.Model):
    receipt = models.ForeignKey("Receipt", related_name="discounts")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=6, decimal_places=2) # up to 999999.99

    def amount_usd(self):
        return utils.to_usd(self.amount)
    amount_usd.short_description = "Amount (USD)"

    def __str__(self):
        return "%s for %s" % (self.name, self.amount_usd())


class TaxCharge(models.Model):
    tax = models.ForeignKey("Tax", related_name="charges")
    receipt = models.ForeignKey("Receipt", related_name="taxes")
    amount = models.DecimalField(max_digits=8, decimal_places=2) # up to 999999.99

    class Meta:
        verbose_name = "tax charged"
        verbose_name_plural = "taxes charged"

    def amount_usd(self):
        return utils.to_usd(self.amount)
    amount_usd.short_description = "Amount (USD)"

    def rate(self):
        return self.amount / self.receipt.total
    rate.short_description = "Tax Rate"

    def percentage(self):
        """Convert tax rate decimal into a percentage, e.g. 0.14 --> 14"""
        return self.rate() * 100
    percentage.short_description = "Tax %"

    def percentage_str(self):
        """Convert tax rate decimal into a percentage string, e.g. 0.14 --> 14%"""
        return "%2.3f%%" % self.percentage()
    percentage_str.short_description = "Tax"

    def __str__(self):
        return "%s (%s)" % (self.tax.name, self.percentage_str())


class Gratuity(models.Model):
    receipt = models.ForeignKey("Receipt", related_name="gratuities")
    to = models.CharField("server, salesperson, etc", max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2) # up to 999999.99

    class Meta:
        verbose_name_plural = "gratuities"

    def amount_usd(self):
        return utils.to_usd(self.amount)
    amount_usd.short_description = "Amount (USD)"

    def __str__(self):
        repr = "%s" % self.amount_usd()
        if self.to:
            repr = "%s for %s" % (self.amount_usd(), self.to)
        return repr
