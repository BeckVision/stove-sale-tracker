from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

# Import Sum to calculate total share percentage
from django.db.models import Sum

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_cost = models.IntegerField(validators=[MinValueValidator(0)])
    master_fee = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    share_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of total sales revenue (e.g., 12.5 for 12.5%)"
    )

    def __str__(self):
        return f"{self.user.username} ({self.share_percentage}%)"
    
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    sale_price = models.PositiveIntegerField() # This is the TOTAL price for all items
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def total_base_cost(self):
        return self.product.base_cost * self.quantity

    @property
    def total_master_pay(self):
        return self.product.master_fee * self.quantity

    @property
    def investor_fee(self):
        # Calculate the total investment share percentage from all investors
        total_share_percentage = Investor.objects.aggregate(total=Sum('share_percentage'))['total'] or 0
        
        # New calculation: (Sold Price - Base Cost) * Total Investor Percentage
        gross_profit = self.sale_price - self.total_base_cost
        fee = gross_profit * (total_share_percentage / 100)
        return round(fee)

    @property
    def profit(self):
        # NEW PROFIT CALCULATION: (Sold Price - Base Cost - Investor Fee - Master's Pay)
        
        # 1. Total Revenue
        revenue = self.sale_price
        
        # 2. Total Costs
        base_cost = self.total_base_cost
        master_pay = self.total_master_pay
        investor_fee = self.investor_fee # Calculated using the new formula
        
        # Final Profit
        return revenue - base_cost - investor_fee - master_pay

    def __str__(self):
        return f"{self.quantity} x {self.product.name} on {self.date.strftime('%Y-%m-%d')}"
    
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add fields later if needed: phone, rate_per_unit, etc.

    def __str__(self):
        return f"Worker: {self.user.username}"
    
class WorkerPayRate(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate_per_unit = models.IntegerField(
        validators=[MinValueValidator(0)],
        # CHANGED CURRENCY FROM UGX TO SO'M
        help_text="How much the worker earns per unit of this product (SO'M)"
    )

    class Meta:
        unique_together = ('worker', 'product')

    def __str__(self):
        return f"{self.worker} → {self.product}: {self.rate_per_unit} SO'M"

class ProductionLog(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    date = models.DateField(default=date.today)  # auto today

    class Meta:
        verbose_name = "Production Log"
        verbose_name_plural = "Production Logs"
        unique_together = ('worker', 'product', 'date')  # one entry per product per day

    @property
    def earnings(self):
        # NEW LOGIC: Try to find individual rate, if not found, use Product.master_fee
        try:
            # 1. Check for individual WorkerPayRate
            rate_obj = WorkerPayRate.objects.get(worker=self.worker, product=self.product)
            rate_per_unit = rate_obj.rate_per_unit
        except WorkerPayRate.DoesNotExist:
            # 2. Fallback to the Product's master_fee
            rate_per_unit = self.product.master_fee

        return rate_per_unit * self.quantity

    def __str__(self):
        return f"{self.worker} made {self.quantity} {self.product.name} on {self.date}"
