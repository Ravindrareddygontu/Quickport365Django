import razorpay
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, DomesticForm, InternationalForm, ParcelDetailsForm, OrderDetailsForm, ComplaintForm, \
   DriverDetailsForm
from .forms import UpdateOrderStatus, AdminDriverForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import OrderDetails, Complaint, Drivers_orders, Admin_driver, ParcelDetails
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import send_mail
from twilio.rest import Client
from django.core.paginator import Paginator
from datetime import *
import requests
from django.contrib import messages
from .serializers import *


def base(request):
    # msg = 'hii'
    # send_mail(
    #     'sending mail regarding new order',msg,
    #     , 'mani.mallula@gmail.com', ['ravindrareddy72868@gmail.com']
    #     fail_silently=False,
    # )
    return render(request, 'base.html')


def home(request):
    if request.method == 'POST':
        range = request.session['range']
        if range == 'Domestic':
            form = DomesticForm(request.POST)
            if form.is_valid():
                request.session['range'] = request.POST
                print(request.POST)
                return HttpResponseRedirect('parcel')
            else:
                return render(request, 'home.html', {'form': form, 'range': range})
    range = request.GET.get('range')
    if range == 'Domestic':
        form = DomesticForm
        request.session['range'] = range
    else:
        request.session['range'] = range
        form = InternationalForm
    return render(request, 'home.html', {"form": form, 'range': range})


@login_required(login_url='login')
def parcel(request):
    print(request.session['range'])
    if request.method == 'POST':
        request.session['summary'] = request.POST
        form = ParcelDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES)
            form.save()
            return HttpResponseRedirect('summary')
        else:
            return render(request, 'parcel.html', {'parcel_form': form})
    parcel_form = ParcelDetailsForm
    return render(request, 'parcel.html', {'parcel_form': parcel_form})


@login_required(login_url='login')
def booking(request):
    fm = OrderDetails.objects.all().filter(user=request.user).order_by('id')
    paginator = Paginator(fm, 2, orphans=1)
    page_number = request.GET.get('page')
    order_page = paginator.get_page(page_number)
    total = len(fm)
    return render(request, 'booking.html', {'order_page': order_page, 'total': total})


def tracking(request):
    return render(request, 'tracking.html')


def history(request):
    print(request.GET)
    date = request.GET.get('payment')

    def mdy_to_ymd(d):
        return datetime.strptime(d, '%b. %d, %Y').strftime('%Y-%m-%d')

    print(mdy_to_ymd(date))
    fm = OrderDetails.objects.filter(date=mdy_to_ymd(date))
    print(request.GET.get('payment'))
    for i in fm:
        print(i.date)
    return render(request, "history.html", {'form': fm})


def profiles(request):
    fm = User.objects.all()
    print(fm, '.......................................')
    return render(request, 'profiles.html', {'form': fm})


def order_summary(request):

    print('hi')
    print(request.POST)
    summary = request.session['summary']
    return render(request, 'order_summary.html', {'summary': summary})


def payment_details(request):
    request.session['address'] = {}
    print(request.GET)
    try:
        request.session['service'] = request.GET.get('service')
        print(request.session['service'])
    except Exception as e:
        print(e)

    if request.GET.get('service') == 'Standard':
        price = int(request.session['summary']['item_weight']) * 120
        request.session['price'] = price
        days = 3
        return render(request, 'payment_details.html', {'price': price, 'days': days})
    if request.GET.get('service') == 'Premium':
        price = int(request.session['summary']['item_weight']) * 250
        request.session['price'] = price
        days = 1
        return render(request, 'payment_details.html', {'price': price, 'days': days})
    return render(request, 'payment_details.html')


# def address_enter(request):
#     if request.method == 'POST':
#         request.session['address'] = request.POST
#         print(request.session['address'])
#         return HttpResponseRedirect('payment_options')
#     return render(request, 'address.html')

