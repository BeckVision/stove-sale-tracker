from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Investor, Product, ProductionLog, Sale, Worker, WorkerPayRate


class SaleModelTests(TestCase):
    def test_sale_profit_splits_costs_worker_pay_and_investor_fee(self):
        staff = User.objects.create_user(username="staff")
        product = Product.objects.create(
            name="Classic Stove",
            base_cost=200_000,
            master_fee=30_000,
        )
        investor_user = User.objects.create_user(username="investor")
        Investor.objects.create(user=investor_user, share_percentage=25)

        sale = Sale.objects.create(
            product=product,
            quantity=2,
            sale_price=700_000,
            recorded_by=staff,
        )

        self.assertEqual(sale.total_base_cost, 400_000)
        self.assertEqual(sale.total_master_pay, 60_000)
        self.assertEqual(sale.investor_fee, 75_000)
        self.assertEqual(sale.profit, 165_000)


class ProductionLogTests(TestCase):
    def test_worker_specific_rate_overrides_product_master_fee(self):
        worker_user = User.objects.create_user(username="worker")
        worker = Worker.objects.create(user=worker_user)
        product = Product.objects.create(
            name="Compact Stove",
            base_cost=150_000,
            master_fee=25_000,
        )
        WorkerPayRate.objects.create(worker=worker, product=product, rate_per_unit=35_000)

        log = ProductionLog.objects.create(
            worker=worker,
            product=product,
            quantity=3,
            date=date.today(),
        )

        self.assertEqual(log.earnings, 105_000)

    def test_worker_earnings_fallback_to_product_master_fee(self):
        worker_user = User.objects.create_user(username="worker")
        worker = Worker.objects.create(user=worker_user)
        product = Product.objects.create(
            name="Family Stove",
            base_cost=300_000,
            master_fee=40_000,
        )

        log = ProductionLog.objects.create(
            worker=worker,
            product=product,
            quantity=2,
            date=date.today(),
        )

        self.assertEqual(log.earnings, 80_000)


class ViewRoutingTests(TestCase):
    def test_staff_home_redirects_to_sales_list(self):
        staff = User.objects.create_user(username="staff", password="password", is_staff=True)
        self.client.force_login(staff)

        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("sale_list"))

    def test_worker_home_redirects_to_worker_dashboard(self):
        user = User.objects.create_user(username="worker", password="password")
        Worker.objects.create(user=user)
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("worker_dashboard"))
