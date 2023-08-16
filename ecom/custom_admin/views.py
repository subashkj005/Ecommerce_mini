from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from accounts.models import Profile
from cart.models import Order, OrderDetail
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
import io
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta, datetime, time




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


def get_order_data(request):
    today = timezone.now()
    seven_days_ago = today - timedelta(days=6)

    orders_by_day = Order.objects.filter(
        date_created__range=(seven_days_ago, today)
    ).values('date_created__day').annotate(order_count=Count('id'))

    order_data = [0] * 7  # Initialize with zeros for all days of the week

    for order in orders_by_day:
        day = (order['date_created__day'] + 6) % 7  # Adjust for array indexing
        order_data[day] = order['order_count']

    return JsonResponse({'order_data': order_data})


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
        this_month_monthly_revenue = OrderDetail.objects.filter(
            order_status='delivered',
            order__date_created__month=month
        ).aggregate(monthly_revenue=Sum('total_price'))

        # Incase whether monthly revenue return None in case of no revenue
        if this_month_monthly_revenue is None:
            this_month_monthly_revenue['monthly_revenue'] = 0

        first_day_of_current_month = current_date.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timezone.timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
        last_month_monthly_revenue = OrderDetail.objects.filter(
            order_status='delivered',
            order__date_created__range=(
                first_day_of_previous_month,
                last_day_of_previous_month)).aggregate(monthly_revenue=Sum('total_price'))

        if this_month_monthly_revenue['monthly_revenue'] is not None and last_month_monthly_revenue[
            'monthly_revenue'] is not None:
            last_month_monthly_revenue_diff = ((this_month_monthly_revenue['monthly_revenue'] -
                                                last_month_monthly_revenue['monthly_revenue']) /
                                               last_month_monthly_revenue['monthly_revenue']) * 100
        else:
            last_month_monthly_revenue_diff = 0

        context = {
            'daily_sales_count': daily_sales_count['delivered_count'],
            'daily_sales_amount': daily_sales_amount['delivered_amount'],
            'daily_orders_count': daily_orders_count['orders_count'],
            'this_month_monthly_revenue': this_month_monthly_revenue['monthly_revenue'],
            'last_month_monthly_revenue_diff': last_month_monthly_revenue_diff,
        }

        return render(request, 'custom_admin/admin_home.html', context)

    return redirect('admin_login')


def users(request):
    if 'username' in request.session:
        user = Profile.objects.all()
        
        if request.method == 'POST':
            search = request.POST.get('search')
            if search:
                user = Profile.objects.filter(name__startswith=search)
        
        return render(request, 'custom_admin/users.html', {'users': user})
    return redirect('admin_login')


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
        all_orders = Order.objects.all().order_by('-date_created')
        # Filter the orders except delivered or cancelled or returned
        filtered_orders = []
        for order in all_orders:
            if order.order_items.exclude(order_status__in=['delivered', 'cancelled', 'returned']).exists():
                filtered_orders.append(order)

        return render(request, 'custom_admin/orders.html', {'orders': filtered_orders})

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

        # Get the datetime with the maximum time value (end of the day) for the given start date and end date
        start_date_strp = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_strp = datetime.strptime(end_date, '%Y-%m-%d')

        start_date_with_time = start_date_strp.replace(hour=23, minute=59, second=59)
        end_date_with_time = end_date_strp.replace(hour=23, minute=59, second=59)

        if selected_report == 'sales':
            # OrderItems where delivered
            delivered_orders = OrderDetail.objects.filter(
                order__date_created__gte=start_date_with_time,
                order__date_created__lte=end_date_with_time,
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
            orders = Order.objects.filter(
                date_created__gte=start_date_with_time,
                date_created__lte=end_date_with_time
            )

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