def address_enter(request):
    def address_with_pincode(pincode):
        response = requests.get(f"https://api.postalpincode.in/pincode/{pincode}").json()
        address = {}
        for i in response:
            address['city'] = i['PostOffice'][0]['Block']
            address['district'] = i['PostOffice'][0]['District']
            address['state'] = i['PostOffice'][0]['State']
        return address

    if request.method == 'GET':
        print(request.GET)
        if 'pickup_pincode' in request.GET:
            try:
                paddress = address_with_pincode(request.GET['pickup_pincode'])
                request.session['ppincode'] = request.GET['pickup_pincode']
            except Exception as e:
                print(e, '-')
                messages.success(request, 'Enter correct pincode')
                return render(request, 'address.html')
            pickup_context = {'pcity': paddress['city'], 'pdistrict': paddress['district'], 'pstate': paddress['state']}
            request.session['address']['pickup'] = pickup_context
        if 'delivery_pincode' in request.GET:
            print('delivery')
            try:
                daddress = address_with_pincode(request.GET['delivery_pincode'])
                request.session['dpincode'] = request.GET['delivery_pincode']
            except Exception as e:
                print(e, '--')
                messages.error(request, 'Enter correct pincode')
                return render(request, 'address.html')
            delivery_context = {'dcity': daddress['city'], 'ddistrict': daddress['district'],
                                'dstate': daddress['state']}
            request.session['address']['delivery'] = delivery_context
        if 'address' in request.session:
            request.session.modified = True
            if 'pickup' in request.session['address'] and 'delivery' in request.session['address']:
                pickup = request.session['address']['pickup']
                delivery = request.session['address']['delivery']
                context = {'pcity': pickup['pcity'], 'pdistrict': pickup['pdistrict'], 'pstate': pickup['pstate'],
                           'dcity': delivery['dcity'], 'ddistrict': delivery['ddistrict'], 'dstate': delivery['dstate'],
                           'ppincode': request.session['ppincode'], 'dpincode': request.session['dpincode']}
                return render(request, 'address.html', context)
            if 'pickup' in request.session['address']:
                pickup = request.session['address']['pickup']
                print(pickup)
                context = {'pcity': pickup['pcity'], 'pdistrict': pickup['pdistrict'], 'pstate': pickup['pstate'],
                           'ppincode': request.session['ppincode']}
                return render(request, 'address.html', context)
            if 'delivery' in request.session['address']:
                delivery = request.session['address']['delivery']
                context = {'dcity': delivery['dcity'], 'ddistrict': delivery['ddistrict'], 'dstate': delivery['dstate'],
                           'dpincode': request.session['dpincode']}
                return render(request, 'address.html', context)

        return render(request, 'address.html')

    if request.method == "POST":
        print(request.POST)
        if 'pickup' in request.session['address'] and 'delivery' in request.session['address']:
            return HttpResponseRedirect('payment_options')
        else:
            messages.error(request, 'enter all fields')
            return render(request, 'address.html')


def payment_options(request):
    # if request.method == 'POST':
    #     amount  = 50000
    #     order_currency = 'INR'
    #     client = razorpay.Client(auth=('rzp_test_6lrPUDLV0dRFf9', 'OjNBfOuoD0M8yl3Gkeo9YuJK'))
    #     payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
    price = request.session['price']
    delivery_address = ' '
    delivery_address += request.session['address']['delivery']['dcity'] + ' ,'
    delivery_address += request.session['address']['delivery']['ddistrict'] + ', '
    delivery_address += request.session['dpincode']
    print(request.session['range'])
    return render(request, 'payment_options.html', {'price': price, 'delivery': delivery_address})


@csrf_exempt
def success(request):
    print(request.session['range'])
    print(request.session['address'])
    pickup = request.session['address']['pickup']
    delivery = request.session['address']['delivery']
    order = OrderDetails(user=request.user, origin=request.session['range']['origin_pincode'],
                         destination=request.session['range']['destination_pincode'],
                         item_weight=request.session['summary']['item_weight'],
                         item_name=request.session['summary']['item_name'],
                         date=request.session['summary']['pickup_date'],
                         services=request.session['service'],
                         price=request.session['price'], status='started', receiver_name=request.session['summary']['receiver_name'],
                         receiver_phone=request.session['summary']['receiver_phone'],
                         pickup_address=f'{pickup["pcity"]},{pickup["pdistrict"]},{pickup["pstate"]}',
                         delivery_address=f'{delivery["dcity"]},{delivery["ddistrict"]},{delivery["dstate"]}')
    order.save()
    # msg = f"new order has came please accept and pickup the parcel from {request.session['address']['pickup'][
    # 'pcity']}" \ f" and deliver " \ f"to area = {request.session['address']['delivery']['dcity']} , " \ f"location
    # = {request.session['address']['delivery']['ddistrict']}," \ f"pincode= {request.session['dpincode']} ,
    # " \ f"receiver_phone={request.session['range']['receiver_phone']} , " send_mail( 'sending mail regarding new
    # order', msg, 'ravindrareddy72868@gmail.com', [drivers_emails[1]], fail_silently=False, ) request.session[
    # 'driver'] = drivers_emails[1] client = Client('AC2bf4c0d59ce8e22adaf36f66db8e94d7',
    # '75b5458d5839d0732541b151c35b6f72') message = client.messages.create( body=msg, from_='+17816508594',
    # 93' # ) # print('message send') to='+9172868539
    return render(request, 'success.html', {'order': order})


def sign(request):
    if request.method == "POST":
        fm = SignUpForm(request.POST)

        if fm.is_valid():
            fm.save()
            messages.success(request, 'Account Created Successfully !!')
    else:
        fm = SignUpForm()
    return render(request, 'signup.html', {'form': fm})


def logins(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            fm = AuthenticationForm(request=request, data=request.POST)
            if fm.is_valid():
                uname = fm.cleaned_data['username']
                upass = fm.cleaned_data['password']
                user = authenticate(username=uname, password=upass)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Logged in successfully !!')
                    return HttpResponseRedirect('/')
        else:
            fm = AuthenticationForm()
        return render(request, 'login.html', {'form': fm})
    else:
        return HttpResponseRedirect('/sign')


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {'name': request.user})
    else:
        return HttpResponseRedirect('/login')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/sign')


