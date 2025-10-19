from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Sale, Investor, Worker, ProductionLog
from django.db.models import Sum, F, fields
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.contrib import messages

# The rest of the views (home_redirect, add_sale, investor_dashboard, worker_dashboard, add_production) 
# remain the same as they correctly rely on the updated model properties.

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
    
    # Debug: Log number of products fetched
    if not products.exists():
        messages.warning(request, "Hech qanday mahsulot topilmadi. Iltimos, mahsulotlar bazasini tekshiring.")
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        sale_price_raw = request.POST.get('sale_price')
        quantity_raw = request.POST.get('quantity')

        if not all([product_id, sale_price_raw, quantity_raw]):
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring: mahsulot, miqdor va narx.")
            return redirect('add_sale')

        try:
            sale_price = int(sale_price_raw)
            quantity = int(quantity_raw)
            product = Product.objects.get(id=product_id)
        except (ValueError, Product.DoesNotExist):
            messages.error(request, "Noto'g'ri ma'lumot kiritildi yoki mahsulot topilmadi.")
            return redirect('add_sale')
        
        Sale.objects.create(
            product=product,
            quantity=quantity,
            sale_price=sale_price,
            recorded_by=request.user
        )
        
        messages.success(
            request,
            f"Sotuv ro'yxatga olindi: {quantity} x {product.name} uchun {sale_price:,} SO'M"
        )
        return redirect('add_sale')
    
    return render(request, 'add_sale.html', {'products': products})

@staff_member_required
def sale_list(request):
    # Fetch all sales, pre-fetching product and recorded_by for efficiency
    sales = Sale.objects.select_related('product', 'recorded_by').order_by('-date')
    
    # Calculate Total Revenue in the database (efficient)
    total_revenue = sales.aggregate(total=Sum('sale_price'))['total'] or 0

    # --- NEW CURRENT PERIOD CALCULATIONS ---
    today = date.today()
    today_revenue = sales.filter(date__date=today).aggregate(total=Sum('sale_price'))['total'] or 0
    
    week_start = today - timedelta(days=today.weekday())
    this_week_revenue = sales.filter(date__date__gte=week_start).aggregate(total=Sum('sale_price'))['total'] or 0
    
    month_start = today.replace(day=1)
    this_month_revenue = sales.filter(date__date__gte=month_start).aggregate(total=Sum('sale_price'))['total'] or 0

    # --- END NEW CALCULATIONS ---
    
    return render(request, 'sale_list.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'today': today,
        'today_revenue': today_revenue,
        'week_start': week_start,
        'this_week_revenue': this_week_revenue,
        'month_start': month_start,
        'this_month_revenue': this_month_revenue,
    })

@login_required
def investor_dashboard(request):
    try:
        investor = Investor.objects.get(user=request.user)
    except Investor.DoesNotExist:
        messages.error(request, "Sizda investor profili mavjud emas.")
        return redirect('home')
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Note: Investor earnings now depend on the new Sale.investor_fee property, which is complex.
    # It is safer and more consistent to calculate the total fee paid to ALL investors,
    # and then the individual investor's share of that fee.

    # Calculate total fee paid to all investors for all time
    total_investor_fee_all_time = sum(s.investor_fee for s in Sale.objects.all())
    # Calculate total fee paid to this investor
    total_earnings = total_investor_fee_all_time * (investor.share_percentage / 
                                                   (Investor.objects.aggregate(total=Sum('share_percentage'))['total'] or 1))

    # Calculate today's fee paid to all investors
    today_investor_fee = sum(s.investor_fee for s in Sale.objects.filter(date__date=today))
    # Calculate today's fee paid to this investor
    today_earnings = today_investor_fee * (investor.share_percentage / 
                                          (Investor.objects.aggregate(total=Sum('share_percentage'))['total'] or 1))

    # Calculate week's fee paid to all investors
    week_investor_fee = sum(s.investor_fee for s in Sale.objects.filter(date__date__gte=week_start))
    # Calculate week's fee paid to this investor
    week_earnings = week_investor_fee * (investor.share_percentage / 
                                        (Investor.objects.aggregate(total=Sum('share_percentage'))['total'] or 1))

    # Calculate daily breakdown for last 7 days
    last_7_days = []
    total_share_pct = Investor.objects.aggregate(total=Sum('share_percentage'))['total'] or 1
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_investor_fee = sum(s.investor_fee for s in Sale.objects.filter(date__date=day))
        day_earnings = day_investor_fee * (investor.share_percentage / total_share_pct)
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
        messages.error(request, "Sizda ishchi profili mavjud emas.")
        return redirect('home')

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Since ProductionLog.earnings is now a property, we calculate sums in Python
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
        messages.error(request, "Siz ishchi sifatida ro'yxatdan o'tmagansiz.")
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

        if updated_any:
            messages.success(request, "Ishlab chiqarish jurnallari muvaffaqiyatli yangilandi!")
        else:
            messages.info(request, "Hech qanday ishlab chiqarish miqdori kiritilmadi yoki nol edi.")

        return redirect('worker_dashboard')

    # For GET requests, just render the form
    return render(request, 'add_production.html', {'products': products})