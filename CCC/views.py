from django.shortcuts import render,redirect
from .models import *
from django.db.models import Sum
from django.http  import HttpResponse
import math
import random
import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import csv
from random import *
import string
from CCC import Checksum

from CCC.utils import VerifyPaytmResponse
from django.views.decorators.csrf import csrf_exempt

###################Paytm#############




def payment(request):
    
    order_id = Checksum.__id_generator__()
    bill_amount = "100"
    data_dict = {
        'MID': "cTSIBy37736701153348",
        'INDUSTRY_TYPE_ID': "Retail",
        'WEBSITE': settings.PAYTM_WEBSITE,
        'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
        'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
        'MOBILE_NO': '8347386541',
        'EMAIL': 'gohilbhavesh1997@gmail.com',
        'CUST_ID': '123123',
        'ORDER_ID':order_id,
        'TXN_AMOUNT': bill_amount,
    } # This data should ideally come from database
    print(settings.PAYTM_MERCHANT_KEY)
    print(settings.PAYTM_MERCHANT_ID)
    data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, "mA&OnVHKf%aur&J8")
    print(data_dict)
    context = {
        'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
        'comany_name': settings.PAYTM_COMPANY_NAME,
        'data_dict': data_dict
    }
    return render(request, 'car/payment.html', context)


@csrf_exempt
def response(request):
    print("####")
    resp = VerifyPaytmResponse(request)
    if resp['verified']:
        # save success details to db; details in resp['paytm']
        return HttpResponse("<center><h1>Transaction Successful</h1><center>", status=200)
    else:
        # check what happened; details in resp['paytm']
        return HttpResponse("<center><h1>Transaction Failed</h1><center>", status=400)
###########End Paytm###############

# Create your views here.

def index(request):
    return render(request,"car/index.html")

def home(request):
    return render(request,"car/index.html")

def login(request): 
    return render(request,"car/login.html")

def aboutus(request):
    return render(request,"car/about-us.html")