def admin_dashboard(request):
    status = request.GET.get('status')

    def status_orders(orders):
        total = len(orders)
        paginator = Paginator(orders, 2, orphans=1)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'admin_dashboard.html', {'page_obj': page_obj, 'total': total})

    Pending = OrderDetails.objects.filter(picked=None).order_by('id')
    In_Process = OrderDetails.objects.filter(picked=True, status='in_process').order_by('id')
    Picked = OrderDetails.objects.filter(picked=True).order_by('id')
    Delivered = OrderDetails.objects.filter(picked=True, status='completed').order_by('id')
    status_list = {'Pending': Pending, 'In_Process': In_Process, 'Picked': Picked, 'Delivered': Delivered}

    for order_status in status_list:
        if order_status == status:
            return status_orders(status_list[order_status])
            break

    orders = OrderDetails.objects.all().order_by('id')
    total_orders = len(orders)
    paginator = Paginator(orders, 2, orphans=1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_dashboard.html', {'page_obj': page_obj, 'total': total_orders})


from django.db.models import Q


def driver_dashboard(request):
    driver = Admin_driver.objects.get(name=request.user)
    if driver:
        request.session['sta'] = request.POST
        print('------------------------------')
        orders = OrderDetails.objects.filter(Q(picked=None) | Q(picked=False)).order_by('id')
        print(orders)
        paginator = Paginator(orders, 2, orphans=1)
        page_number = request.GET.get('page')
        orders = paginator.get_page(page_number)
        return render(request, 'driver_dashboard.html', {'all': orders, 'total': len(orders), 'driver': driver})
    else:
        return render(request, 'driver_dashboard.html')


def edit_order(request, id):
    model = OrderDetails.objects.get(pk=id)
    form = OrderDetailsForm(instance=model)
    driver = Admin_driver.objects.get(name=request.user)
    if request.method == 'POST':
        form = OrderDetailsForm(request.POST, instance=model)
        if form.is_valid():
            picked = form.cleaned_data['picked']
            if picked == True:
                from .models import Drivers_orders
                driver_order = Drivers_orders(driver=request.user, order=model).save()
                model.driver = driver
                model.driver_phone = driver.phone
                model.save(update_fields=['driver', 'driver_phone'])
                print('--------------------------')
            form.save()

            print(request.user)

        return HttpResponseRedirect('/driver_dashboard')
    else:
        return render(request, 'edit.html', {'form': form})


def orders_picked(request):
    orders = Drivers_orders.objects.filter(driver=request.user).order_by('id')
    paginator = Paginator(orders, 2, orphans=1)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    total = len(orders)
    return render(request, 'driver_orders.html', {'orders': orders, 'total': total})


def update_status(request, id):
    model = OrderDetails.objects.get(id=id)
    form = UpdateOrderStatus(instance=model)
    if request.POST:
        form = UpdateOrderStatus(request.POST, instance=model)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/orderspicked')
    return render(request, 'update_status.html', {'form': form})


@login_required(login_url='login')
def complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['booking_id']
            iss = form.cleaned_data['issue']
            reg = Complaint(booking_id=book, issue=iss, user=request.user)
            reg.save()
            form = ComplaintForm()
    else:
        form = ComplaintForm()
    stud = Complaint.objects.filter(user=request.user)
    return render(request, 'complaint.html', {'form': form, 'stu': stud})


def list_drivers(request):
    drivers = Admin_driver.objects.all().order_by('id')
    paginator = Paginator(drivers, per_page=1, orphans=1)
    page_num = request.GET.get('page')
    drivers = paginator.get_page(page_num)
    return render(request, 'list_drivers.html', {'drivers': drivers})


def user_complaints(request):
    comp = Complaint.objects.all()
    return render(request, 'user_complaints.html', {'comp': comp})


def complaint_order(request):
    order_details = OrderDetails.objects.all()
    comp = Complaint.objects.all()

    return render(request, 'complaint_order.html', {'comp': comp, 'order_details': order_details})


def first(request):
    return render(request, 'first.html')


def admin_driver(request):
    if request.method == 'POST':
        form = AdminDriverForm(request.POST)
        print(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            form.save()
            print(form, '------------')
            reg = Admin_driver.objects.get(name=form.cleaned_data['name'])

            print(reg.id, '--------------sdkjfha')
            msg = f'click the link to complete your details:http://127.0.0.1:8000/driver_details/{reg.id}\n' \
                  f'Temparory password: hyd0055'
            print(msg)
            print(email)
            send_mail(
                'Testing Mail',
                msg,
                'ravindrareddy72868@gmail.com',
                [email],
                fail_silently=False)
            print('success', '==================')
    else:
        form = AdminDriverForm()
    return render(request, 'add_driver.html', {'form': form})


def driver_details(request, id):
    print(request.session)
    print(request.user)
    model = Admin_driver.objects.get(id=id)
    form = DriverDetailsForm(instance=model)
    if request.method == 'POST':
        form = DriverDetailsForm(request.POST, instance=model)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['new_password']
            form.save()
            user = User.objects.create_user(name, email, password)
            user.is_staff = True
            user.save()
            return HttpResponseRedirect('/')
    return render(request, 'driver_details.html', {'form': form})


