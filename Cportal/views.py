from django.contrib.auth import authenticate, login, logout
from django.db.models.query import QuerySet
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import *
from .form import *
from .filters import *
from netmiko import ConnectHandler
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import json
from datetime import datetime
from .decorators import unauthenticated_user, allowed_users, admin_only

@require_POST
def alertapi_view(request):
    #print(request.body)
    alert_data = request.body
    #json_alert = alert_data.decode('utf8').replace("'","\"")
    #print(type(json_alert))
    print(type(alert_data))
    jsondata = json.loads(alert_data)
    print(type(jsondata))
    #print(jsondata['message'])
    print(jsondata)
    return HttpResponse('Hello, world. This is the webhook response.')

def registerPage(request):
    form = UserCreationForm()
    context = {}
    return render(request, 'Cportal/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username OR password is incorrect!")
    context = {}
    return render(request, 'Cportal/Loginpass/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def contact(request):

    def get_ip(request):
        address=request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip(request)

    customer = CustomerInfo.objects.get(username=request.user)
    location = 0
    c = ''
    interface_number = 0
    d = CustomerProperties.objects.filter(name__username=request.user)
    if len(d)>1:
        d = CustomerProperties.objects.filter(name__username=request.user)
        for i in d:
            interface_number += i.connected_interface.count()
            if i.customer_location.location_name:
                location += 1
    else:
        c = CustomerProperties.objects.get(name__username=request.user)
        p = ""
        interface_number = c.connected_interface.count()
        location = c.customer_location.location_name   
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry" 
            body = {
            'first_name': form.cleaned_data['first_name'], 
            'last_name': form.cleaned_data['last_name'], 
            'email': form.cleaned_data['email_address'], 
            'message':form.cleaned_data['message'], 
            }
            message = "\n".join(body.values())
            fr_email = settings.EMAIL_HOST_USER
            try:
                send_mail(subject, message, fr_email, ['mohibul373@gmail.com']) 
                messages.success(request, 'send mail successful.')
            except BadHeaderError:
                return messages.error(request, 'Invalid header found.')
            return HttpResponseRedirect ("contact",{})
        # else:
        #     return render(request, "Cportal/Customer/contact.html",{})   
        
    form = ContactForm()
    context = {
        'customer':customer,
        'ip': ip,
        'c': c,
        # 'p' : p,
        'd': d,
        'inNum': interface_number,
        'location': location,
        'form':form
    }
    
    return render(request, "Cportal/Customer/contact.html", context)

@login_required(login_url='login')
# @allowed_users(allowed_roles=['Customer'])
def bgplay(request):
    def get_ip(request):
        address=request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip(request)
    context = {'ip': ip }
    return render(request, 'Cportal/bgplay.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def route_troubleshoot_customer(request):
    def get_ip(request):
        address=request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip(request)

    customer = CustomerInfo.objects.get(username=request.user)
    location = 0
    c = ''
    interface_number = 0
    d = CustomerProperties.objects.filter(name__username=request.user)
    if len(d)>1:
        d = CustomerProperties.objects.filter(name__username=request.user)
        for i in d:
            interface_number += i.connected_interface.count()
            if i.customer_location.location_name:
                location += 1
    else:
        c = CustomerProperties.objects.get(name__username=request.user)
        p = ""
        interface_number = c.connected_interface.count()
        location = c.customer_location.location_name   
    
    context = {
        'customer':customer,
        'ip': ip,
        'c': c,
        # 'p' : p,
        'd': d,
        'inNum': interface_number,
        'location': location
     }
    return render(request, 'Cportal/Customer/route-check.html', context)

@login_required(login_url='login')
@admin_only
def home(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    user_count = customerproperties.count()
    inter_count = interface.count()
    device_count = devices.count()

    def get_ip(request):
        address=request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip(request)
    print(ip)

    context = {'user': customer,
        'count': user_count,
        'dcount': device_count,
        'icount': inter_count,
        'devices': devices,
        'custpro': customerproperties,
        'ip': ip }

    return render(request, 'Cportal/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def userPage(request):
    customer = CustomerInfo.objects.get(username=request.user)
    # devices = DeviceInfo.objects.all()
    # interface = InterfaceInfo.objects.all()
    # customerproperties = CustomerProperties.objects.all()
    # user_count = customerproperties.count()
    # inter_count = interface.count()
    # device_count = devices.count()
    
    output=''
    ioutput=''
    data=''
    ierror = ''
    location = 0
    c = ''
    interface_number = 0
    
    if request.method == "POST":
        rt = request.POST.get('rt',"")
        dv = request.POST.get('dv',"")
        print(dv)
        print(rt) 
        if dv=="Router":
            ciscoasr = {
                'device_type': 'cisco_xr',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': 'noc',
                'password': 'noc@bsccl',
                }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh controller "+ data +" phy | i x Power")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            net_connect.disconnect()
        elif rt=="192.168.200.14":
            ciscoasr = {
                'device_type': 'cisco_ios_telnet',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': '',
                'password': 'cisco',
                'secret': 'noc@bsccl',
                }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" transceiver detail | b Optical")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
        elif rt=="192.168.200.15":
            ciscoasr = {
                'device_type': 'cisco_ios_telnet',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': '',
                'password': 'cisco',
                'secret': 'bs((1SW@ctg@gr@bad',
            }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" transceiver detail | b Optical")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
        else:
            ciscoasr = {
                'device_type': 'cisco_ios',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': 'admin',
                'password': 'Bsccl@Netw0rk',
                }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" trans details | i Power")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
    
    def get_ip(request):
        address=request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip(request)
    d = CustomerProperties.objects.filter(name__username=request.user)
    if len(d)>1:
        d = CustomerProperties.objects.filter(name__username=request.user)
        for i in d:
            interface_number += i.connected_interface.count()
            if i.customer_location.location_name:
                location += 1
    else:
        c = CustomerProperties.objects.get(name__username=request.user)
        p = ""
        interface_number = c.connected_interface.count()
        location = c.customer_location.location_name

    context = {
        'customer': customer,
        # 'count': user_count,
        # 'dcount': device_count,
        # 'icount': inter_count,
        # 'devices': devices,
        # 'custpro': customerproperties,
        'data':data,
        'ip': ip,
        'c': c,
        # 'p' : p,
        'd': d,
        'inNum': interface_number,
        'output': output,
        'ioutput': ioutput, 
        'ierror': ierror,
        'location': location
        }

    return render(request, 'Cportal/Customer/customer-view.html', context)

@login_required(login_url='login')
#@allowed_users(allowed_roles=['Customer'])
def customer_graph_view(request):
    customer = CustomerInfo.objects.get(username=request.user)
    # devices = DeviceInfo.objects.all()
    # interface = InterfaceInfo.objects.all()
    # customerproperties = CustomerProperties.objects.all()
    # user_count = customerproperties.count()
    # inter_count = interface.count()
    # device_count = devices.count()
    
    output=''
    ioutput=''
    data=''
    ierror = ''
    location = 0
    c = ''
    interface_number = 0
    
    if request.method == "POST":
        rt = request.POST.get('rt',"")
        dv = request.POST.get('dv',"")
        print(dv)
        print(rt) 
        if dv=="Router":
            ciscoasr = {
                'device_type': 'cisco_xr',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': 'noc',
                'password': 'noc@bsccl',
                }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh controller "+ data +" phy | i x Power")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            net_connect.disconnect()
        elif rt=="192.168.200.14":
            ciscoasr = {
                'device_type': 'cisco_ios_telnet',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': '',
                'password': 'cisco',
                'secret': 'noc@bsccl',
                }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" transceiver detail | b Optical")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
        elif rt=="192.168.200.15":
            ciscoasr = {
                'device_type': 'cisco_ios_telnet',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': '',
                'password': 'cisco',
                'secret': 'bs((1SW@ctg@gr@bad',
            }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" transceiver detail | b Optical")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
        else:
            ciscoasr = {
                'device_type': 'cisco_ios',
                # 'ip': '192.168.200.2',
                'ip': rt,
                'username': 'admin',
                'password': 'Bsccl@Netw0rk',
                }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" trans details | i Power")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
    
    def get_ip(request):
        address=request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip(request)
    d = CustomerProperties.objects.filter(name__username=request.user)
    if len(d)>1:
        d = CustomerProperties.objects.filter(name__username=request.user)
        for i in d:
            interface_number += i.connected_interface.count()
            if i.customer_location.location_name:
                location += 1
    else:
        c = CustomerProperties.objects.get(name__username=request.user)
        p = ""
        interface_number = c.connected_interface.count()
        location = c.customer_location.location_name    

    context = {
        'customer': customer,
        # 'count': user_count,
        # 'dcount': device_count,
        # 'icount': inter_count,
        # 'devices': devices,
        # 'custpro': customerproperties,
        'data':data,
        'ip': ip,
        'c': c,
        # 'p' : p,
        'd': d,
        'inNum': interface_number,
        'output': output,
        'ioutput': ioutput, 
        'ierror': ierror,
        'location': location
        }

    return render(request, 'Cportal/Customer/show-graph.html', context)

