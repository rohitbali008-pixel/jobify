
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import User , Profile , Employee, Company , Job, Application , Category, Question, Test, TestAssignment

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
DESIGNATION_CHOICES = Employee._meta.get_field("designation").choices
ROLE_CHOICES = Employee._meta.get_field("role").choices
APPLICATION_STATUS_CHOICES = Application._meta.get_field("status").choices


def get_current_employee(request):
    session_email = request.session.get("email")
    if not session_email:
        return None
    try:
        return Employee.objects.get(email=session_email)
    except Employee.DoesNotExist:
        return None


def dashboard_context(current_employee, **kwargs):
    context = {"current_employee": current_employee}
    context.update(kwargs)
    context["session_fullname"] = current_employee.fullname if current_employee else ""
    context["session_email"] = current_employee.email if current_employee else ""
    context["is_authenticated"] = True
    return context


def index(request):
    categories = Category.objects.select_related("company").order_by("name")[:8]
    featured_jobs = Job.objects.select_related("created_by__company").order_by("-id")[:6]
    latest_jobs = Job.objects.select_related("created_by__company").order_by("-id")[:6]
    context = {
        "categories": categories,
        "featured_jobs": featured_jobs,
        "latest_jobs": latest_jobs,
        "base_template": "base.html",
    }
    return render(request, "index.html", context)