def contactus(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        msg = request.POST.get('msg')
        contacts = contact(name=name,email=email,msg=msg)
        contacts.save()
        return render(request,"car/contact-us.html")
    else:
        return render(request,"car/contact-us.html")
         
def trackorder(request):
    return render(request,"car/track-order.html")
#======================================================================#
#                  Customer Related Views                              #
#======================================================================#
def changepassword(request):
    return render(request,"car/change-password.html")

def forgotpassword(request):
    if request.method == 'POST':         
        try:
            useremail = request.POST.get('email')

            mail = customer.objects.get(email = useremail)
            num = "1234567890"
            otp = randint(0000,9999)
            # for i in range(4):
                # otp += num[math.floor(random.random() * 10)]
            request.session['email'] = mail.email
            request.session['otp'] = otp
            send_mail('Forgot Password(car care Center)', f'Customer otp is: {otp}', 'gohilbhavesh1997@gmail.com', [f'{useremail}'])
            return redirect('check_otp')   
        except:
            text = "Email is not Registered!"
            return render(request,'car/forgot_password.html',{'mail':text})
    else:   
        return render(request,'car/forgot_password.html')

def check_otp(request):
    if request.method == 'POST':
        otppass = int(request.POST.get('otppass'))
        if otppass==request.session.get('otp'):
            return redirect('forgotpasschange')  
        else:
            text = "you have entered wrong otp..!"
            return render(request,'car/otp_check.html',{'otp':text})
    else:   
        return render(request,"car/otp_check.html")

def forgotpasschange(request):
    if request.method == 'POST':
        newpass = request.POST.get('newpass')
        customer.objects.all().filter(email = request.session['email']).update(password=newpass)
        text = 'Your Password has Succesfully Change!'
        return redirect('customerlogin')
    else:
        return render(request,'car/forgot_password_change.html')

def customerbase(request):
    return render(request,"car/customerindex.html")

def customerregister(request):
    if request.method == 'POST' and request.FILES['image']:
        try:
            if customer.objects.get(email = request.POST['email']):
                mail = "Already Registered with this email!"
                return render(request,"car/customerregister.html",{"mail":mail})
        except:
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile_no')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            myfile = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            char = string.ascii_letters + string.digits
            password ="".join(choice(char)
            for x in range(randint(6,10)))
            reg = customer(fname = fname,lname=lname,email=email,mobile=mobile,gender=gender,address=address,password=password,image=myfile)
            reg.save()
            stu = customer.objects.all()
            text = "Your Password Will Be Sent Your Registered Mail id..!"
            send_mail('Registered Successfully car care Center', f'You Are registered Successfuly in Our System!\n Your Password is: {password}', 'gohilbhavesh1997@gmail.com', [f'{email}'])
            return render(request,"car/customerregister.html",{"text":text})
    else:
        return render(request,"car/customerregister.html")

def customerlogin(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user =  customer.objects.get(email=email,password=password)
            if user:   
                request.session['user'] = user.fname
                return redirect('customer_dashboard')
        except:
            email = "invalid Login Credintials"
            return render(request,"car/login.html",{"text":email})           
    else:   
        return render(request,"car/login.html")

def cust_change_pass(request):
    if request.method == 'POST':
        cust = customer.objects.get(fname = request.session['user'])
        current = request.POST.get('current')
        newpass = request.POST.get('newpass')
        password = request.session.get('password')
        print(current)
        print(newpass)
        try:
            customer.objects.get(password=current)
            customer.objects.all().filter(id=cust.id).update(password=newpass)
            text = "Your Password Successfully Change..."
            return render(request,'car/cust_change_password.html',{'text':text})
        except:
            change = "Current Password is not Match"
            return render(request,'car/cust_change_password.html',{'change':change})

    else:
        return render(request,'car/cust_change_password.html')

def customer_profile(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        # enqiry = cus_request.objects.all().filter(Customer_id = cust.id, status="Approved").order_by('date')
        cus= customer.objects.get(id=cust.id)
        return render(request,"car/customer_profile.html",{"user":cust,"stu":cus})
    else:
        return redirect('customerlogin')


def cust_edit_profile(request):
    if request.method == 'POST':
        if 'user' in request.session and request.FILES['image']:
            cust = customer.objects.get(fname = request.session['user'])
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            mobile = request.POST.get('mobile')
            myfile = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            enquiry = customer.objects.all().filter(id=cust.id).update(fname=fname,lname=lname,email=email,gender=gender,address=address,mobile=mobile,image=myfile)
            request.session['user']=fname
            return redirect('customer_profile')
        else:
            return redirect('customerlogin')
        
    else:
        if 'user' in request.session:
            cust = customer.objects.get(fname = request.session['user'])
            return render(request,'car/cust_profile_edit.html',{'user':cust})
        else:
            return redirect('customerlogin')



def customer_feedback(request):
    if request.method == 'POST':    
        if 'user' in request.session:
            cust = customer.objects.get(fname = request.session['user'])
            username = request.POST.get('username')
            email = request.POST.get('email')
            msg = request.POST.get('msg')
            feed = feedback(username=username,email=email,msg=msg)
            feed.save()
            text = 'Your Feedback Successfully Sent'
            return render(request,"car/feedback.html",{'user':cust,'text':text})
        else:
            return redirect('customerlogin')     

    else:
        if 'user' in request.session:
            cust = customer.objects.get(fname = request.session['user'])
            return render(request,"car/feedback.html",{'user':cust})
        else:
            return redirect('customerlogin')
   
from django.db.models import Q
def customer_dashboard(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        count_req = cus_request.objects.filter(Customer_id=cust.id).count()
        work_in_progress = cus_request.objects.all().filter(Customer_id = cust.id,status='Repairing').count()
        work_in_completed = cus_request.objects.all().filter(Customer_id = cust.id).filter(Q(status='Repairing Done') | Q(status = 'Released')).count
        bill = cus_request.objects.all().filter(Customer_id = cust.id).filter(Q(status='Repairing Done') | Q(status = 'Released')).aggregate(Sum('cost'))
        dict = {
            "user":cust,
            "count_req":count_req,
            'work_in_progress':work_in_progress,
            'work_in_completed':work_in_completed,
            'bill': bill['cost__sum']
        }
        return render(request,"car/customer_dashboard.html" ,context=dict)
    else:
        return redirect('customerlogin')
def invoice(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        enquiry = cus_request.objects.all().filter(Customer_id = cust.id).exclude(status = 'Pending')
        return render(request,"car/customer_invoice.html" ,{"user":cust,'enquiry':enquiry})
    else:
        return redirect('customerlogin')
def service(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        return render(request,"car/customer_request.html",{"user":cust})
    else:
        return render('customerlogin')
def customer_view_request(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        enqiry = cus_request.objects.all().filter(Customer_id = cust.id, status="Pending")
        return render(request, "car/customer_view_request.html",{"user":cust,"enquiry":enqiry})
    else:
        return render('customerlogin')

def customer_add_request(request):
    if request.method == 'POST':
        if 'user' in request.session:
            cust = customer.objects.get(fname=request.session['user'])
            category = request.POST.get('category')
            number = request.POST.get('number')
            name = request.POST.get('name')
            brand = request.POST.get('brand')
            model = request.POST.get('model')
            problem = request.POST.get('problem')
            cust = customer.objects.get(fname=request.session['user'])
            req = cus_request(category=category,number=number,name=name,brand=brand,model=model,problem=problem,Customer_id=cust.id)
            req.save()
            return render(request,"car/customer_add_request.html",{"user":cust})
        else:
            return redirect("customerlogin")
    else:
        if 'user' in request.session:
            cust = customer.objects.get(fname=request.session['user'])
            return render(request,"car/customer_add_request.html",{"user":cust})
        else:
            return redirect("customerlogin")

def customer_view_approved_request(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        enqiry = cus_request.objects.all().filter(Customer_id = cust.id, status="Approved")
        return render(request,"car/customer_view_approved_request.html",{"user":cust,"enquiry":enqiry})
    else:
        return render('customerlogin')
def customer_approved_request_bill(request):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        enqiry = cus_request.objects.all().filter(Customer_id = cust.id).exclude(status='Pending')
        return render(request,"car/customer_view_approved_request_bill.html",{"user":cust,"enquiry":enqiry})
    else:
        return render('customerlogin')

def del_customer_request(request,id):
    if 'user' in request.session:
        cust = customer.objects.get(fname = request.session['user'])
        enquiry = cus_request.objects.get(id = id)
        enquiry.delete()
        return redirect('customer_view_request')


def customer_logout(request):
    if 'user' in request.session:
        del request.session['user']
        return redirect('customerlogin')
    else:
        return render(request,"car/customer_dashboard.html") 




#======================================================#
#  Mechanic Views                                      #
#======================================================#

def mechaniclogin(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            mec =  mechanic.objects.get(email=email,password=password)
            if mec:   
                request.session['mec'] = mec.fname
                return redirect('mechanicindex')
        except:
            email = "invalid Login Credintials"
            return render(request,"car/mechaniclogin.html",{"text":email})           
    else:   
        return render(request,"car/mechaniclogin.html")

def mech_change_pass(request):
    if request.method == 'POST':
        user = mechanic.objects.get(fname = request.session['mec'])
        current = request.POST.get('current')
        newpass = request.POST.get('newpass')
        password = request.session.get('password')
        print(current)
        print(newpass)
        try:
            mechanic.objects.get(password=current)
            mechanic.objects.all().filter(id=user.id).update(password=newpass)
            text = "Your Password Successfully Change..."
            return render(request,'car/mech_change_pass.html',{'text':text,"mech":user})
        except:
            change = "Current Password is not Match"
            return render(request,'car/mech_change_pass.html',{'change':change})

    else:
        if 'mec' in request.session:
            user = mechanic.objects.get(fname = request.session['mec'])
            return render(request,'car/mech_change_pass.html',{'mech':user})
        else:
            return redirect('mechaniclogin')

def mechanic_profile(request):
    if 'mec' in request.session:
        user = mechanic.objects.get(fname = request.session['mec'])
        # enqiry = cus_request.objects.all().filter(Customer_id = cust.id, status="Approved").order_by('date')
        cus= mechanic.objects.get(id=user.id)
        return render(request,"car/mechanic_profile.html",{"mech":user,"stu":cus})
    else:
        return redirect('mechaniclogin')


def mech_edit_profile(request):
    if request.method == 'POST':
        if 'mec' in request.session and request.FILES['image']:
            user = mechanic.objects.get(fname = request.session['mec'])
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            mobile = request.POST.get('mobile')
            myfile = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            enquiry = mechanic.objects.all().filter(id=user.id).update(fname=fname,lname=lname,email=email,gender=gender,address=address,mobile=mobile,image=myfile)
            request.session['mec']=fname
            return redirect('mechanic_profile')
        else:
            return redirect('mechaniclogin')
        
    else:
        if 'mec' in request.session:
            user = mechanic.objects.get(fname = request.session['mec'])
            return render(request,'car/mech_edit_profile.html',{'mech':user})
        else:
            return redirect('mechaniclogin')

    
def mechanicindex(request):
    if 'mec' in request.session:
        user = mechanic.objects.get(fname = request.session['mec'])
        count_req = cus_request.objects.all().filter(Mechanic_id = user.id, status = 'Approved').count()
        work_progress =  cus_request.objects.all().filter(Mechanic_id = user.id, status = 'Repairing').count()
        work_complete = cus_request.objects.all().filter(Mechanic_id = user.id, status = 'Reoairing Done').count()
        Salary  = mechanic.objects.get(salary=user.salary)
        dict = {
            'mech':user,
            'count_req':count_req,
            'work_progress':work_progress,
            'work_complete':work_complete,
            'Salary':Salary
        }
        return render(request,"car/mechanicindex.html",context=dict)
    else:
        return redirect('mechaniclogin')


def mechanic_base(request):
        return render(request,"car/mechanicbase.html")
    
def mechanic_service(request):
    if 'mec' in request.session:
        user = mechanic.objects.get(fname = request.session['mec'])
        enquiry = cus_request.objects.all().filter(Mechanic_id = user.id)
        return render(request,"car/mechanicservice.html",{"mech":user,"work":enquiry})
    else:
        return redirect('mechaniclogin')

def mechanic_feedback(request):
    if request.method == 'POST':
        if 'mec' in request.session:
            user = mechanic.objects.get(fname = request.session['mec'])
            username = request.POST.get('username')
            email = request.POST.get('email')
            msg = request.POST.get('msg')
            feed = feedback(username=username,email=email,msg=msg)
            feed.save()
            return render(request,'car/mechanic_feedback.html',{"mech":user})
        else:
            return redirect('mechaniclogin')
    else:
        if  'mec' in request.session:
            user = mechanic.objects.get(fname = request.session['mec'])
            return render(request,"car/mechanic_feedback.html",{"mech":user})
        else:
            return redirect('mechaniclogin') 


def mechanic_update_status(request,id):
    if request.method == 'POST':
        if 'mec' in request.session:
            user = mechanic.objects.get(fname = request.session['mec'])
            status = request.POST.get('status')
            cus_request.objects.filter(Mechanic_id=user.id).update(status=status)
            return redirect('mechanic_service')
        else:
            return redirect('mechaniclogin')
    else:
        if 'mec' in request.session:
            user = mechanic.objects.get(fname = request.session['mec'])
            return render(request,'car/mechanic_update_status.html',{'mech':user})
        else:  
            return redirect('mechanic_service')
def mechanic_leave(request):
    if 'mec' in request.session:
        user = mechanic.objects.get(fname=request.session['mec'])
        return render(request,'car/mechanicleave.html',{'mech':user})
    else:
        return redirect('mechaniclogin')

def mechanic_leave_form(request):
    if request.method == 'POST':
        if 'mec' in request.session:
            user = mechanic.objects.get(fname=request.session['mec'])
            print("gfdgdfgdfgfd")
            reason = request.POST.get('reason')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date') 
            leave = apply_leave(reason=reason,from_date=from_date,to_date=to_date,Mechanic_id=user.id) 
            leave.save()
            print("gfdgdfgdfgfd")
            print(leave)
            return render(request,'car/mechanic_apply_leave.html',{"mech":user})
        else:
            return redirect('mechaniclogin')
    else:
        if 'mec' in request.session:
            user = mechanic.objects.get(fname=request.session['mec'])
            return render(request,'car/mechanic_apply_leave.html',{"mech":user})
        else:
            return redirect('mechaniclogin')

def leave_status(request):
    if 'mec' in request.session:
        user = mechanic.objects.get(fname=request.session['mec'])
        leave_stat = apply_leave.objects.filter(Mechanic_id=user.id) 
        return render(request,'car/leave_status.html',{'mech':user,'leave_stat':leave_stat})
    else:
        return redirect('mechaniclogin')

def mechanicforgotpass(request):
    if request.method == 'POST':         
        try:
            useremail = request.POST.get('email')

            mail = mechanic.objects.get(email = useremail)
            num = "1234567890"
            otp = randint(0000,9999)
            # for i in range(4):
                # otp += num[math.floor(random.random() * 10)]
            request.session['email'] = mail.email
            request.session['otp'] = otp
            send_mail('Forgot Password(car care Center)', f'Mechnic otp is: {otp}', 'gohilbhavesh1997@gmail.com', [f'{useremail}'])
            return redirect('mechanic_check_otp')   
        except:
            text = "Email is not Registered!"
            return render(request,'car/mechanicforgotpass.html',{'mail':text})
    else:   
        return render(request,'car/mechanicforgotpass.html')

def mechanic_check_otp(request):
    if request.method == 'POST':
        otppass = int(request.POST.get('otppass'))
        if otppass==request.session.get('otp'):
            return redirect('mechanicforgotpasschange')  
        else:
            text = "you have entered wrong otp..!"
            return render(request,'car/mechanic_check_otp.html',{'otp':text})
    else:   
        return render(request,"car/mechanic_check_otp.html")

def mechanicforgotpasschange(request):
    if request.method == 'POST':
        newpass = request.POST.get('newpass')
        mechanic.objects.all().filter(email = request.session['email']).update(password=newpass)
        text = 'Your Password has Succesfully Change!'
        return redirect('mechaniclogin')
    else:
        return render(request,'car/mechanic_forgot_pass_change.html')


def mechanic_logout(request):
    if 'mec' in request.session:
        del request.session['mec']
        return redirect('mechaniclogin')


#Export csv file

def export_csv(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Customer_Request.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"category"),
        smart_str(u"name"),
        smart_str(u"brand"),
        smart_str(u"model"),
        smart_str(u"problem"),
        smart_str(u"date"),
        smart_str(u"date"),
        smart_str(u"cost"),
        smart_str(u"status"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.category),
            smart_str(obj.number),
            smart_str(obj.name),
            smart_str(obj.brand),
            smart_str(obj.model),
            smart_str(obj.problem),
            smart_str(obj.date),
            smart_str(obj.cost),
            smart_str(obj.status),
        ])
export_csv.short_description = u"Export CSV"