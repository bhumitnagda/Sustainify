# ==============================================================================
# EcoScore is based on the JavaScript implementation by Gavin Kimball/Gkimbo
# Original repository: https://github.com/Gkimbo/eco-score
# Distributed under the MIT License.
# ==============================================================================
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager
from unicodedata import decimal
import random

STATUS_CHOICE = (
    ("process", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

RATING = (
    (1, " ★ ☆ ☆ ☆ ☆"),
    (2, " ★ ★ ☆ ☆ ☆"),
    (3, " ★ ★ ★ ☆ ☆"),
    (4, " ★ ★ ★ ★ ☆"),
    (5, " ★ ★ ★ ★ ★"),
)

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

def cert_directory_path(instance, filename):
    # store certificates under vendor_<vendor_id>/
    return f'vendor_{instance.vendor.id}/{filename}'

class Category(models.Model):
    c_id = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="a-z1-9")
    title = models.CharField(max_length=150, default="football")
    image = models.ImageField(upload_to="category", default="brand_02.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.title

class Tags(models.Model):
    pass

class Vendor(models.Model):
    v_id = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="a-z1-9")
    title = models.CharField(max_length=150, default="Barca")
    image = models.ImageField(upload_to=user_directory_path, default="brand_01.jpg")
    description = models.TextField(null=True, blank=True, default="Spain")
    address = models.CharField(max_length=150, default="123")
    chat_resp_time = models.CharField(max_length=150, default="123")
    contact = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d+$', message='Enter a valid numeric contact number.')],
        default="91000000000"
    )
    shipping_on_time = models.CharField(max_length=150, default="123")
    authentic_rating = models.CharField(max_length=150, default="123")
    days_return = models.CharField(max_length=150, default="123")
    warranty_period = models.CharField(max_length=150, default="123")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.title

# ─── Certificate Model ───────────────────────────────────────────────────────────
class Certificate(models.Model):
    vendor      = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="certificates")
    file        = models.FileField(upload_to=cert_directory_path)
    cert_no     = models.CharField(max_length=100)
    issued_on   = models.DateField()
    expires_on  = models.DateField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"{self.vendor.title} – {self.cert_no}"
# ────────────────────────────────────────────────────────────────────────────────

class Product(models.Model):
    p_id = ShortUUIDField(unique=True, length=10, max_length=20, prefix="prd", alphabet="a-z1-9")
    title = models.CharField(max_length=150, default="This is a fresh product")
    image = models.ImageField(upload_to=user_directory_path, default="shop_11.jpg")
    description = models.TextField(null=True, blank=True, default="This is a product")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    price = models.DecimalField(max_digits=99999999999, decimal_places=2, default="0.00")
    old_price = models.DecimalField(max_digits=99999999999, decimal_places=2, default="1.00", null=True, blank=True)
    specifications = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="products")
    tags = TaggableManager(blank=True)

    CARBON_FOOTPRINT_CHOICES = (
        (0, 'Low (0-33)'),
        (1, 'Moderate (34-66)'),
        (2, 'High (67-100)'),
    )
    carbon_footprint_level = models.IntegerField(choices=CARBON_FOOTPRINT_CHOICES, default=0)
    MATERIAL_CHOICES = (
        ('good', 'Good'),
        ('better', 'Better'),
        ('best', 'Best'),
    )
    material_sourcing = models.CharField(max_length=10, choices=MATERIAL_CHOICES, default='good')
    RECYCLABILITY_CHOICES = (
        (0, 'Low (0-33)'),
        (1, 'Moderate (34-66)'),
        (2, 'High (67-100)'),
    )
    recyclability_level = models.IntegerField(choices=RECYCLABILITY_CHOICES, default=0)
    WATER_USAGE_CHOICES = (
        ('high', 'High'),
        ('moderate', 'Moderate'),
        ('low', 'Low'),
    )
    water_usage = models.CharField(max_length=10, choices=WATER_USAGE_CHOICES, default='low')
    ENERGY_EFFICIENCY_CHOICES = (
        ('high', 'High'),
        ('moderate', 'Moderate'),
        ('low', 'Low'),
    )
    energy_efficiency = models.CharField(max_length=10, choices=ENERGY_EFFICIENCY_CHOICES, default='low')
    BIODEGRADABILITY_CHOICES = (
        (0, 'Low (0-33)'),
        (1, 'Moderate (34-66)'),
        (2, 'High (67-100)'),
    )
    biodegradability_level = models.IntegerField(choices=BIODEGRADABILITY_CHOICES, default=0)
    durability = models.CharField(max_length=20, default="0 months")
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    STATUS = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.title

    def get_percentage(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - (self.price / self.old_price)) * 100)
        return 0

    def calculate_eco_score(self):
        score = 0
        carbon_score_map = {0: 100, 1: 50, 2: 0}
        score += carbon_score_map.get(self.carbon_footprint_level, 50) * 0.2

        material_sourcing_scores = {"good": 40, "better": 70, "best": 100}
        score += material_sourcing_scores.get(self.material_sourcing.lower(), 40) * 0.2

        value_map = {0: 17, 1: 50, 2: 84}
        score += value_map.get(self.recyclability_level, 17) * 0.2

        water_usage_scores = {"high": 0, "moderate": 50, "low": 100}
        score += water_usage_scores.get(self.water_usage.lower(), 100) * 0.1

        energy_efficiency_scores = {"high": 100, "moderate": 70, "low": 40}
        score += energy_efficiency_scores.get(self.energy_efficiency.lower(), 40) * 0.1

        score += value_map.get(self.biodegradability_level, 17) * 0.1

        try:
            durability_value = float(self.durability.split()[0])
            if "year" in self.durability.lower():
                durability_in_months = durability_value * 12
            elif "month" in self.durability.lower():
                durability_in_months = durability_value
            else:
                durability_in_months = durability_value * 12
        except ValueError:
            durability_in_months = 0

        durability_score = min(durability_in_months / 12, 1) * 10
        score += durability_score

        return round(min(score, 100) / 10, 2)

    @property
    def eco_score(self):
        return self.calculate_eco_score()

    @property
    def average_rating(self):
        reviews = self.product_reivew_set.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count())
        return 0

################################### PRODUCT IMAGES ###################################
class Product_Images(models.Model):
    images  = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"

################################### Cart, Order, OrderItems ####################################
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=99999999999, decimal_places=2, default="0.00")
    paid_Status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Order"


class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=300)
    image = models.CharField(max_length=300)
    qty = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_image(self):
        return mark_safe('<img src ="/media/%s" width="50" height="50" />' % (self.image))


################################### Product Review, Wishlists, Address ####################################
class Product_Reivew(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        if self.product and self.product.title:
            return self.product.title
        return "Product Review (No Product)"

    def get_rating(self):
        return self.rating


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=300, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"


class ProductOption(models.Model):
    product = models.ForeignKey(Product, related_name='options', on_delete=models.CASCADE)
    option_type = models.CharField(max_length=50,null = True, blank= True)  # e.g., "Color", "Size", "Pack"
    value = models.CharField(max_length=50,null = True , blank= True)  # e.g., "Black", "Red", "6", "2"

class Certificate(models.Model):
    vendor      = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="certificates")
    file        = models.FileField(upload_to=cert_directory_path)
    cert_no     = models.CharField(max_length=100)
    issued_on   = models.DateField()
    expires_on  = models.DateField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"{self.vendor.title} – {self.cert_no}"