def dashboard(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')
    return render(request, "dashboard.html", dashboard_context(curr_employee))


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
    return render(request, "bookmarked.html", {"active_page": "bookmarked"})


def browse_categories(request):
    return render(request, "browse-categories.html")


def browse_jobs(request):
    return render(request, "browse-jobs.html")


def browse_resumes(request):
    return render(request, "browse-resumes.html")


def change_password(request):
    curr_employee = get_current_employee(request)
    if curr_employee:
        if request.method == "POST":
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not (check_password(current_password, curr_employee.password) or current_password == curr_employee.password):
                messages.error(request, "Current password is incorrect")
                return redirect('change_password')

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect('change_password')

            curr_employee.password = make_password(new_password)
            curr_employee.save()
            messages.success(request, "Password changed successfully")
            return redirect('change_password')

        return render(request, "change-password.html", {"user_type": "employee", "active_page": "change_password"})

    session_email = request.session.get("email")
    user = None
    if session_email:
        try:
            user = User.objects.get(email=session_email)
        except User.DoesNotExist: 
            user = None

    if not user:
        return redirect('login')

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not (check_password(current_password, user.password) or current_password == user.password):
            messages.error(request, "Current password is incorrect")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect('change_password')

        user.password = make_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully")
        return redirect('change_password')

    return render(request, "change-password.html", {"user_type": "user", "active_page": "change_password"})


def contact(request):
    return render(request, "contact.html")


def faq(request):
    return render(request, "faq.html")


def job_alerts(request):
    return render(request, "job-alerts.html", {"active_page": "job_alerts"})


def job_details(request, id):
    job = get_object_or_404(Job, id=id)
    skills_list = [skill.strip() for skill in job.skills.split(',') if skill.strip()]
    experience_choices = Profile._meta.get_field("experience").choices
    similar_jobs = Job.objects.exclude(id=job.id).order_by("-id")[:4]
    context = {
        "job": job,
        "skills_list": skills_list,
        "experience_choices": experience_choices,
        "similar_jobs": similar_jobs,
    }
    return render(request, "job-details.html", context)


def job_page(request):
    return render(request, "job-page.html")


def manage_applications(request):
    return render(request, "manage-applications.html", {"active_page": "manage_applications"})


def manage_jobs(request):
    return render(request, "manage-jobs.html", {"active_page": "manage_jobs"})


def manage_resumes(request):
    return render(request, "manage-resumes.html", {"active_page": "manage_resumes"})


def notifications(request):
    return render(request, "notifications.html", {"active_page": "notifications"})


def post_job(request):
    return render(request, "post-job.html")


def pricing(request):
    return render(request, "pricing.html")


def privacy_policy(request):
    return render(request, "privacy-policy.html")


def resume(request):
    return render(request, "resume.html", {"active_page": "resume"})


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

                if check_password(password, employee.password) or password == employee.password:

                    request.session["fullname"] = employee.fullname
                    request.session["email"] = employee.email
                    print("Login Successfully.")
                    messages.success(request,"Login Successfully.")
                    return redirect('dashboard')
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
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "password":
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not (check_password(current_password, curr_employee.password) or current_password == curr_employee.password):
                messages.error(request, "Current password is incorrect")
                return redirect('employee_profile')

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect('employee_profile')

            curr_employee.password = make_password(new_password)
            curr_employee.save()
            messages.success(request, "Password changed successfully")
            return redirect('employee_profile')

        email = request.POST.get("email")
        if email != curr_employee.email and Employee.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('employee_profile')

        curr_employee.fullname = request.POST.get("fullname")
        curr_employee.email = email
        curr_employee.phone = request.POST.get("phone")

        profile_pic = request.FILES.get("profile_pic")
        if profile_pic:
            curr_employee.profile_pic = profile_pic

        curr_employee.save()
        request.session["fullname"] = curr_employee.fullname
        request.session["email"] = curr_employee.email
        messages.success(request, "Profile updated successfully")
        return redirect('employee_profile')

    context = {
        "employee": curr_employee,
    }
    return render(request, "employee_profile.html", dashboard_context(curr_employee, **context))

 

 




def view_employees(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    employees = Employee.objects.filter(company=curr_employee.company).order_by("-id")
    return render(request, "view_employees.html", dashboard_context(curr_employee, employees=employees))


def update_employee(request, employee_id):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    employee = get_object_or_404(Employee, id=employee_id, company=curr_employee.company)

    if request.method == "POST":
        employee.fullname = request.POST.get("fullname")
        employee.email = request.POST.get("email")
        employee.phone = request.POST.get("phone")
        employee.designation = request.POST.get("designation")
        employee.role = request.POST.get("role")
        employee.sallary = request.POST.get("sallary")
        employee.joiningdate = request.POST.get("joiningdate")

        profile_pic = request.FILES.get("profile_pic")
        if profile_pic:
            employee.profile_pic = profile_pic

        employee.save()
        messages.success(request, "Employee updated successfully")
        return redirect('view_employees')

    context = {
        "employee": employee,
        "designation_choices": DESIGNATION_CHOICES,
        "role_choices": ROLE_CHOICES,
    }
    return render(request, "update_employee.html", dashboard_context(curr_employee, **context))



def add_employee(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    if request.method == "POST":
        designation =   request.POST.get("designation")
        fullname =   request.POST.get("fullname")
        email =      request.POST.get("email")
        phone =      request.POST.get("phone")
        role =      request.POST.get("role")
        sallary =     request.POST.get("sallary")
        joiningdate =  request.POST.get("dateofjoining")
        password =   request.POST.get("password")

        if Employee.objects.filter(email=email).exists():
            messages.error(request, "Employee email already exists")
            return redirect('add_employee')

        Employee.objects.create(
            
            fullname =fullname,
            email =   email,
            phone =   phone,
            joiningdate= joiningdate,
            company = curr_employee.company,
            password= make_password(password),
            designation= designation,
            role= role or "Employee",
            sallary= sallary
        )
        messages.success(request, "Employee added successfully")
        return redirect('add_employee')

    return render(request, "add_employee.html", dashboard_context(
        curr_employee,
        company=curr_employee.company,
        designation_choices=DESIGNATION_CHOICES,
        role_choices=ROLE_CHOICES,
    ))





def vacancy(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    if request.method == "POST":
        Job.objects.create(
            title=request.POST.get("title"),
            experience=request.POST.get("experience"),
            discription=request.POST.get("discription"),
            skills=request.POST.get("skills"),
            qualification=request.POST.get("qualification"),
            minsalary=request.POST.get("minsalary"),
            maxsalary=request.POST.get("maxsalary"),
            created_by=curr_employee,
            deadline=request.POST.get("deadline"),
            vacancies=request.POST.get("vacancies"),
            location=request.POST.get("location"),
        )
        messages.success(request, "Vacancy created successfully")
        return redirect('vacancy')

    jobs = Job.objects.filter(created_by=curr_employee).order_by("-id")
    return render(request, "vacancy.html", dashboard_context(curr_employee, jobs=jobs))


def view_applications(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    if request.method == "POST":
        if request.POST.get("auto_shortlist"):
            from .utils import generate_job_scores
            applications = Application.objects.select_related("job_id", "user_id").filter(
                job_id__created_by=curr_employee
            )
            for job in Job.objects.filter(created_by=curr_employee):
                generate_job_scores(job)
            messages.success(request, "ATS scoring and auto-shortlisting completed")
            return redirect('view_applications')

        application = get_object_or_404(Application, id=request.POST.get("application_id"))
        application.status = request.POST.get("status")
        application.save()
        messages.success(request, "Application status updated")
        return redirect('view_applications')

    applications = Application.objects.select_related("job_id", "user_id").filter(
        job_id__created_by=curr_employee
    ).order_by("-applied_on", "-id")
    return render(request, "view_applications.html", dashboard_context(
        curr_employee,
        applications=applications,
        status_choices=APPLICATION_STATUS_CHOICES,
    ))


def shortlisted_list(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    applications = Application.objects.select_related("job_id", "user_id").filter(
        job_id__created_by=curr_employee,
        status="Shortlisted",
    ).order_by("-applied_on", "-id")
    return render(request, "shortlisted_list.html", dashboard_context(curr_employee, applications=applications))


def scheduled_interview(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    applications = Application.objects.select_related("job_id", "user_id").filter(
        job_id__created_by=curr_employee,
        status="Shortlisted",
    ).order_by("-applied_on", "-id")

    if request.method == "POST":
        application = get_object_or_404(applications, id=request.POST.get("application_id"))
        interview_date = request.POST.get("interview_date")
        interview_time = request.POST.get("interview_time")
        meeting_place = request.POST.get("meeting_place")
        applicant_name = application.user_id.fullname if application.user_id else "Unknown applicant"
        messages.success(
            request,
            f"Interview scheduled for {applicant_name} on {interview_date} at {interview_time}. Venue: {meeting_place}",
        )
        return redirect('scheduled_interview')

    return render(request, "scheduled_interview.html", dashboard_context(curr_employee, applications=applications))


def create_test(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    companies = Company.objects.all()
    if request.method == "POST":
        company = get_object_or_404(Company, id=request.POST.get("company_id"))
        Category.objects.create(
            name=request.POST.get("name"),
            company=company,
        )
        messages.success(request, "Test created successfully")
        return redirect('create_test')

    categories = Category.objects.select_related("company").order_by("-id")
    return render(request, "create_test.html", dashboard_context(
        curr_employee,
        companies=companies,
        categories=categories,
    ))


def add_question(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    categories = Category.objects.all().order_by("name")
    if request.method == "POST":
        job_profile = get_object_or_404(Category, id=request.POST.get("job"))
        Question.objects.create(
            job_profile=job_profile,
            questions=request.POST.get("questions"),
            opt_a=request.POST.get("opt_a"),
            opt_b=request.POST.get("opt_b"),
            opt_c=request.POST.get("opt_c"),
            opt_d=request.POST.get("opt_d"),
            answer=request.POST.get("answer"),
            marks=request.POST.get("marks"),
            added_by=curr_employee,
        )
        messages.success(request, "Question added successfully")
        return redirect('add_question')

    questions = Question.objects.select_related("job_profile").order_by("-id")
    return render(request, "add_question.html", dashboard_context(
        curr_employee,
        categories=categories,
        questions=questions,
    ))


def add_test_question(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    jobs = Job.objects.filter(created_by__company=curr_employee.company).order_by("-id")
    questions = Question.objects.select_related("job_profile").order_by("-id")

    if request.method == "POST":
        title = request.POST.get("title")
        vacancy = get_object_or_404(Job, id=request.POST.get("vacancy"))
        duration_minutes = int(request.POST.get("duration_minutes", 0))
        passing_marks = int(request.POST.get("passing_marks", 0))
        question_ids = request.POST.getlist("question_ids")

        total_marks = 0
        selected_questions = []
        for qid in question_ids:
            try:
                q = Question.objects.get(id=qid)
                selected_questions.append(q)
                total_marks += q.marks
            except Question.DoesNotExist:
                pass

        test = Test.objects.create(
            title=title,
            vacancy=vacancy,
            duration_minutes=duration_minutes,
            total_marks=total_marks,
            passing_marks=passing_marks,
            created_by=curr_employee,
        )
        test.questions.set(selected_questions)
        messages.success(request, "Test created successfully")
        return redirect('add_test_question')

    tests = Test.objects.select_related("vacancy", "created_by").all().order_by("-id")
    return render(request, "add_test_question.html", dashboard_context(
        curr_employee,
        jobs=jobs,
        questions=questions,
        tests=tests,
    ))


def allot_test(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    tests = Test.objects.select_related("vacancy").order_by("-id")
    applications = Application.objects.select_related("job_id", "user_id").filter(
        job_id__created_by=curr_employee,
        status="Shortlisted",
    ).order_by("-applied_on", "-id")

    if request.method == "POST":
        test = get_object_or_404(Test, id=request.POST.get("test_id"))
        application = get_object_or_404(applications, id=request.POST.get("application_id"))
        TestAssignment.objects.create(
            application=application,
            test=test,
        )
        messages.success(request, "Test alloted successfully")
        return redirect('allot_test')

    assignments = TestAssignment.objects.select_related("application__user_id", "test").filter(
        application__job_id__created_by=curr_employee
    ).order_by("-assigned_on", "-id")
    return render(request, "allot_test.html", dashboard_context(
        curr_employee,
        tests=tests,
        applications=applications,
        assignments=assignments,
    ))



    
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
            apply_date =  request.POST.get("apply_date")
            job_id =   curr_job
            status =   request.POST.get("status")
            user_id = curr_user

            print()
            Application.objects.create(
                resume =resume,
                skills=   ", ".join(request.POST.getlist("skills")),
                experience= experience,
                apply_date= request.POST.get("apply_date") or datetime.now(),
                status= status or "Under Review",
                job_id=job_id,
                user_id=user_id,
            )
        messages.success(request, "Application submitted successfully")
        return redirect('job_details', id=curr_job.id)
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
    return add_question(request)


