from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from accounts.models import Profile
from cart.models import Order, OrderDetail
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
from django.utils import timezone
from django.db import models
from django.db.models import Sum, F, Count
from datetime import datetime, timedelta
from django.db.models.functions import Extract
from django.db.models.functions import ExtractWeekDay


def admin_login(request):
    if 'username' in request.session:
        return render(request, 'custom_admin/admin_home.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in and make session
            request.session['username'] = username
            # Redirect to a success page or perform other actions
            return render(request, 'custom_admin/admin_home.html')
        else:
            # Authentication failed, display an error message or perform other actions
            error_message = "Invalid username or password"
            return render(request, 'custom_admin/admin_login.html', {'error_message': error_message})

    # If the request method is GET, render the login form
    return render(request, 'custom_admin/admin_login.html')


# def admin_home(request):
#     if 'username' in request.session:
#         return render(request, 'custom_admin/admin_home.html')
#
#     return redirect('admin_login')

# import json
# def get_last_week_dates():
#     today = datetime.now(timezone.utc)
#     # Calculate the date for last Sunday
#     last_sunday = today - timedelta(days=today.weekday() + 1)
#     # Calculate the date for next Saturday
#     next_saturday = last_sunday + timedelta(days=6)
#     return last_sunday, next_saturday
#
#
# def admin_home(request):
#     if 'username' in request.session:
#         last_sunday, next_saturday = get_last_week_dates()
#
#         delivered_orders = Order.objects.filter(
#             date_created__gte=last_sunday,
#             date_created__lte=next_saturday,
#             order_items__is_delivered=True
#         )
#
#         data = delivered_orders.annotate(
#             day_of_week=ExtractWeekDay('date_created'),
#             earnings=Sum(F('order_items__quantity') * F('order_items__price'))
#         ).values('day_of_week').order_by('day_of_week')
#
#         weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
#         earnings_by_day = [0] * 7
#
#         for item in data:
#             day_of_week = item['day_of_week']
#             earnings = item.get('earnings', 0)  # Use get() to handle missing 'earnings'
#             earnings_by_day[day_of_week] = earnings
#
#         # Convert earnings_by_day to a JSON string
#         earnings_by_day_json = json.dumps(earnings_by_day)
#
#         context = {
#             'weekdays': weekdays,
#             'earnings_by_day_json': earnings_by_day_json,  # Pass the JSON data to the template
#         }
#
#         return render(request, 'custom_admin/admin_home.html', context)
#     else:
#         return redirect('admin_login')

from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, Value
from django.db.models.functions import ExtractWeek, ExtractYear
def calculate_weekly_sales():
    today = timezone.now().date()
    one_week_ago = today - timedelta(days=7)

    weekly_sales = OrderDetail.objects.filter(
        order__delivered_date__range=[one_week_ago, today],
        order__order_status='delivered',
        order__delivered_date__week_day__in=[0, 1, 2, 3, 4, 5, 6]  # All days
    ).annotate(
        week=ExtractWeek('order__delivered_date'),
        year=ExtractYear('order__delivered_date')
    ).values('week', 'year').annotate(sales=Sum('total_price'))

    return weekly_sales





from django.db.models import Sum
from django.db.models.functions import TruncWeek
import json
from datetime import timedelta


def admin_home(request):
    if 'username' in request.session:
        # Count of daily delivered products
        today = timezone.now().date()
        month = timezone.now().month
        current_date = timezone.now()
        daily_sales_count = OrderDetail.objects.filter(order_status='delivered',
                                                       order__date_created__date=today).aggregate(
            delivered_count=Count('order'))
        daily_sales_amount = OrderDetail.objects.filter(order_status='delivered',
                                                        order__date_created__date=today).aggregate(
            delivered_amount=Sum('total_price'))
        # Count of daily Orders
        daily_orders_count = OrderDetail.objects.filter(delivered_date=today).aggregate(orders_count=Count('order'))
        # Monthly Revenue
        this_month_monthly_revenue = OrderDetail.objects.filter(order_status='delivered',
                                                                order__date_created__month=month).aggregate(
            monthly_revenue=Sum('total_price'))
        first_day_of_current_month = current_date.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timezone.timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
        last_month_monthly_revenue = OrderDetail.objects.filter(order_status='delivered', order__date_created__range=(
        first_day_of_previous_month, last_day_of_previous_month)).aggregate(monthly_revenue=Sum('total_price'))
        last_month_monthly_revenue_diff = ((this_month_monthly_revenue['monthly_revenue'] - last_month_monthly_revenue[
            'monthly_revenue']) / last_month_monthly_revenue['monthly_revenue']) * 100

        # weekly_sales = calculate_weekly_sales()

        context = {
            'daily_sales_count': daily_sales_count['delivered_count'],
            'daily_sales_amount': daily_sales_amount['delivered_amount'],
            'daily_orders_count': daily_orders_count['orders_count'],
            'this_month_monthly_revenue': this_month_monthly_revenue['monthly_revenue'],
            'last_month_monthly_revenue_diff': last_month_monthly_revenue_diff,
            # 'weekly_sales': weekly_sales,
        }

        return render(request, 'custom_admin/admin_home.html', context)

    return redirect('admin_login')


def users(request):
    user = Profile.objects.all()
    return render(request, 'custom_admin/users.html', {'users': user})


def user_status(request, id):
    # if 'username' in request.session:
    user = Profile.objects.get(id=id)
    if user.is_active:
        user.is_active = 0
        user.save()
        return redirect('users')
    else:
        user.is_active = 1
        user.save()
        return redirect('users')


def admin_logout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('admin_login')


def orders(request):
    if 'username' in request.session:
        orders = Order.objects.all().order_by('date_created')
        return render(request, 'custom_admin/orders.html', {'orders': orders})

    return redirect('admin_login')


def order_details(request, id):
    if 'username' in request.session:
        order = Order.objects.get(id=id)
        return render(request, 'custom_admin/order_details.html', {'order': order})

    return redirect('admin_login')


def order_status_update(request, ord_id, item_id):
    if 'username' in request.session:
        order = Order.objects.get(id=ord_id)
        item = OrderDetail.objects.get(id=item_id)

        if request.method == 'POST':
            status = request.POST.get('order_status')
            if status == 'delivered':
                item.is_delivered = True
                item.order_status = status
                item.delivered_date = timezone.now()
                item.save()
            elif status == 'returned':
                item.is_returned = True
                item.order_status = status
                item.save()
            else:
                item.order_status = status
                item.save()

            return redirect('order_details', id=ord_id)

        return render(request, 'custom_admin.html', {'order': order})
    return redirect('admin_login')


# Reports

def filter_reports(request):
    if request.method == 'POST':
        selected_report = request.POST.get('selected_report')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if selected_report == 'sales':
            # OrderItems where delivered
            delivered_orders = OrderDetail.objects.filter(
                order__date_created__gte=start_date,
                order__date_created__lte=end_date,
                is_delivered=True
            )
            context = {
                # Creating list of orders with delivered items only
                'orders': [order.order for order in delivered_orders],
                'start_date': start_date,
                'end_date': end_date,
                'report': selected_report
            }
            return render(request, 'custom_admin/sales_reports.html', context)

        if selected_report == 'orders':
            orders = Order.objects.filter(date_created__gte=start_date, date_created__lte=end_date)

            context = {
                # Creating list of orders with delivered items only
                'orders': orders,
                'start_date': start_date,
                'end_date': end_date,
                'report': selected_report
            }
            return render(request, 'custom_admin/orders_report.html', context)

    return render(request, 'custom_admin/filter_report.html')


def generate_pdf(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report = request.POST.get('report')

        if report == 'orders':
            orders = Order.objects.filter(date_created__gte=start_date, date_created__lte=end_date)

            template_path = 'pdf/orders_report_pdf.html'
            context = {
                # Creating list of orders
                'orders': orders,
                'start_date': start_date,
                'end_date': end_date,
            }

        if report == 'sales':
            # OrderItems where delivered
            delivered_orders = OrderDetail.objects.filter(
                order__date_created__gte=start_date,
                order__date_created__lte=end_date,
                is_delivered=True
            )

            template_path = 'pdf/sales_report_pdf.html'
            context = {
                # Creating list of orders with delivered items only
                'orders': [order.order for order in delivered_orders],
                'start_date': start_date,
                'end_date': end_date
            }

        # Render the template with form data
        response = render(request, template_path, context)

        # Create a PDF from the rendered HTML
        pdf = generate_pdf_bytes(response.content)

        # Set the response content type for PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        return response
    return render(request, 'custom_admin/filter_report.html')


def generate_pdf_bytes(html):
    # Convert HTML to PDF using xhtml2pdf
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_file)

    if not pisa_status.err:
        return pdf_file.getvalue()

    return None
