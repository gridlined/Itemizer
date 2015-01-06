from datetime import date, time
from decimal import Decimal
from os import path

from django.test import TestCase

from mizer.models import utils, Supplier, Tax, TaxCharge, ProductType, Product, Item, Fee, Discount, Gratuity, Receipt


class UtilsTest(TestCase):
    def test_to_usd_format_of_integers(self):
        """An integer is correctly formatted for USD"""
        self.assertEqual(utils.to_usd(4), "$4.00")

    def test_to_usd_format_of_floats(self):
        """A float is correctly rounded and formatted for USD"""
        self.assertEqual(utils.to_usd(5.2), "$5.20")
        self.assertEqual(utils.to_usd(8.387), "$8.39")
        self.assertEqual(utils.to_usd(4.961), "$4.96")

    def test_to_usd_format_of_large_numbers(self):
        """A large number is correctly formatted for USD"""
        self.assertEqual(utils.to_usd(1234567890.12), "$1234567890.12")

    def test_to_usd_format_of_negatives(self):
        """A negative number is correctly formatted for USD"""
        self.assertEqual(utils.to_usd(-987.654), "-$987.65")

    def test_datestamp_format(self):
        """Datestamp string returned follows a YYYY-MM-DD format"""
        today = date.today()
        self.assertEqual(utils.datestamp(today), today.strftime("%Y-%m-%d"))

    def test_datestamp_default_date(self):
        """Datestamp defaults to that for today's date"""
        today = date.today()
        self.assertEqual(utils.datestamp(), utils.datestamp(today))

    def test_clean_dirname_valid_characters(self):
        """Cleaned directory name contains only alphanumeric plus hyphen and underscore"""
        valid_chars = 'abcdefghijklmnopqrstuvwxy01234567890-_'
        invalid_chars = '`~!@#$%^&*()=+[]\{}|'";:/?.>,<"
        self.assertEqual(utils.clean_dirname(valid_chars), valid_chars)
        self.assertEqual(utils.clean_dirname(invalid_chars), '_'*len(invalid_chars))

    def test_clean_dirname_character_case(self):
        """Cleaned directory name is forced to all lowercase"""
        name = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        self.assertEqual(utils.clean_dirname(name), name.lower())

    def test_build_image_path_no_args(self):
        """Without additional arguments, the base filename is returned"""
        filename = "/path/to/filename.ext"
        self.assertEqual(utils.build_image_path(filename), filename)

    def test_build_image_path_appends_extension(self):
        """The original file extension is added to the end of the new path"""
        root = "/path/to/filename"
        ext = ".ext"
        filename = "%s%s" % (root, ext)
        new_path = "some/new/path/and/filename"
        self.assertEqual(utils.build_image_path(filename, new_path),
                         "%s%s" % (new_path, ext))

    def test_build_image_path_os_conversion(self):
        """Generated path is formatted for the current operating system"""
        root = "/path/to/filename"
        ext = ".ext"
        filename = "%s%s" % (root, ext)
        new_path = "some\\new\\path\\and\\filename"
        os_path = path.join(new_path)
        self.assertEqual(utils.build_image_path(filename, new_path),
                         "%s%s" % (os_path, ext))

    def test_build_image_path_accepts_any_number_of_arguments(self):
        """Path is generated from any number of arguments, as separate path parts"""
        root = "/path/to/filename"
        ext = ".ext"
        filename = "%s%s" % (root, ext)
        parts = ["one", "two", "three"]
        new_path = path.join(*parts)
        self.assertEqual(utils.build_image_path(filename, *parts),
                         "%s%s" % (new_path, ext))

    def test_product_image_path_format(self):
        Product.objects.create(name="Test Product")
        product = Product.objects.first()
        datestamp = utils.datestamp()
        id = product.pk
        name = utils.clean_dirname(product.name)
        self.assertEqual(utils.product_image_path(product, "filename.jpg"),
                         "product/%i/%s_%s.jpg" % (id, datestamp, name))

    def test_receipt_image_path_format(self):
        Supplier.objects.create(name="Test supplier")
        Receipt.objects.create(supplier=Supplier.objects.first())
        receipt = Receipt.objects.first()
        year = receipt.date.strftime("%Y")
        month = receipt.date.strftime("%m")
        day = receipt.date.strftime("%d")
        id = receipt.pk
        name = utils.clean_dirname(receipt.supplier)
        self.assertEqual(utils.receipt_image_path(receipt, "filename.jpg"),
                         "receipt/%s/%s/%s/%s_%s.jpg" % (year, month, day, id, name))


