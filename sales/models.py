from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_cost = models.IntegerField(validators=[MinValueValidator(0)])
    master_fee = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) # <-- ADD THIS LINE
    sale_price = models.PositiveIntegerField() # This is the TOTAL price for all items
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def profit(self):
        # The profit is now calculated with quantity
        total_cost = self.product.base_cost * self.quantity
        return self.sale_price - total_cost

    def __str__(self):
        return f"{self.quantity} x {self.product.name} on {self.date.strftime('%Y-%m-%d')}"

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    share_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of total sales revenue (e.g., 12.5 for 12.5%)"
    )

    def __str__(self):
        return f"{self.user.username} ({self.share_percentage}%)"
    

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
        help_text="How much the worker earns per unit of this product (UGX)"
    )

    class Meta:
        unique_together = ('worker', 'product')

    def __str__(self):
        return f"{self.worker} → {self.product}: {self.rate_per_unit} UGX"

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
        try:
            rate = WorkerPayRate.objects.get(worker=self.worker, product=self.product)
            return rate.rate_per_unit * self.quantity
        except WorkerPayRate.DoesNotExist:
            return 0

    def __str__(self):
        return f"{self.worker} made {self.quantity} {self.product.name} on {self.date}"