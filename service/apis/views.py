from service.serializers import *
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, NotAcceptable, ValidationError
from rest_framework.response import Response
import jwt
import requests
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.contrib.auth import login, logout
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
import requests
from django.core.mail import send_mail
from rest_framework import permissions
from django.db.models import Q
from django.core import serializers


class ParcelDetailsdetails(ModelViewSet):
    queryset = ParcelDetails.objects.all()
    serializer_class = ParcelDetailsSerializer
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]


class AdminDriverView(ModelViewSet):
    queryset = Admin_driver.objects.all()
    serializer_class = Admin_driverSerializer


class IsAuthenticatedAndStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        print(request.user, '----------')
        return request.user.is_authenticated and request.user.is_staff


class UserOrdersView(APIView):
    def get(self, request, id=None):
        user = User.objects.get(id=id)
        orders = OrderDetails.objects.filter(user=user)
        serializer = OrderDetailsSerializer(orders, many=True)
        return Response(serializer.data)


class DriverPickedOrdersView(APIView):
    def get(self, request, id=None):
        user = User.objects.get(id=id)
        driver = Admin_driver.objects.get(name=user.username)
        driver_orders = OrderDetails.objects.filter(driver=driver)
        serializer = OrderDetailsSerializer(driver_orders, many=True)
        return Response(serializer.data)


class OrderdetailsView(ModelViewSet):
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = OrderDetails.objects.all()
    serializer_class = OrderDetailsSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['delivery_address'] = ','.join(data['delivery_address'].values())
        data['pickup_address'] = ','.join(data['pickup_address'].values())
        print(data, 'ddddddddddddd')
        serializer = self.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    # def get_permissions(self):
    #     if self.request.method == 'PATCH':
    #         self.permission_classes = [IsAuthenticatedAndStaff]
    #     return super().get_permissions()


class OrderdetailsPendingView(ModelViewSet):
    queryset = OrderDetails.objects.filter(Q(picked=False) | Q(picked=None))
    serializer_class = OrderDetailsSerializerPending


class OrderdetailsPickedView(ModelViewSet):
    queryset = OrderDetails.objects.filter(picked=True)
    serializer_class = OrderDetailsSerializerPicked


class OrderdetailsProcessView(ModelViewSet):
    queryset = OrderDetails.objects.filter(picked=True, status='in_process')
    serializer_class = OrderDetailsSerializerInProcess


class OrderdetailsDeliveredView(ModelViewSet):
    queryset = OrderDetails.objects.filter(picked=True, status='completed')
    serializer_class = OrderDetailsSerializerDelivered


class Drivers_ordersView(ModelViewSet):
    queryset = Drivers_orders.objects.all()
    serializer_class = Drivers_ordersSerializer


class ComplaintView(ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer


class Signup(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username, password)
        user = User.objects.filter(username=username).first()
        if user is not None:
            if user.check_password(password):
                login(request, user)
                print(request.session.__dict__)
                if user.is_superuser:
                    role = 'is_superuser'
                elif user.is_staff and not user.is_superuser:
                    role = 'is_staff'
                else:
                    role = 'is_active'
                return Response({
                    'status': 'success',
                    'data': {'user': username},
                    'user_id':user.id,

                    'role': role,
                    'message': 'login successful'
                })
            else:
                raise AuthenticationFailed('Incorrect Password')
        else:
            raise AuthenticationFailed('user not found')

        # payload = {
        #     'id': user.id,
        #     'exp': datetime.utcnow()+timedelta(minutes=5),
        #     'iat': datetime.utcnow()
        # }
        # token = jwt.encode(payload, 'secret', algorithm='HS256')
        # response = Response()
        # response.set_cookie(key='jwt', value=token, httponly=True)
        # print(request.COOKIES)
        # response.data = {
        #     'jwt': token
        # }


class PincodeView(APIView):
    def post(self, request):
        print(request.data)
        origin_pin = request.data.get('OriginalPincode')
        destination_pin = request.data.get('DestinationPincode')
        origin = requests.get(f"https://api.postalpincode.in/pincode/{origin_pin}").json()
        destination = requests.get(f"https://api.postalpincode.in/pincode/{destination_pin}").json()
        if destination[0]['Status'] == 'Success' and origin[0]['Status'] == 'Success':
            return Response({
                'status': 'success',
                'data': {'origin_pincode': origin_pin,
                         'destination_pincode': destination_pin},
                'message': 'Pincode validation successful'
            })
        else:
            raise ValidationError({
                'status': 'failure',
                'data': None,
                'message': 'Invalid Pincodes'
            })


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        print('yes')
        return Response('logged out succefully')


class ServiceView(APIView):
    def get(self, request):
        price, days = 0, ''
        if request.GET.get('service') == 'standard':
            price = 500
            days = '3 to 4 days'
        if request.GET.get('service') == 'premium':
            price = 800
            days = '1 to 2 days'
        return Response({
            'status': 'Success',
            'data': {
                'price': price,
                'days': days
            }
        })


class GetAddressView(APIView):
    def get(self, request):
        pincode = request.GET.get('pincode')
        print(pincode)
        response = requests.get(f"https://api.postalpincode.in/pincode/{pincode}").json()
        if response[0]['Status'] != 'Error':
            for i in response:
                response = {
                    'Mandal': i['PostOffice'][0]['Block'],
                    'District': i['PostOffice'][0]['District'],
                    'State': i['PostOffice'][0]['State']
                }
        return Response({
            'status': 'success',
            'data': response
        })


class DriverEntryByAdminView(APIView):
    def post(self, request):
        print(request.data, '===========')
        serializer = DriverEntryByAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data,'--------')
        driver = Admin_driver.objects.get(name=serializer.data.get('name'))
        print(driver.email)
        msg = f'click the link to complete your details:http://127.0.0.1:3000/DriverSignup/{driver.id}/\n' \
              f'Temparory password: hyd0055'
        send_mail(
            'Testing Mail', msg, 'ravindrareddygontu@gmail.com', [driver.email], fail_silently=False)
        return Response({
            'status': 'success',
            'data': 'driver entry successfull and mail has sent'
        })


class DriverSignupView(APIView):
    def post(self, request):
        serializer = DriverSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'response': 'success',
            'data': 'driver signup successful'
        })