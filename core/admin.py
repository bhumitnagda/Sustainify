from django.contrib import admin
from .models import (
    Product, Category, Vendor, CartOrderItems, CartOrder, Wishlist,
    Product_Images, Product_Reivew, Address, ProductOption, Certificate
)
import zipfile
from django.http import HttpResponse

class ProductImagesAdmin(admin.TabularInline):
    model = Product_Images
    extra = 1

class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductOptionInline]
    list_display = ['p_id', 'title', 'vendor', 'category', 'price', 'product_status', 'in_stock', 'eco_score']
    list_filter = ('product_status', 'in_stock', 'category', 'vendor')
    search_fields = ('title', 'description', 'p_id')
    readonly_fields = ('p_id', 'sku', 'date', 'updated', 'eco_score')
    fieldsets = (
        (None, {'fields': ('p_id', 'title', 'user', 'vendor', 'category', 'image')}),
        ('Pricing', {'fields': ('price', 'old_price')}),
        ('Details', {'fields': ('description', 'specifications', 'tags')}),
        ('Sustainability', {
            'fields': (
                'carbon_footprint_level', 'material_sourcing', 'recyclability_level',
                'water_usage', 'energy_efficiency', 'biodegradability_level', 'durability'
            )
        }),
        ('Status', {'fields': ('product_status', 'in_stock', 'featured', 'digital', 'sku')}),
        ('Metadata', {'fields': ('date', 'updated', 'eco_score')}),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']

class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image', 'warranty_period']

class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'price', 'order_date', 'product_status']  # Removed 'paid_status'

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_no', 'item', 'image', 'qty']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'status']

class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['product', 'option_type', 'value']
    search_fields = ['product__title', 'option_type', 'value']

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'cert_no', 'issued_on', 'expires_on', 'uploaded_at')
    list_filter = ('vendor', 'issued_on', 'expires_on')
    search_fields = ('vendor__title', 'cert_no')
    date_hierarchy = 'issued_on'
    ordering = ('-uploaded_at',)
    actions = ['download_pdfs']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vendor')

    def download_pdfs(self, request, queryset):
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=certificates.zip'
        with zipfile.ZipFile(response, 'w') as zip_file:
            for cert in queryset:
                with open(cert.file.path, 'rb') as f:
                    zip_file.writestr(cert.file.name, f.read())
        return response
    download_pdfs.short_description = "Download selected certificate PDFs"

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Product_Reivew, ProductReviewAdmin)
admin.site.register(ProductOption, ProductOptionAdmin)
admin.site.register(Certificate, CertificateAdmin)