class TaxTest(TestCase):
    name = "Test Tax"

    def setUp(self):
        Tax.objects.create(name=self.name)

    def test_creation(self):
        """Tax object can be created"""
        self.assertEqual(Tax.objects.count(), 1)

    def test_properties(self):
        """Tax properties are assigned as provided during creation"""
        self.assertEqual(Tax.objects.first().name, self.name)

    def test_representation(self):
        """Tax string representation contains tax name"""
        self.assertRegexpMatches("%s" % Tax.objects.first(), r"\b%s\b" % self.name)

    def test_verbose_name(self):
        """Tax object verbose name and plural version are defined as expected"""
        self.assertEqual(Tax._meta.verbose_name, "tax")
        self.assertEqual(Tax._meta.verbose_name_plural, "taxes")


class SupplierTest(TestCase):
    name = "TestSupplier"
    street = """
        Address Line1
        Address Line 2
        """
    city = "TestCity"
    state = "ST"
    postal_code = "55555-5555"
    phone = "(888) 555-1212"
    website = "http://www.gridlined.com/"

    def setUp(self):
        Supplier.objects.create(name=self.name,
                                street=self.street,
                                city=self.city,
                                state=self.state,
                                postal_code=self.postal_code,
                                phone=self.phone,
                                website=self.website)

    def test_creation(self):
        """Supplier object can be created"""
        self.assertEqual(Supplier.objects.count(), 1)

    def test_properties(self):
        """Supplier properties are assigned as provided during creation"""
        supplier = Supplier.objects.first()
        self.assertEqual(supplier.name, self.name)
        self.assertEqual(supplier.street, self.street)
        self.assertEqual(supplier.city, self.city)
        self.assertEqual(supplier.state, self.state)
        self.assertEqual(supplier.postal_code, self.postal_code)
        self.assertEqual(supplier.phone, self.phone)
        self.assertEqual(supplier.website, self.website)

    def test_representation(self):
        """Supplier string representation contains both supplier name and city"""
        supplier = Supplier.objects.first()
        self.assertRegexpMatches("%s" % supplier, r"\b%s\b" % self.name)
        self.assertRegexpMatches("%s" % supplier, r"\b%s\b" % self.city)
        supplier.city = None
        self.assertNotRegexpMatches("%s" % supplier, r"\b%s\b" % self.city)


class ProductTypeTest(TestCase):
    name = "Test Product Type"

    def setUp(self):
        ProductType.objects.create(name=self.name)

    def test_creation(self):
        """ProductType object can be created"""
        self.assertEqual(ProductType.objects.count(), 1)

    def test_representation(self):
        """Tax string representation contains tax name"""
        self.assertRegexpMatches("%s" % ProductType.objects.first(), r"\b%s\b" % self.name)


class ProductTest(TestCase):
    product_name = "Test Product"
    type_name = "Test Product Type"

    def setUp(self):
        ProductType.objects.create(name=self.type_name)
        Product.objects.create(name=self.product_name)
        Product.objects.first().types.add(ProductType.objects.first())

    def test_creation(self):
        self.assertEqual(Product.objects.count(), 1)

    def test_properties(self):
        self.assertEqual(Product.objects.first().name, self.product_name)
        self.assertEqual(Product.objects.first().types.first(), ProductType.objects.first())

    def test_representation(self):
        self.assertRegexpMatches("%s" % Product.objects.first(), r"\b%s\b" % self.product_name)


