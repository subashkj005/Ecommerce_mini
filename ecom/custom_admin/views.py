from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from accounts.models import Profile
from cart.models import Order, OrderDetail
from django.shortcuts import render
from django.http import HttpResponse
from xhtml2pdf import pisa
import io



# Create your views here.

def admin_login(request):
    if 'username' in request.session:
        return render(request,'custom_admin/admin_home.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in and make session
            request.session['username'] = username
            # Redirect to a success page or perform other actions
            return render(request,'custom_admin/admin_home.html')
        else:
            # Authentication failed, display an error message or perform other actions
            error_message = "Invalid username or password"
            return render(request, 'custom_admin/admin_login.html', {'error_message': error_message})

    # If the request method is GET, render the login form
    return render(request, 'custom_admin/admin_login.html')


def admin_home(request):
    if 'username' in request.session:
        return render(request, 'custom_admin/admin_home.html')

    return redirect('admin_login')

def users(request):
    user = Profile.objects.all()
    return render(request, 'custom_admin/users.html', {'users':user})

def user_status(request, id):
    # if 'username' in request.session:
        user = Profile.objects.get(id = id)
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
        return render(request, 'custom_admin/orders.html', {'orders':orders})

    return redirect('admin_login')

def order_details(request, id):
    if 'username' in request.session:
        order = Order.objects.get(id = id)
        return render(request, 'custom_admin/order_details.html', {'order':order})

    return redirect('admin_login')

def order_status_update(request, ord_id, item_id):
    if 'username' in request.session:
        order = Order.objects.get(id = ord_id)
        item = OrderDetail.objects.get(id = item_id)

        if request.method == 'POST':
            status = request.POST.get('order_status')
            if status == 'delivered':
                item.is_delivered = True
                item.order_status = status
                item.save()
            elif status == 'returned':
                item.is_returned = True
                item.order_status = status
                item.save()
            else:
                item.order_status = status
                item.save()

            return redirect('order_details', id=ord_id)

        return render(request, 'custom_admin.html', {'order':order} )
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

        if report == 'sales':
            # OrderItems where delivered
            delivered_orders = OrderDetail.objects.filter(
                order__date_created__gte=start_date,
                order__date_created__lte=end_date,
                is_delivered=True
            )

            template_path = 'pdf/sales-report_pdf.html'
            context = {
                # Creating list of orders with delivered items only
                'orders': [order.order for order in delivered_orders],
                'start_date': start_date,
                'end_date': end_date
            }
        if report == 'orders':
            orders = Order.objects.filter(date_created__gte=start_date, date_created__lte=end_date)

            template_path = 'pdf/orders_report_pdf.html'
            context = {
                # Creating list of orders with delivered items only
                'orders': orders,
                'start_date': start_date,
                'end_date': end_date,
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
