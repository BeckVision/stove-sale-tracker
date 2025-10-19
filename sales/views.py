from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Sale, Investor, Worker, ProductionLog
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

# ... home_redirect, add_sale, sale_list, investor_dashboard functions remain the same ...
def home_redirect(request):
    if request.user.is_staff:
        return redirect('sale_list')
    elif hasattr(request.user, 'investor'):
        return redirect('investor_dashboard')
    elif hasattr(request.user, 'worker'):
        return redirect('worker_dashboard')
    else:
        return redirect('login')

@staff_member_required
def add_sale(request):
    products = Product.objects.all()
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        sale_price_raw = request.POST.get('sale_price')
        quantity_raw = request.POST.get('quantity')

        if not all([product_id, sale_price_raw, quantity_raw]):
            messages.error(request, "Please fill out all fields: product, quantity, and price.")
            return redirect('add_sale')

        sale_price = int(sale_price_raw)
        quantity = int(quantity_raw)
        product = Product.objects.get(id=product_id)
        
        Sale.objects.create(
            product=product,
            quantity=quantity,
            sale_price=sale_price,
            recorded_by=request.user
        )
        
        messages.success(
            request,
            f"Sale recorded: {quantity} x {product.name} for {sale_price:,} SUM"
        )
        return redirect('add_sale')
    
    return render(request, 'add_sale.html', {'products': products})

@staff_member_required
def sale_list(request):
    sales = Sale.objects.select_related('product', 'recorded_by').order_by('-date')
    total_revenue = sales.aggregate(total=Sum('sale_price'))['total'] or 0
    total_profit = sum(sale.profit for sale in sales)
    return render(request, 'sale_list.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
    })

@login_required
def investor_dashboard(request):
    try:
        investor = Investor.objects.get(user=request.user)
    except Investor.DoesNotExist:
        messages.error(request, "You do not have an investor profile.")
        return redirect('home')
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    total_profit_all_time = sum(s.profit for s in Sale.objects.all())
    total_earnings = total_profit_all_time * (investor.share_percentage / 100)

    today_profit = sum(s.profit for s in Sale.objects.filter(date__date=today))
    today_earnings = today_profit * (investor.share_percentage / 100)

    week_profit = sum(s.profit for s in Sale.objects.filter(date__date__gte=week_start))
    week_earnings = week_profit * (investor.share_percentage / 100)

    last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_profit = sum(s.profit for s in Sale.objects.filter(date__date=day))
        day_earnings = day_profit * (investor.share_percentage / 100)
        last_7_days.append({
            'date': day,
            'earnings': round(day_earnings),
        })

    return render(request, 'investor_dashboard.html', {
        'percentage': investor.share_percentage,
        'total_earnings': round(total_earnings),
        'today_earnings': round(today_earnings),
        'week_earnings': round(week_earnings),
        'last_7_days': last_7_days,
    })

@login_required
def worker_dashboard(request):
    try:
        worker = Worker.objects.get(user=request.user)
    except Worker.DoesNotExist:
        messages.error(request, "You do not have a worker profile.")
        return redirect('home')

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    today_earnings = ProductionLog.objects.filter(worker=worker, date=today).aggregate(total=Sum('earnings'))['total'] or 0
    week_earnings = ProductionLog.objects.filter(worker=worker, date__gte=week_start).aggregate(total=Sum('earnings'))['total'] or 0

    all_logs = ProductionLog.objects.filter(worker=worker).order_by('-date', '-id')
    
    grouped_logs = defaultdict(lambda: {'logs': [], 'daily_total': 0})
    for log in all_logs:
        grouped_logs[log.date]['logs'].append(log)
        grouped_logs[log.date]['daily_total'] += log.earnings

    return render(request, 'worker_dashboard.html', {
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'grouped_logs': dict(grouped_logs),
    })

@login_required
def home_redirect(request):
    if request.user.is_staff:
        return redirect('sale_list')
    elif hasattr(request.user, 'investor'):
        return redirect('investor_dashboard')
    elif hasattr(request.user, 'worker'):
        return redirect('worker_dashboard')
    else:
        return redirect('login')