class ReceiptTest(TestCase):
    supplier_name = "Test Supplier"
    date = date.today()
    time = time(4, 32, 15, 0)
    product_type_name = "Test Product Type"
    product_name = "Test Product"
    item_quantity = 2
    item_price = 4.25

    def setUp(self):
        Supplier.objects.create(name=self.supplier_name)
        Receipt.objects.create(supplier=Supplier.objects.first(),
                               date=self.date,
                               time=self.time)
        ProductType.objects.create(name=self.product_type_name)
        Product.objects.create(name=self.product_name)
        Product.objects.first().types.add(ProductType.objects.first())
        Item.objects.create(receipt=Receipt.objects.first(),
                            product=Product.objects.first(),
                            quantity=self.item_quantity,
                            unit_price=self.item_price)

    def test_creation(self):
        self.assertEqual(Receipt.objects.count(), 1)

    def test_properties(self):
        receipt = Receipt.objects.first()
        self.assertEqual(receipt.supplier, Supplier.objects.first())
        self.assertEqual(receipt.date, self.date)
        self.assertEqual(receipt.time, self.time)

    def test_subtotal(self):
        self.assertEqual(Receipt.objects.first().subtotal, self.item_price * self.item_quantity)

    def test_subtotal_usd(self):
        receipt = Receipt.objects.first()
        self.assertEqual(receipt.subtotal_usd(), utils.to_usd(receipt.subtotal))

    def test_tax(self):
        self.assertEqual(Receipt.objects.first().tax, 0)

    def test_tax_usd(self):
        self.assertEqual(Receipt.objects.first().tax_usd(), utils.to_usd(0))

    def test_fee(self):
        self.assertEqual(Receipt.objects.first().fee, 0)

    def test_fee_usd(self):
        self.assertEqual(Receipt.objects.first().fee_usd(), utils.to_usd(0))

    def test_discount(self):
        self.assertEqual(Receipt.objects.first().discount, 0)

    def test_discount_usd(self):
        self.assertEqual(Receipt.objects.first().discount_usd(), utils.to_usd(0))

    def test_tip(self):
        self.assertEqual(Receipt.objects.first().tip, 0)

    def test_tip_usd(self):
        self.assertEqual(Receipt.objects.first().tip_usd(), utils.to_usd(0))

    def test_total(self):
        receipt = Receipt.objects.first()
        self.assertEqual(receipt.total, (receipt.subtotal
                                         + receipt.fee
                                         - receipt.discount
                                         + receipt.tax
                                         + receipt.tip))

    def test_total_usd(self):
        receipt = Receipt.objects.first()
        self.assertEqual(receipt.total_usd(), utils.to_usd(receipt.total))

    def test_when(self):
        receipt = Receipt.objects.first()
        self.assertEqual(receipt.when, "%s %s" % (self.date, self.time))
        receipt.time = None
        self.assertEqual(receipt.when, "%s" % self.date)

    def test_representation(self):
        receipt = Receipt.objects.first()
        self.assertRegexpMatches("%s" % receipt, r"\b%s\b" % receipt.when)
        self.assertRegexpMatches("%s" % receipt, r"\b%s\b" % receipt.supplier)
        self.assertRegexpMatches("%s" % receipt, r"\b%d\b" % receipt.subtotal)


class ItemTest(TestCase):
    product_type_name = "Test Product Type"
    product_name = "Test Product"
    supplier_name = "Test Supplier"
    quantity = 2
    unit_price = Decimal("%2.2f" % 3.87)
    receipt_date = date.today()

    def setUp(self):
        ProductType.objects.create(name=self.product_type_name)
        Product.objects.create(name=self.product_name)
        Product.objects.first().types.add(ProductType.objects.first())
        Supplier.objects.create(name=self.supplier_name)
        Receipt.objects.create(supplier=Supplier.objects.first(), 
                               date=self.receipt_date)
        Item.objects.create(product=Product.objects.first(),
                            receipt=Receipt.objects.first(),
                            quantity=self.quantity,
                            unit_price=self.unit_price)

    def test_creation(self):
        self.assertEqual(Item.objects.count(), 1)

    def test_cost(self):
        self.assertEqual(Item.objects.first().cost,
                         self.unit_price * self.quantity)

    def test_cost_usd(self):
        item = Item.objects.first()
        self.assertEqual(item.cost_usd(), utils.to_usd(item.cost))

    def test_representation(self):
        item = Item.objects.first()
        self.assertRegexpMatches("%s" % item, r"\b%d\b" % self.quantity)
        self.assertRegexpMatches("%s" % item, r"\b%s\b" % self.product_name)
        self.assertRegexpMatches("%s" % item,
                                 r"\b%d\b" % (self.unit_price * self.quantity))


class FeeTest(TestCase):
    supplier_name = "Test Supplier"
    receipt_date = date.today()
    fee_name = "Test Fee"
    quantity = 2
    amount = Decimal("%2.2f" % 0.05)

    def setUp(self):
        Supplier.objects.create(name=self.supplier_name)
        Receipt.objects.create(supplier=Supplier.objects.first(), 
                               date=self.receipt_date)
        Fee.objects.create(receipt=Receipt.objects.first(),
                           name=self.fee_name,
                           quantity=self.quantity,
                           amount=self.amount)

    def test_creation(self):
        self.assertEqual(Fee.objects.count(), 1)

    def test_amount_usd(self):
        self.assertEqual(Fee.objects.first().amount_usd(),
                         utils.to_usd(self.amount))

    def test_cost(self):
        self.assertEqual(Fee.objects.first().cost, self.amount * self.quantity)

    def test_cost_usd(self):
        fee = Fee.objects.first()
        self.assertEqual(fee.cost_usd(), utils.to_usd(fee.cost))

    def test_representation(self):
        fee = Fee.objects.first()
        self.assertRegexpMatches("%s" % fee, r"\b%d\b" % self.quantity)
        self.assertRegexpMatches("%s" % fee, r"\b%s\b" % self.fee_name)
        self.assertRegexpMatches("%s" % fee,
                                 r"\b%d\b" % (self.amount * self.quantity))


