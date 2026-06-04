
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import User , Profile , Employee, Company , Job, Application , Category, Question

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
# Create your views here.
from django.db.models import Q
from django.contrib import messages
import random
import string
# Create your views here.
from datetime import date, datetime


BASE_TEMPLATE_CONTEXT = {"base_template": "base.html"}


def index(request):
    return render(request, "index.html")


def index_2(request):
    return render(request, "index-2.html")


def about(request):
    return render(request, "about.html")


def add_resume(request):
    return render(request, "add-resume.html")


def base(request):
    return render(request, "base.html")


def blog(request):
    return render(request, "blog.html")


def blog_full_width(request):
    return render(request, "blog-full-width.html")


def blog_left_sidebar(request):
    return render(request, "blog-left-sidebar.html")


def bookmarked(request):
    return render(request, "bookmarked.html")


def browse_categories(request):
    return render(request, "browse-categories.html")


def browse_jobs(request):
    return render(request, "browse-jobs.html")


def browse_resumes(request):
    return render(request, "browse-resumes.html")


def change_password(request):
    return render(request, "change-password.html")


def contact(request):
    return render(request, "contact.html")


def faq(request):
    return render(request, "faq.html")


def job_alerts(request):
    return render(request, "job-alerts.html")


def job_details(request):
    return render(request, "job-details.html")


def job_page(request):
    return render(request, "job-page.html")


def manage_applications(request):
    return render(request, "manage-applications.html")


def manage_jobs(request):
    return render(request, "manage-jobs.html")


def manage_resumes(request):
    return render(request, "manage-resumes.html")


def notifications(request):
    return render(request, "notifications.html")


def post_job(request):
    return render(request, "post-job.html")


def pricing(request):
    return render(request, "pricing.html")


def privacy_policy(request):
    return render(request, "privacy-policy.html")


def resume(request):
    return render(request, "resume.html")


def single_post(request):
    return render(request, "single-post.html")


 


def register(request):
    if request.method == "POST":
        # username =   request.POST.get("username")
        fullname =   request.POST.get("fullname")
        email =      request.POST.get("email")
        mobileno =     request.POST.get("mobileno")
        dateofbirth =       request.POST.get("dateofbirth")
        # address =    request.POST.get("address")
        password =   request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')
 
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')
        
        if dateofbirth:
            dob = datetime.strptime(dateofbirth, "%Y-%m-%d").date()
            today = date.today()

            age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )

            if age < 18:
                messages.error(request, "You must be at least 18 years old to register.")
                return redirect('register')
            

        User.objects.create(
            
            fullname =fullname,
            email =   email,
            mobileno = mobileno, 
            dateofbirth =     dateofbirth,
            # address = address,
            password= make_password(password)
        )
        print("student data added successfully")
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')
    return render(request, "register.html", BASE_TEMPLATE_CONTEXT)

    
def login(request):
    if request.method == "POST":
        form_email     =   request.POST.get("email")
        password  = request.POST.get("password")
        print(form_email)
        try:
            # user =  get_object_or_404(User, email=form_email)
            user =  User.objects.get(email = form_email )

            if user:
             
                if check_password(password, user.password) or password == user.password:
                
                    request.session["fullname"] =user.fullname
                    request.session["email"] = user.email
                    return redirect('index')
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
                messages.error(request, "Invalid email or password")
                return redirect('login')
            return redirect('register')
          
    return render(request, "login.html", BASE_TEMPLATE_CONTEXT)


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

    return render(request, "index.html", context)

def  employee_profile(request):
    if not request.session.get('email'):
        return redirect('login')
    
    session_email = request.session.get('email')

    if not session_email:
        return redirect('login')
    try:

        curr_employee = Employee.objects.get(email = session_email)

        if request.method == "POST":
            username =  request.POST.get("username")
            avatar =    request.FILES.get("avatar") 
            resume =    request.FILES.get("resume")

            Profile.objects.create(
                username = username,
                profile_pic =  avatar,
                resume =  resume
        )

        employee= Profile.objects.all()
        context = {
            "employee_data":employee
    }
    except:
        return redirect('login')

    return render(request, "employeeprofile.html", context)

 



# def reset_password(request):
#     if request.method=="POST":
#         email = request.POST.get('email')
#         try:
#             student = Student.objects.get(email = email)

#             characters = string.ascii_letters+string.digits
#             new_password=""
#             for i in range(1,9):
#                 new_password += "".join(random.choices(characters))

#             student.password = make_password(new_password)
#             student.save()
#             send_mail(
#                 'New Password',
#                 f'Your new password is {new_password}',
#                 'rohitbali008@gmail.com',
#                 [email]
#             )
#         except:
#             print("invalid mail")
        
#     return redirect('login')





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

            Job.objects.create(
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
        
    return render(request, "dashboard.html")



    
def logout(request):
    request.session.flush()
    return redirect('login')


def cards(request):

    vacancies = Job.objects.all()
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
        

        curr_job = Job.objects.get(id = id)

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
        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    else:
        jobs = Job.objects.all()
    return render(request, 'cards.html', {'cards': cards})
def side(request):
    return render(request,'base2.html')
def courses(request):
    companies=Company.objects,all()
    if request.method == "POST":
        name=  request.POST.get("name")
        company=request.POST.get("company")
        Category.objects.create(
            name=name,
            company=company,
        )
    job= Category.objects.all()
    context = {
        "job_data":job
    }
    return render(request,"",{"companies":companies},context)


    
def test(request):
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
        employees=Employee.objects.all()
        categories=Category.objects.all()
        if request.method=="POST":
            print(curr_employee)
            job_profile=Category.objects.get(id =request.POST.get("job") )
            questions=request.POST.get("questions")
            opt_a=request.POST.get("opt_a")
            opt_b=request.POST.get("opt_b")
            opt_c=request.POST.get("opt_c")
            opt_d=request.POST.get("opt_d")
            answer=request.POST.get("answer")
            marks=request.POST.get("marks")
            

            Question.objects.create(
                job_profile=job_profile,
                questions=questions,
                opt_a=opt_a,
                opt_b=opt_b,
                opt_c=opt_c,
                opt_d=opt_d,
                answer=answer,
                marks=marks,
                added_by=curr_employee,
        )
    except:
        return redirect('login')
    jobs = Category.objects.all()
    return render(request,"questions.html",{"employees":employees,"categories":categories, "job_data":jobs})