@staff_member_required
def add_sale(request):
    products = Product.objects.all()
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        sale_price_raw = request.POST.get('sale_price')
        quantity_raw = request.POST.get('quantity')

        if not all([product_id, sale_price_raw, quantity_raw]):
            messages.error(request, "Please fill out all fields: product, quantity, and price.")
            return redirect('add_sale')

        sale_price = int(sale_price_raw)
        quantity = int(quantity_raw)
        product = Product.objects.get(id=product_id)
        
        Sale.objects.create(
            product=product,
            quantity=quantity,
            sale_price=sale_price,
            recorded_by=request.user
        )
        
        messages.success(
            request,
            f"Sale recorded: {quantity} x {product.name} for {sale_price:,} SUM"
        )
        return redirect('add_sale')
    
    return render(request, 'add_sale.html', {'products': products})

@staff_member_required
def sale_list(request):
    sales = Sale.objects.select_related('product', 'recorded_by').order_by('-date')
    total_revenue = sales.aggregate(total=Sum('sale_price'))['total'] or 0
    total_profit = sum(sale.profit for sale in sales)
    return render(request, 'sale_list.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
    })

@login_required
def investor_dashboard(request):
    try:
        investor = Investor.objects.get(user=request.user)
    except Investor.DoesNotExist:
        messages.error(request, "You do not have an investor profile.")
        return redirect('home')
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    total_profit_all_time = sum(s.profit for s in Sale.objects.all())
    total_earnings = total_profit_all_time * (investor.share_percentage / 100)

    today_profit = sum(s.profit for s in Sale.objects.filter(date__date=today))
    today_earnings = today_profit * (investor.share_percentage / 100)

    week_profit = sum(s.profit for s in Sale.objects.filter(date__date__gte=week_start))
    week_earnings = week_profit * (investor.share_percentage / 100)

    last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_profit = sum(s.profit for s in Sale.objects.filter(date__date=day))
        day_earnings = day_profit * (investor.share_percentage / 100)
        last_7_days.append({
            'date': day,
            'earnings': round(day_earnings),
        })

    return render(request, 'investor_dashboard.html', {
        'percentage': investor.share_percentage,
        'total_earnings': round(total_earnings),
        'today_earnings': round(today_earnings),
        'week_earnings': round(week_earnings),
        'last_7_days': last_7_days,
    })

@login_required
def worker_dashboard(request):
    try:
        worker = Worker.objects.get(user=request.user)
    except Worker.DoesNotExist:
        messages.error(request, "You do not have a worker profile.")
        return redirect('home')

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # FIX: Fetch logs first, then sum the .earnings property in Python
    today_logs = ProductionLog.objects.filter(worker=worker, date=today)
    today_earnings = sum(log.earnings for log in today_logs)

    week_logs = ProductionLog.objects.filter(worker=worker, date__gte=week_start)
    week_earnings = sum(log.earnings for log in week_logs)

    # Group all production logs by date for a better historical view
    all_logs = ProductionLog.objects.filter(worker=worker).order_by('-date', '-id')
    
    grouped_logs = defaultdict(lambda: {'logs': [], 'daily_total': 0})
    for log in all_logs:
        grouped_logs[log.date]['logs'].append(log)
        grouped_logs[log.date]['daily_total'] += log.earnings

    return render(request, 'worker_dashboard.html', {
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'grouped_logs': dict(grouped_logs),
    })


@login_required
def add_production(request):
    try:
        worker = Worker.objects.get(user=request.user)
    except Worker.DoesNotExist:
        messages.error(request, "You are not registered as a worker.")
        return redirect('home')

    products = Product.objects.all()

    if request.method == 'POST':
        updated_any = False
        for product in products:
            qty_str = request.POST.get(f'quantity_{product.id}', '0')
            try:
                qty = int(qty_str)
            except ValueError:
                # Handle potential non-integer input gracefully, maybe log a warning
                qty = 0

            if qty > 0:
                # Use update_or_create to handle the unique constraint
                log, created = ProductionLog.objects.update_or_create(
                    worker=worker,
                    product=product,
                    date=date.today(), # Assuming you always log for today
                    defaults={'quantity': qty} # This sets the quantity
                )
                updated_any = True
                # Optional: Add a message if it was updated vs. created
                # action = "created" if created else "updated"
                # print(f"Log {action} for {product.name}: {qty}") # For debugging

        if updated_any:
            messages.success(request, "Production log(s) updated successfully!")
        else:
            messages.info(request, "No production quantities were entered or were zero.")

        return redirect('worker_dashboard')

    # For GET requests, just render the form
    return render(request, 'add_production.html', {'products': products})