#Start of PhoneDB creation
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_phoneadd_view(request):

    form = PhoneDBaddInfo()
    if request.method == 'POST':
        form = PhoneDBaddInfo(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Added Successfully!")
            return redirect('phoneinfo')
        else:
            messages.MessageFailure

    custpro = PhonealertDB.objects.all()
    #if request.path == '/userupdateinfo':
    ur = 'phoneupdateinfo'
    dl = 'deletephoneinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_phone_view(request, pk):
    user = PhonealertDB.objects.get(id=pk)
    form = PhoneDBaddInfo(instance=user)
    if request.method == 'POST':
        form = PhoneDBaddInfo(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('phoneinfo')
    custpro = PhonealertDB.objects.all()

    if request.path == '/phoneupdateinfo/'+pk:
        ur = 'phoneupdateinfo'
    else:
        ur = 'phoneupdateinfo'
    dl = 'deletephoneinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_phone_view(request, pk):
    email = PhoneDBaddInfo.objects.get(id=pk)
    if request.method == 'POST':
        email.delete()
        messages.success(request, 'Delete successful')
        return redirect('phoneinfo')
    print(request.path)
    if request.path == '/deletephoneinfo/'+pk:
        dl = 'deletephoneinfo'
    else:
        dl = 'deletephoneinfo'
    context={'item':email, 'dl': dl}
    return render(request, 'Cportal/delete.html', context)

#Start of emailDB creation
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_emailadd_view(request):

    form = EmailDBaddInfo()
    if request.method == 'POST':
        form = EmailDBaddInfo(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Added Successfully!")
            return redirect('emailinfo')
        else:
            messages.MessageFailure

    custpro = EmailalertDB.objects.all()
    #if request.path == '/userupdateinfo':
    ur = 'emailupdateinfo'
    dl = 'deleteemailinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_email_view(request, pk):
    user = EmailalertDB.objects.get(id=pk)
    form = EmailDBaddInfo(instance=user)
    if request.method == 'POST':
        form = EmailDBaddInfo(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('emailinfo')
    custpro = EmailalertDB.objects.all()

    if request.path == '/emailupdateinfo/'+pk:
        ur = 'emailupdateinfo'
    else:
        ur = 'emailupdateinfo'
    dl = 'deleteemailinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_email_view(request, pk):
    email = EmailalertDB.objects.get(id=pk)
    if request.method == 'POST':
        email.delete()
        messages.success(request, 'Delete successful')
        return redirect('emailinfo')
    print(request.path)
    if request.path == '/deleteemailinfo/'+pk:
        dl = 'deleteemailinfo'
    else:
        dl = 'deleteemailinfo'
    context={'item':email, 'dl': dl}
    return render(request, 'Cportal/delete.html', context)

#Start of user creation
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_userinfo_view(request):
    devices = DeviceInfo.objects.all()
    form = CreateUser()
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Added Successfully!")
            return redirect('userinfo')
        else:
            messages.MessageFailure

    custpro = User.objects.all()
    #if request.path == '/userupdateinfo':
    ur = 'userupdateinfo'
    dl = 'deleteuserinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_userinfo_view(request, pk):
    devices = DeviceInfo.objects.all()
    user = User.objects.get(id=pk)
    form = CreateUser(instance=user)
    if request.method == 'POST':
        form = CreateUser(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('userinfo')
    custpro = User.objects.all()

    if request.path == '/userupdateinfo/'+pk:
        ur = 'userupdateinfo'
    else:
        ur = 'userupdateinfo'
    dl = 'deleteuserinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_userinfo_view(request, pk):
    devices = DeviceInfo.objects.all()
    user = User.objects.get(id=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Delete successful')
        return redirect('customerproperties')
    print(request.path)
    if request.path == '/deleteuserinfo/'+pk:
        dl = 'deleteuserinfo'
    else:
        dl = 'deleteuserinfo'
    context={'item':user, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/delete.html', context)

#Customer information add
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_customerinfo_view(request):
    devices = DeviceInfo.objects.all()
    form = CustomeraddInfo()
    if request.method == 'POST':
        form = CustomeraddInfo(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Added Successfully!")
            return redirect('customerinfo')
    custpro = CustomerInfo.objects.all()
    ur = 'customerupdateinfo'
    dl = 'deletecustomerinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_customerinfo_view(request, pk):
    #to update/edit information
    devices = DeviceInfo.objects.all()
    custpro = CustomerInfo.objects.all()
    customer = CustomerInfo.objects.get(id=pk)
    form = CustomeraddInfo(instance=customer)
    if request.method == 'POST':
        form = CustomeraddInfo(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('customerinfo')
    print(request.path)
    if request.path == '/customerupdateinfo/'+pk:
        ur = 'customerupdateinfo'
    else:
        ur = 'customerupdateinfo'

    dl = 'deletecustomerinfo'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_customerinfo_view(request, pk):
    devices = DeviceInfo.objects.all()
    customer = CustomeraddInfo.objects.get(id=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Delete successful')
        return redirect('customerinfo')
    print(request.path)
    if request.path == '/deletecustomerinfo/'+pk:
        dl = 'deletecustomerinfo'
    else:
        dl = 'deletecustomerinfo'
    context={'item':customer, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_customerproperties_view(request):
    devices = DeviceInfo.objects.all()
    custpro = CustomerProperties.objects.all()
    form = CustomeraddProperties()
    if request.method == 'POST':
        form = CustomeraddProperties(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form submission successful')
            return redirect('customerproperties')
    print(request.path)
    if request.path == '/customerproperties':
        ur = 'customerpropertiesupdate'
    else:
        ur = 'customerpropertiesupdate'

    dl = 'deletecustproperties'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_customerproperties_view(request, pk):
    #to update/edit information
    devices = DeviceInfo.objects.all()
    custpro = CustomerProperties.objects.all()
    customer = CustomerProperties.objects.get(id=pk)
    form = CustomeraddProperties(instance=customer)
    if request.method == 'POST':
        form = CustomeraddProperties(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('customerproperties')
    print(request.path)
    if request.path == '/customerpropertiesupdate/'+pk:
        ur = 'customerpropertiesupdate'
    else:
        ur = 'customerpropertiesupdate'

    dl = 'deletecustproperties'
    context = {'form': form, 'custpro': custpro, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_deletecustproperties_view(request, pk):
    devices = DeviceInfo.objects.all()
    customer = CustomerProperties.objects.get(id=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Delete successful')
        return redirect('customerproperties')
    print(request.path)
    if request.path == '/deletecustproperties/'+pk:
        dl = 'deletecustproperties'
    else:
        dl = 'deletecustproperties'
    context={'item':customer, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_location_view(request):

    # user = UserInformation.objects.all()
    devices = DeviceInfo.objects.all()
    form = LocationaddInfo()
    if request.method == 'POST':
        form = LocationaddInfo(request.POST)
        if form.is_valid():
            ln = form.cleaned_data['location_name']
            if LocationInfo.objects.filter(location_name=ln).exists():
                messages.error(request, 'Location Name  "'+ln+'"  already exists!')
                return redirect('locationinfo')
            form.save()
            messages.success(request, 'Form submission successful')
            #return redirect('locationinfo')
            #return HttpResponseRedirect('locationinfo')
    user = CustomerInfo.objects.all()
    location = LocationInfo.objects.all()
    if request.path == '/locationinfo':
        ur = 'locationupdate'
    dl = 'deletelocation'
    context = {'form': form, 'user': user, 'custpro': location, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_location_view(request, pk):
    devices = DeviceInfo.objects.all()
    location = LocationInfo.objects.get(id=pk)
    form = LocationaddInfo(instance=location)
    if request.method == 'POST':
        form = LocationaddInfo(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('locationinfo')
    inter = LocationInfo.objects.all()

    if request.path == '/locationupdate/'+pk:
        ur = 'locationupdate'
    else:
        ur = 'locationupdate'
    dl = 'deletelocation'
    context = {'form': form, 'custpro': inter, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_location_view(request, pk):
    devices = DeviceInfo.objects.all()
    location = LocationInfo.objects.get(id=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Delete successful')
        return redirect('locationinfo')
    print(request.path)
    if request.path == '/deletelocation/'+pk:
        dl = 'deletelocation'
    else:
        dl = 'deletelocation'
    context={'item':location, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def Interface_add_view(request):
    devices = DeviceInfo.objects.all()
    form = InterfaceaddInfo()
    if request.method == 'POST':
        form = InterfaceaddInfo(request.POST)
        if form.is_valid():
            dn = form.cleaned_data['interface_name']
            dv = form.cleaned_data['device']
            if InterfaceInfo.objects.filter(device=dv, interface_name=dn).exists():
                messages.error(request, 'Interface "'+dn+'" on  "' +str(dv)+'"  already exists!')
                return redirect('interfaceinfo')
            form.save()
            messages.success(request, 'Form submission successful')
            return redirect('interfaceinfo')
        else:
            messages.error(request, 'Something wrong!!!')
    inter = InterfaceInfo.objects.all()
    if request.path == '/interfaceinfo':
        ur = 'interfaceupdate'
    dl = 'deleteinterface'
    context = {'form': form, 'custpro': inter, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def Interface_update_view(request, pk):
    devices = DeviceInfo.objects.all()
    #to update/edit information
    interface = InterfaceInfo.objects.get(id=pk)
    form = InterfaceaddInfo(instance=interface)
    if request.method == 'POST':
        form = InterfaceaddInfo(request.POST, instance=interface)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('interfaceinfo')
    inter = InterfaceInfo.objects.all()

    if request.path == '/interfaceupdate/'+pk:
        ur = 'interfaceupdate'
    else:
        ur = 'interfaceupdate'
    dl = 'deleteinterface'
    context = {'form': form, 'custpro': inter, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_interface_view(request, pk):
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.get(id=pk)
    if request.method == 'POST':
        interface.delete()
        messages.success(request, 'Delete successful')
        return redirect('interfaceinfo')
    print(request.path)
    if request.path == '/deleteinterface/'+pk:
        dl = 'deleteinterface'
    else:
        dl = 'deleteinterface'
    context={'item':interface, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def device_add_view(request):
    devices = DeviceInfo.objects.all()
    form = DeviceaddInfo()
    if request.method == 'POST':
        form = DeviceaddInfo(request.POST)
        if form.is_valid():
            dn = form.cleaned_data['device_name']
            if DeviceInfo.objects.filter(device_name=dn).exists():
                messages.error(request, 'Device Name  "'+dn+'"  already exists!')
                return redirect('deviceinfo')
            form.save()
            messages.success(request, 'Form submission successful')
            return redirect('deviceinfo')
            #return HttpResponseRedirect('deviceinfo')
            #devices = DeviceInfo.objects.all()
        else:
            messages.error(request, 'Something wrong!!!')
    if request.path == '/deviceinfo':
        ur = 'deviceupdate'
    dl = 'deletedevice'
    df = DeviceInfo.objects.all()
    context = {'form': form, 'custpro': df, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def device_update_view(request, pk):
    devices = DeviceInfo.objects.all()
    #to update/edit information
    device = DeviceInfo.objects.get(id=pk)
    form = DeviceaddInfo(instance=device)
    if request.method == 'POST':
        form = DeviceaddInfo(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            return redirect('deviceinfo')
    inter = DeviceInfo.objects.all()

    if request.path == '/deviceupdate/'+pk:
        ur = 'deviceupdate'
    else:
        ur = 'deviceupdate'

    dl = 'deletedevice'

    context = {'form': form, 'custpro': inter, 'ur': ur, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/creation_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_device_view(request, pk):
    devices = DeviceInfo.objects.all()
    device = DeviceInfo.objects.get(id=pk)
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Delete successful')
        return redirect('deviceinfo')
    print(request.path)
    if request.path == '/deletedevice/'+pk:
        dl = 'deletedevice'
    else:
        dl = 'deletedevice'
    context={'item':device, 'dl': dl, 'devices': devices}
    return render(request, 'Cportal/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def device_view(request):
    devices = DeviceInfo.objects.all()

    context = {'devices': devices }
    return render (request, 'Cportal/device_detail.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def customer_view(request):
    customers = CustomerProperties.objects.all()
    devices = DeviceInfo.objects.all()

    context = {'customers': customers, 'devices': devices }
    return render (request, 'Cportal/customer_detail.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def interface_view(request):
    devices = DeviceInfo.objects.all()
    interfaces = InterfaceInfo.objects.all()
    intFilter = InterfaceFilter(request.GET, queryset=interfaces)
    interfaces = intFilter.qs 
    context = {'interfaces': interfaces, 'intFilter':intFilter, 'devices': devices}
    return render (request, 'Cportal/interface_detail.html', context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def clientdetails_view(request, pk):
    
    c = CustomerProperties.objects.get(id=pk)
    output=''
    ioutput=''
    data=''
    ierror = ''
    if request.method == "POST":
        rt = request.POST.get('rt',"")
        dv = request.POST.get('dv',"")
        print(dv)
        print(rt) 
        if dv=="Router":
            ciscoasr = {
            'device_type': 'cisco_xr',
            # 'ip': '192.168.200.2',
            'ip': rt,
            'username': 'noc',
            'password': 'noc@bsccl',
            }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh controller "+ data +" phy | i x Power")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            net_connect.disconnect()
        elif rt=="192.168.200.14":
            ciscoasr = {
            'device_type': 'cisco_ios_telnet',
            # 'ip': '192.168.200.2',
            'ip': rt,
            'username': '',
            'password': 'cisco',
            'secret': 'noc@bsccl',
            }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" transceiver detail | b Optical")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
        elif rt=="192.168.200.15":
            ciscoasr = {
            'device_type': 'cisco_ios_telnet',
            # 'ip': '192.168.200.2',
            'ip': rt,
            'username': '',
            'password': 'cisco',
            'secret': 'bs((1SW@ctg@gr@bad',
            }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            #print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" transceiver detail | b Optical")
            # print(output)
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            net_connect.disconnect()        
        else:
            ciscoasr = {
            'device_type': 'cisco_ios',
            # 'ip': '192.168.200.2',
            'ip': rt,
            'username': 'admin',
            'password': 'Bsccl@Netw0rk',
            }
            data = request.POST.get('cmd',"")
            ierror = request.POST.get('errors',"")
            print(data)
            net_connect = ConnectHandler(**ciscoasr)
            output = net_connect.send_command("sh int "+ data +" trans details | i Power")
            ioutput = net_connect.send_command("sh int "+ ierror +" | i error")
            print(output)
            net_connect.disconnect()
        
    interface_number = c.connected_interface.count()
    context = {'c': c, 'inNum': interface_number, 'output': output, 'data':data, 'ioutput': ioutput, 'ierror': ierror}
    return render (request, 'Cportal/customer-admin-view.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def customer_profile_view(request):
    #to update/edit information
    custpro = CustomerInfo.objects.all()
    d = CustomerProperties.objects.filter(name__username=request.user)
    customer = CustomerInfo.objects.get(username=request.user)
    form = CustomerprofileInfo(instance=customer)
    if request.method == 'POST':
        form = CustomerprofileInfo(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form update successful')
            
    context = {'form': form, 'custpro': custpro, 'customer':customer, 'd': d }
    return render(request, 'Cportal/Customer/customer-profile.html', context)

#start of router access views logic
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def dhk_core_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.200.2',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route summary detail")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}
    return render(request, 'Cportal/Router/BSCCL-DHK-CORE-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def DHK_AGG_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.200.4',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route vrf all summary")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-DHK-AGG-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def COX_CORE_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.200.8',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route vrf all summary")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-COX-CORE-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def COX_CORE_02_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.200.6',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route summary detail")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-COX-CORE-02.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def KKT_CORE_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.202.150',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route vrf all summary")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-KKT-CORE-RTR-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def KKT_CORE_02_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.202.151',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route vrf all summary")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-KKT-CORE-RTR-02.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def nexus_sw_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoSW = {
        'device_type': 'cisco_ios',
        'ip': '192.168.200.18',
        'username': 'admin',
        'password': 'Bsccl@Netw0rk',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'intstatus' in request.POST:
            output = net_connect.send_command("sh int status")
        elif 'showvlan' in request.POST:
            output = net_connect.send_command("sh vlan")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-NEXUS-SW-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def nexus_sw_02_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoSW = {
        'device_type': 'cisco_ios',
        'ip': '192.168.200.19',
        'username': 'admin',
        'password': 'Bsccl@Netw0rk',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'intstatus' in request.POST:
            output = net_connect.send_command("sh int status")
        elif 'showvlan' in request.POST:
            output = net_connect.send_command("sh vlan")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-AGG-NEXUS-SW.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def nexus_NRB_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoSW = {
        'device_type': 'cisco_ios',
        'ip': '192.168.200.23',
        'username': 'admin',
        'password': 'Bsccl@Netw0rk',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'intstatus' in request.POST:
            output = net_connect.send_command("sh int status")
        elif 'showvlan' in request.POST:
            output = net_connect.send_command("sh vlan")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-NRB-POP.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def nexus_cox_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoSW = {
        'device_type': 'cisco_ios',
        'ip': '192.168.200.22',
        'username': 'admin',
        'password': 'Bsccl@Netw0rk',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'intstatus' in request.POST:
            output = net_connect.send_command("sh int status")
        elif 'showvlan' in request.POST:
            output = net_connect.send_command("sh vlan")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-COX-NEXUS-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def access_sw_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    now = datetime.now()
    month = now.strftime("%b")
    day = now.strftime("%d")
    
    ciscoSW = {
        'device_type': 'cisco_ios_telnet',
        'ip': '192.168.200.14',
        'username': '',
        'password': 'cisco',
        'secret': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'intstatus' in request.POST:
            output = net_connect.send_command("sh int status")
        elif 'showvlan' in request.POST:
            output = net_connect.send_command("sh vlan")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging | i "+ month +" "+day)
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-ACCESS-SW-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def access_sw_CTG_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoSW = {
        'device_type': 'cisco_ios_telnet',
        'ip': '192.168.200.15',
        'username': '',
        'password': 'cisco',
        'secret': 'bs((1SW@ctg@gr@bad',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'intstatus' in request.POST:
            output = net_connect.send_command("sh int status")
        elif 'showvlan' in request.POST:
            output = net_connect.send_command("sh vlan")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-CTG-SW-01.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def access_sw_CTG_view_02(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoSW = {
        'device_type': 'cisco_ios',
        'ip': '192.168.200.26',
        'username': 'admin',
        'password': 'Bsccl@Netw0rk',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoSW)
        if 'showint' in request.POST:
            output = net_connect.send_command_timing(
                command_string="sh int des", 
                strip_prompt=False,
                strip_command=False
            )
        elif 'intstatus' in request.POST:
            output = net_connect.send_command_timing(
                command_string="sh int status", 
                strip_prompt=False,
                strip_command=False
            )
        elif 'showvlan' in request.POST:
            output = net_connect.send_command_timing(
                command_string="sh vlan", 
                strip_prompt=False,
                strip_command=False
                )
        elif 'showlog' in request.POST:
            output = net_connect.send_command_timing(
                command_string="sh logging", 
                strip_prompt=False,
                strip_command=False
                )
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command_timing(
                command_string=str(cd), 
                strip_prompt=False,
                strip_command=False
                )
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Switch/BSCCL-CTG-SW-02.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def EQ_RT_01_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.203.1',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route vrf all summary")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-EQ-RTR-01.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def EQ_RT_02_view(request):
    customer = CustomerInfo.objects.all()
    devices = DeviceInfo.objects.all()
    interface = InterfaceInfo.objects.all()
    customerproperties = CustomerProperties.objects.all()
    
    ciscoasr = {
        'device_type': 'cisco_xr',
        'ip': '192.168.203.3',
        'username': 'noc',
        'password': 'noc@bsccl',
        }

    cmd=''
    output=''
    #net_connect.find_prompt()
    if request.method == "POST":
        net_connect = ConnectHandler(**ciscoasr)
        if 'showint' in request.POST:
            output = net_connect.send_command("sh int des")
        elif 'showroute' in request.POST:
            output = net_connect.send_command("sh route vrf all summary")
        elif 'showbgp' in request.POST:
            output = net_connect.send_command("sh bgp vrf network summary")
        elif 'showpolicy' in request.POST:
            output = net_connect.send_command("sh run policy-map ?")
        elif 'showlog' in request.POST:
            output = net_connect.send_command("sh logging last 20")
        elif 'cmd' in request.POST:
            cd = request.POST.get("cmd", None)
            cmd = net_connect.send_command(cd)
        else:
            output = "Click Buttons you need"
        net_connect.disconnect()

    # if request.method == "POST":
    # 	cd = request.POST.get("cmd", None)
    # 	cmd = net_connect.send_command(cd)

    context = {'user': customer,
        'devices': devices,
        'custpro': customerproperties,
        'output': output,
        'cmd': cmd}

    return render(request, 'Cportal/Router/BSCCL-EQ-RTR-02.html', context)
