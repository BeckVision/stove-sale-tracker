from django.contrib import admin
from .models import Product, Sale, Investor, Worker, ProductionLog, WorkerPayRate

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_cost', 'master_fee')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'sale_price', 'profit', 'date', 'recorded_by')
    list_filter = ('date', 'product')
    readonly_fields = ('date',)
    search_fields = ('product__name',)

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('user', 'share_percentage')
    search_fields = ('user__username',)

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(WorkerPayRate)
class WorkerPayRateAdmin(admin.ModelAdmin):
    list_display = ('worker', 'product', 'rate_per_unit')
    list_filter = ('worker', 'product')

@admin.register(ProductionLog)
class ProductionLogAdmin(admin.ModelAdmin):
    list_display = ('worker', 'product', 'quantity', 'date', 'earnings')
    list_filter = ('date', 'worker', 'product')
    readonly_fields = ('earnings',)
