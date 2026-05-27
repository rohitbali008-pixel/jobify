
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import User , Profile , Employee, Company , Jobs, Application

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
# Create your views here.
from django.db.models import Q
from django.contrib import messages
import random
import string
# Create your views here.
def create_jobs(request):
    if request.method == "POST":
        # username =   request.POST.get("username")
        fullname =   request.POST.get("fullname")
        email =      request.POST.get("email")
        mobileno =     request.POST.get("mobileno")
        dateofbirth =        request.POST.get("dateofbirth")
        address =    request.POST.get("address")
        password=   request.POST.get("password")
 
        User.objects.create(
            
            fullname =fullname,
            
            email =   email,
            mobileno= mobileno, 
            dateofbirth =     dateofbirth,
            address = address,
            password =password
        )
        print("student data added successfully")

    return render(request, "createjobs.html")
def register(request):
    if request.method == "POST":
        # username =   request.POST.get("username")
        fullname =   request.POST.get("fullname")
        email =      request.POST.get("email")
        mobileno =     request.POST.get("mobileno")
        dateofbirth =       request.POST.get("dateofbirth")
        address =    request.POST.get("address")
        password =   request.POST.get("password")
 
        User.objects.create(
            
            fullname =fullname,
            email =   email,
            mobileno = mobileno, 
            dateofbirth =     dateofbirth,
            address = address,
            password= make_password(password)
        )
        print("student data added successfully")
        return redirect('login')
    return render(request, "register.html")
def login(request):
    if request.method == "POST":
        form_email     =   request.POST.get("email")
        password  = request.POST.get("password")
        print(form_email)
        try:
            # user =  get_object_or_404(User, email=form_email)
            user =  User.objects.get(email = form_email )

            if user:
             
                if password == user.password:
                
                    request.session["fullname"] =user.fullname
                    request.session["email"] = user.email
                    return redirect('user_profile')
                else:
                    messages.error(request, "Invalid Password")
                    return redirect('login')
       

        except User.DoesNotExist:
            print("user not found")
            try:
                employee = Employee.objects.get(email = form_email )

                if password == employee.password:

                    request.session["fullname"] = employee.fullname
                    request.session["email"] = employee.email
                    return redirect('vacancy')
            except:

                print("employee not found")
                return redirect('login')
            return redirect('register')
          
      


        
    return render(request, "login.html")


def  user_profile(request):

    if request.method == "POST":
        username =  request.POST.get("username")
        avatar =    request.FILES.get("avatar") 
        resume =    request.FILES.get("resume")

        Profile.objects.create(
            username = username,
            profile_pic =  avatar,
            resume =  resume
        )

    user= Profile.objects.all()
    context = {
        "user_data":user
    }

    return render(request, "userprofile.html", context)

def show_user(request):
    users =  User.objects.all()

    context = {
        "user_data":users
    }
    return render(request, "show_user.html", context)
# def reset_password(request):
#     if request.method=="POST":
#         email = request.POST.get('email')
        # try:
        #     student = Student.objects.get(email = email)

        #     characters = string.ascii_letters+string.digits
        #     new_password=""
        #     for i in range(1,9):
        #         new_password += "".join(random.choices(characters))

        #     student.password = make_password(new_password)
        #     student.save()
        #     send_mail(
        #         'New Password',
        #         f'Your new password is {new_password}',
        #         'rohitbali008@gmail.com',
        #         [email]
        #     )
        # except:
        #     print("invalid mail")
            
    return redirect('login')
def add_employee(request):
    companies = Company.objects.all()
    if request.method == "POST":
        designation =   request.POST.get("designation")
        fullname =   request.POST.get("fullname")
        email =      request.POST.get("email")
        sallary =     request.POST.get("sallary")
        joiningdate =  request.POST.get("dateofjoining")
        company_id =    request.POST.get("company_id")
        password =   request.POST.get("password")
        company = Company.objects.get(id = company_id)
        Employee.objects.create(
            
            fullname =fullname,
            email =   email,
            joiningdate= joiningdate,
            company = company,
            password= password,
            designation= designation,
            sallary= sallary
        )
        print("student data added successfully")
        return redirect('login')
    return render(request, "add_employee.html", {"companies":companies})
def vacancy(request):
    
    if not request.session.get('email'):
        return redirect('login')
    
    session_email = request.session.get('email')

    if not session_email:
        return redirect('login')
    try:

        curr_employee = Employee.objects.get(email = session_email)
        
        print(curr_employee)
        if not curr_employee:
            return redirect('login')
        

        if request.method == "POST":
            print(curr_employee)
            title=   request.POST.get("title")
            experience =   request.POST.get("experience")
            discription =      request.POST.get("discription")
            
            education =  request.POST.get("education")
            skills= request.POST.get("skills")
            minsalary =    request.POST.get("minsalary")
            maxsalary =   request.POST.get("maxsalary")
        
            deadline=   request.POST.get("deadline")
            vacancies =   request.POST.get("vacancies")
            location  = request.POST.get("location")

            Jobs.objects.create(
                title=title,
                experience=experience,
                discription=discription,
                
                skills = skills ,
                education=education,
                minsalary=minsalary,
                maxsalary=maxsalary,
                created_by=curr_employee,

                deadline=deadline,
                vacancies=vacancies,
                location=location,

            )
    except:
        return redirect('login')
        
    return render(request, "vacancy.html")
    
def logout(request):
    request.session.flush()
    return redirect('login')

def cards(request):

    vacancies = Jobs.objects.all()
    return render(request ,"cards.html", {"vacancies":vacancies})


def eligibility(request, id):
    if not request.session.get('email'):
        return redirect('login')
    
    session_email = request.session.get('email')

    if not session_email:
        return redirect('login')
    try:

        curr_user = User.objects.get(email = session_email)
        
        if not curr_user:
            return redirect('login')
        

        curr_job = Jobs.objects.get(id = id)

        print(curr_user)
        print(curr_job)
        if request.method == "POST":
            print(curr_user)
            print(curr_job)

            resume =   request.FILES.get("resume")
            skills=   request.POST.get("skills")
            experience =      request.POST.get("experience")
            current_salary =     request.POST.get("current_salary")
            apply_date =  request.POST.get("apply_date")
            job_id =   curr_job
            status =   request.POST.get("status")
            user_id = curr_user
            education=request.POST.get("education")

            print()
            Application.objects.create(
            
            
                resume =resume,
                skills=   skills,
                experience= experience,
                current_salary= current_salary,
                apply_date= apply_date,
                education=education,
                status= status,
                job_id=job_id,
                user_id=user_id,
                )
    except Exception as e:
        print(e)
        return redirect('login')
    return render(request,"eligibility.html")


def card_list(request):
    query = request.GET.get('q')
    if query:
        jobs = Jobs.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    else:
        jobs = Jobs.objects.all()
    return render(request, 'cards.html', {'cards': cards})
def side(request):
    return render(request,'base2.html')