class DiscountTest(TestCase):
    supplier_name = "Test Supplier"
    receipt_date = date.today()
    discount_name = "Test Discount"
    amount = Decimal("%2.2f" % 1.25)

    def setUp(self):
        Supplier.objects.create(name=self.supplier_name)
        Receipt.objects.create(supplier=Supplier.objects.first(), 
                               date=self.receipt_date)
        Discount.objects.create(receipt=Receipt.objects.first(),
                           name=self.discount_name,
                           amount=self.amount)

    def test_creation(self):
        self.assertEqual(Discount.objects.count(), 1)

    def test_amount_usd(self):
        self.assertEqual(Discount.objects.first().amount_usd(),
                         utils.to_usd(self.amount))

    def test_representation(self):
        discount = Discount.objects.first()
        self.assertRegexpMatches("%s" % discount,
                                 r"\b%s\b" % self.discount_name)
        self.assertRegexpMatches("%s" % discount, r"\b%d\b" % self.amount)


class TaxChargeTest(TestCase):
    tax_name = "Test Tax"
    product_type_name = "Test Product Type"
    product_name = "Test Product"
    supplier_name = "Test Supplier"
    receipt_date = date.today()
    item_quantity = 2
    item_unit_price = Decimal("%2.2f" % 3.87)
    amount = Decimal("%2.2f" % 1.25)

    def setUp(self):
        Tax.objects.create(name=self.tax_name)
        ProductType.objects.create(name=self.product_type_name)
        Product.objects.create(name=self.product_name)
        Product.objects.first().types.add(ProductType.objects.first())
        Supplier.objects.create(name=self.supplier_name)
        Receipt.objects.create(supplier=Supplier.objects.first(), 
                               date=self.receipt_date)
        Item.objects.create(product=Product.objects.first(),
                            receipt=Receipt.objects.first(),
                            quantity=self.item_quantity,
                            unit_price=self.item_unit_price)
        TaxCharge.objects.create(tax=Tax.objects.first(),
                                 receipt=Receipt.objects.first(),
                                 amount=self.amount)

    def test_creation(self):
        self.assertEqual(TaxCharge.objects.count(), 1)

    def test_amount_usd(self):
        self.assertEqual(TaxCharge.objects.first().amount_usd(),
                         utils.to_usd(self.amount))

    def test_rate(self):
        self.assertEqual(TaxCharge.objects.first().rate(),
                         self.amount / Receipt.objects.first().total)

    def test_percentage(self):
        tax = TaxCharge.objects.first()
        self.assertEqual(tax.percentage(), tax.rate() * 100)

    def test_percentage_str(self):
        tax = TaxCharge.objects.first()
        self.assertEqual(tax.percentage_str(), "%2.3f%%" % tax.percentage())

    def test_representation(self):
        tax = TaxCharge.objects.first()
        self.assertRegexpMatches("%s" % tax, r"\b%s\b" % self.tax_name)
        self.assertRegexpMatches("%s" % tax, r"\b%d\b" % tax.percentage())

    def test_verbose_name(self):
        """Taxcharge object verbose name and plural version are defined as expected"""
        self.assertEqual(TaxCharge._meta.verbose_name, "tax charged")
        self.assertEqual(TaxCharge._meta.verbose_name_plural, "taxes charged")


class GratuityTest(TestCase):
    product_type_name = "Test Product Type"
    product_name = "Test Product"
    supplier_name = "Test Supplier"
    receipt_date = date.today()
    item_quantity = 2
    item_unit_price = Decimal("%2.2f" % 3.87)
    to = "Test Server"
    amount = Decimal("%2.2f" % 1.25)

    def setUp(self):
        ProductType.objects.create(name=self.product_type_name)
        Product.objects.create(name=self.product_name)
        Product.objects.first().types.add(ProductType.objects.first())
        Supplier.objects.create(name=self.supplier_name)
        Receipt.objects.create(supplier=Supplier.objects.first(), 
                               date=self.receipt_date)
        Item.objects.create(product=Product.objects.first(),
                            receipt=Receipt.objects.first(),
                            quantity=self.item_quantity,
                            unit_price=self.item_unit_price)
        Gratuity.objects.create(receipt=Receipt.objects.first(),
                                to=self.to,
                                amount=self.amount)

    def test_creation(self):
        self.assertEqual(Gratuity.objects.count(), 1)

    def test_amount_usd(self):
        self.assertEqual(Gratuity.objects.first().amount_usd(), utils.to_usd(self.amount))

    def test_representation(self):
        tip = Gratuity.objects.first()
        self.assertRegexpMatches("%s" % tip, r"\b%s\b" % self.to)
        self.assertRegexpMatches("%s" % tip, r"\b%d\b" % self.amount)

    def test_verbose_name(self):
        """Gratuity object verbose name and plural version are defined as expected"""
        self.assertEqual(Gratuity._meta.verbose_name, "gratuity")
        self.assertEqual(Gratuity._meta.verbose_name_plural, "gratuities")