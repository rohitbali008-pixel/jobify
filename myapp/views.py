
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.urls import reverse
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from .models import User , Profile , Employee, Company , Job, Application , Category, Question, Test, TestAssignment, Interview

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
# Create your views here.
from django.db.models import Prefetch, Q
from django.contrib import messages
import random
import string
# Create your views here.
from datetime import date, datetime, timedelta


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


def get_current_candidate(request):
    session_email = request.session.get("email")
    if not session_email:
        return None
    try:
        return User.objects.get(email=session_email)
    except User.DoesNotExist:
        return None


def normalize_test_answer(value):
    answer = str(value or "").strip().upper().replace(" ", "").replace(".", "")
    answer = answer.replace("(", "").replace(")", "")
    if answer.startswith("OPTION"):
        answer = answer[6:]
    return answer


def is_assignment_expired(assignment):
    return timezone.now() > assignment.assigned_on + timedelta(minutes=assignment.test.duration_minutes)


def mark_expired_assignments(assignments):
    for assignment in assignments:
        if assignment.status == "Pending" and is_assignment_expired(assignment):
            assignment.status = "Expired"
            assignment.completed_on = timezone.now()
            assignment.save(update_fields=["status", "completed_on"])


def send_test_assignment_email(request, assignment):
    candidate = assignment.application.user_id
    job = assignment.application.job_id
    test = assignment.test
    test_url = request.build_absolute_uri(reverse("take_test_detail", args=[assignment.id]))
    company_name = "our company"
    if test.created_by and test.created_by.company:
        company_name = test.created_by.company.name

    subject = f"Test Allotted - {test.title}"
    message = (
        f"Hello {candidate.fullname},\n\n"
        f"Congratulations! You have been shortlisted for the {job.title} position at {company_name}.\n\n"
        f"A test has been allotted to you.\n"
        f"Test: {test.title}\n"
        f"Duration: {test.duration_minutes} minutes\n"
        f"Total Marks: {test.total_marks}\n"
        f"Passing Marks: {test.passing_marks}\n\n"
        f"Login to Interview IQ and click the Take Test link in the navbar, or open this URL:\n"
        f"{test_url}"
    )

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [candidate.email],
            fail_silently=False,
        )
    except Exception as exc:
        messages.warning(request, f"Test allotted successfully, but email could not be sent: {exc}")
    else:
        messages.success(request, "Test allotted successfully and email sent to candidate")


def send_interview_emails(request, interview, interviewer):
    candidate = interview.application.user_id
    job = interview.application.job_id
    company_name = interviewer.company.name if interviewer and interviewer.company else "our company"
    scheduled_at = timezone.localtime(interview.scheduled_at).strftime("%d %b %Y, %I:%M %p")
    candidate_subject = f"Interview Scheduled - {job.title}"
    interviewer_subject = f"New Interview Assigned - {candidate.fullname if candidate else 'Candidate'}"

    candidate_message = (
        f"Hello {candidate.fullname if candidate else 'Candidate'},\n\n"
        f"Your interview has been scheduled for the {job.title} position at {company_name}.\n\n"
        f"Interview Type: {interview.interview_type}\n"
        f"Scheduled At: {scheduled_at}\n"
        # f"Interviewer: {interviewer.fullname if interviewer else 'Not assigned'}\n"
        f"Meeting Link: {interview.meeting_link or 'Not provided'}\n\n"
        f"Please join the meeting on time. If you have any questions, contact the HR team."
    )

    interviewer_message = (
        f"Hello {interviewer.fullname if interviewer else 'Interviewer'},\n\n"
        f"A new interview has been assigned to you for {company_name}.\n\n"
        # f"Candidate: {candidate.fullname if candidate else 'Unknown candidate'}\n"
        f"Job: {job.title}\n"
        f"Interview Type: {interview.interview_type}\n"
        f"Scheduled At: {scheduled_at}\n"
        f"Meeting Link: {interview.meeting_link or 'Not provided'}\n\n"
        f"Please review the candidate profile before the interview."
    )

    email_errors = []
    if candidate and candidate.email:
        try:
            send_mail(candidate_subject, candidate_message, settings.EMAIL_HOST_USER, [candidate.email], fail_silently=False)
        except Exception as exc:
            email_errors.append(f"candidate email: {exc}")

    if interviewer and interviewer.email:
        try:
            send_mail(interviewer_subject, interviewer_message, settings.EMAIL_HOST_USER, [interviewer.email], fail_silently=False)
        except Exception as exc:
            email_errors.append(f"interviewer email: {exc}")

    if email_errors:
        messages.warning(request, f"Interview scheduled, but email notification failed: {'; '.join(email_errors)}")
    else:
        messages.success(request, "Interview scheduled and notification emails sent")


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
    query = request.GET.get('q', '')
    location_filter = request.GET.get('location', '')
    category_filter = request.GET.get('category', '')

    jobs = Job.objects.select_related("created_by__company").order_by("-id")

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(created_by__company__name__icontains=query) |
            Q(skills__icontains=query)
        )
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
    if category_filter:
        jobs = jobs.filter(skills__icontains=category_filter)

    all_locations = list(Job.objects.values_list('location', flat=True).distinct().order_by('location'))
    all_skills = set()
    for job in Job.objects.all():
        for skill in job.skills.split(','):
            skill = skill.strip()
            if skill:
                all_skills.add(skill)
    all_skills = sorted(all_skills)

    job_list = list(jobs)
    for job in job_list:
        job.skills_list = [skill.strip() for skill in job.skills.split(',') if skill.strip()]
        try:
            job.experience_display = Profile._meta.get_field("experience").choices[int(job.experience)][1]
        except (IndexError, ValueError):
            job.experience_display = f"{job.experience}+"

    context = {
        "jobs": job_list,
        "query": query,
        "location": location_filter,
        "category": category_filter,
        "location_list": all_locations,
        "all_skills": all_skills,
    }
    return render(request, "job-page.html", context)


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
    curr_user = get_current_candidate(request)
    if not curr_user:
        return redirect('login')

    if request.method == "POST":
        fullname = request.POST.get("fullname", "").strip()
        email = request.POST.get("email", "").strip()
        mobileno = request.POST.get("mobileno", "").strip()
        dateofbirth = request.POST.get("dateofbirth", "").strip()
        address = request.POST.get("address", "").strip()
        gender = request.POST.get("gender", "male")
        experience = request.POST.get("experience", "")
        education = request.POST.get("education", "").strip()

        if not fullname or not email or not mobileno or not dateofbirth or not address:
            messages.error(request, "Please fill all required fields")
            return redirect('resume')

        if User.objects.exclude(pk=curr_user.pk).filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('resume')

        try:
            mobileno = int(mobileno)
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid mobile number")
            return redirect('resume')

        try:
            dateofbirth = datetime.strptime(dateofbirth, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid date of birth")
            return redirect('resume')

        experience_choices = dict(Profile._meta.get_field("experience").choices)
        if experience not in experience_choices:
            messages.error(request, "Please select a valid experience")
            return redirect('resume')

        if gender not in ["male", "female", "other"]:
            gender = "male"

        with transaction.atomic():
            curr_user.fullname = fullname
            curr_user.email = email
            curr_user.mobileno = mobileno
            curr_user.dateofbirth = dateofbirth
            curr_user.address = address
            curr_user.save()

            profile, _ = Profile.objects.get_or_create(user=curr_user)
            profile.profile_pic = request.FILES.get("profile_pic") or profile.profile_pic
            profile.resume = request.FILES.get("resume") or profile.resume
            profile.gender = gender
            profile.experience = experience
            profile.education = education
            profile.save()

        request.session["fullname"] = curr_user.fullname
        request.session["email"] = curr_user.email
        messages.success(request, "Profile updated successfully")
        return redirect('resume')

    profile, _ = Profile.objects.get_or_create(user=curr_user)
    return render(request, "resume.html", {
        "active_page": "my_profile",
        "user_profile": curr_user,
        "profile": profile,
        "experience_choices": Profile._meta.get_field("experience").choices,
    })



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
        status__in=["Shortlisted", "Interviewed"],
    ).order_by("-applied_on", "-id")

    completed_assignments = TestAssignment.objects.select_related(
        "application__user_id",
        "application__job_id",
        "test",
        "test__vacancy",
    ).filter(
        application__in=applications,
        status="Completed",
    ).order_by("-completed_on", "-id")

    applications = applications.prefetch_related(Prefetch(
        "testassignment_set",
        queryset=completed_assignments,
        to_attr="completed_assignments",
    ))

    shortlisted_applications = [
        application for application in applications
        if application.status == "Shortlisted"
    ]
    interviewed_applications = [
        application for application in applications
        if application.status == "Interviewed"
    ]

    return render(request, "shortlisted_list.html", dashboard_context(
        curr_employee,
        shortlisted_applications=shortlisted_applications,
        interviewed_applications=interviewed_applications,
    ))


def scheduled_interview(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    applications = Application.objects.select_related("job_id", "user_id").filter(
        job_id__created_by=curr_employee,
        status="Interviewed",
    ).order_by("-applied_on", "-id")

    interviewers = Employee.objects.filter(company=curr_employee.company).order_by("fullname")
    interview_type_choices = Interview._meta.get_field("interview_type").choices

    if request.method == "POST":
        application = get_object_or_404(applications, id=request.POST.get("application_id"))
        interviewer = get_object_or_404(interviewers, id=request.POST.get("interviewer_id"))
        interview_type = request.POST.get("interview_type") or "Technical"
        interview_date = request.POST.get("interview_date")
        interview_time = request.POST.get("interview_time")
        meeting_link = request.POST.get("meeting_link", "").strip()

        if interview_type not in dict(interview_type_choices):
            messages.error(request, "Please select a valid interview type")
            return redirect('scheduled_interview')

        try:
            interview_date_obj = datetime.strptime(interview_date, "%Y-%m-%d").date()
            interview_time_obj = datetime.strptime(interview_time, "%H:%M").time()
            scheduled_at = timezone.make_aware(
                datetime.combine(interview_date_obj, interview_time_obj),
                timezone.get_current_timezone(),
            )
        except (TypeError, ValueError):
            messages.error(request, "Please provide a valid interview date and time")
            return redirect('scheduled_interview')

        if scheduled_at <= timezone.now():
            messages.error(request, "Interview date and time must be in the future")
            return redirect('scheduled_interview')

        if not meeting_link:
            room_name = request.POST.get("room_name", "").strip() or f"interview-{application.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            meeting_link = f"https://meet.jit.si/{room_name}"

        interview = Interview.objects.create(
            application=application,
            interviewer=interviewer,
            interview_type=interview_type,
            scheduled_at=scheduled_at,
            meeting_link=meeting_link,
            status="Scheduled",
        )
        send_interview_emails(request, interview, interviewer)
        return redirect('scheduled_interview')

    return render(request, "scheduled_interview.html", dashboard_context(
        curr_employee,
        applications=applications,
        interviewers=interviewers,
        interview_type_choices=interview_type_choices,
    ))


def create_test(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    if request.method == "POST":
        Category.objects.create(
            name=request.POST.get("name"),
            company=curr_employee.company,
        )
        messages.success(request, "Test category added successfully")
        return redirect('create_test')

    categories = Category.objects.filter(company=curr_employee.company).order_by("-id")
    return render(request, "create_test.html", dashboard_context(
        curr_employee,
        categories=categories,
    ))


def update_category(request, category_id):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    category = get_object_or_404(Category, id=category_id, company=curr_employee.company)

    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
        messages.success(request, "Test category updated successfully")
        return redirect('create_test')

    return render(request, "update_category.html", dashboard_context(
        curr_employee,
        category=category,
    ))


def delete_category(request, category_id):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    category = get_object_or_404(Category, id=category_id, company=curr_employee.company)
    category.delete()
    messages.success(request, "Test category deleted successfully")
    return redirect('create_test')


def add_question(request):
    curr_employee = get_current_employee(request)
    if not curr_employee:
        return redirect('login')

    categories = Category.objects.filter(company=curr_employee.company).order_by("name")
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

    questions = Question.objects.filter(job_profile__company=curr_employee.company).select_related("job_profile").order_by("-id")
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
    questions = Question.objects.filter(job_profile__company=curr_employee.company).select_related("job_profile").order_by("-id")

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

    tests = Test.objects.select_related("vacancy", "created_by").filter(created_by__company=curr_employee.company).order_by("-id")
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

    tests = Test.objects.select_related("vacancy").filter(created_by__company=curr_employee.company).order_by("-id")
    applications = Application.objects.select_related("job_id", "user_id").filter(
        job_id__created_by=curr_employee,
        status="Shortlisted",
    ).order_by("-applied_on", "-id")

    if request.method == "POST":
        test = get_object_or_404(Test, id=request.POST.get("test_id"), created_by__company=curr_employee.company)
        application = get_object_or_404(applications, id=request.POST.get("application_id"))

        if TestAssignment.objects.filter(application=application, test=test, status="Pending").exists():
            messages.warning(request, "This test is already allotted to the selected candidate")
            return redirect('allot_test')

        assignment = TestAssignment.objects.create(
            application=application,
            test=test,
        )
        send_test_assignment_email(request, assignment)
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


def take_test(request):
    curr_user = get_current_candidate(request)
    if not curr_user:
        return redirect('login')

    assignments = TestAssignment.objects.select_related(
        "application__user_id",
        "application__job_id",
        "test",
        "test__vacancy",
    ).filter(application__user_id=curr_user).order_by("-assigned_on", "-id")
    mark_expired_assignments(assignments)

    assignments = TestAssignment.objects.select_related(
        "application__user_id",
        "application__job_id",
        "test",
        "test__vacancy",
    ).filter(application__user_id=curr_user).order_by("-assigned_on", "-id")
    return render(request, "take_test.html", {
        "base_template": "base.html",
        "assignments": assignments,
    })


def take_test_detail(request, assignment_id):
    curr_user = get_current_candidate(request)
    if not curr_user:
        return redirect('login')

    assignment = get_object_or_404(
        TestAssignment.objects.select_related(
            "application__user_id",
            "application__job_id",
            "test",
            "test__vacancy",
        ).prefetch_related("test__questions"),
        id=assignment_id,
        application__user_id=curr_user,
    )

    if assignment.status == "Completed":
        return redirect('take_test_result', assignment.id)

    if assignment.status == "Expired":
        messages.error(request, "This test has expired")
        return redirect('take_test')

    if is_assignment_expired(assignment):
        assignment.status = "Expired"
        assignment.completed_on = timezone.now()
        assignment.save(update_fields=["status", "completed_on"])
        messages.error(request, "This test has expired")
        return redirect('take_test')

    questions = list(assignment.test.questions.all().order_by("id"))
    if not questions:
        messages.error(request, "No questions are available for this test")
        return redirect('take_test')

    return render(request, "take_test_detail.html", {
        "base_template": "base.html",
        "assignment": assignment,
        "questions": questions,
    })


def submit_test(request, assignment_id):
    curr_user = get_current_candidate(request)
    if not curr_user:
        return redirect('login')

    if request.method != "POST":
        return redirect('take_test_detail', assignment_id)

    assignment = get_object_or_404(
        TestAssignment.objects.select_related("application__user_id", "test").prefetch_related("test__questions"),
        id=assignment_id,
        application__user_id=curr_user,
    )

    if assignment.status != "Pending":
        messages.error(request, "This test cannot be submitted now")
        return redirect('take_test')

    if is_assignment_expired(assignment):
        assignment.status = "Expired"
        assignment.completed_on = timezone.now()
        assignment.save(update_fields=["status", "completed_on"])
        messages.error(request, "Test time expired")
        return redirect('take_test')

    questions = list(assignment.test.questions.all().order_by("id"))
    if not questions:
        messages.error(request, "No questions are available for this test")
        return redirect('take_test')

    score = 0
    total_possible = 0
    for question in questions:
        total_possible += question.marks or 0
        selected_answer = request.POST.get(f"answer_{question.id}")
        if normalize_test_answer(selected_answer) == normalize_test_answer(question.answer):
            score += question.marks or 0

    percentage = round((score / total_possible) * 100, 2) if total_possible else 0

    with transaction.atomic():
        assignment.score = score
        assignment.percentage = percentage
        assignment.completed_on = timezone.now()
        assignment.status = "Completed"
        assignment.save(update_fields=["score", "percentage", "completed_on", "status"])

    messages.success(request, "Test submitted successfully")
    return redirect('take_test_result', assignment.id)


def take_test_result(request, assignment_id):
    curr_user = get_current_candidate(request)
    if not curr_user:
        return redirect('login')

    assignment = get_object_or_404(
        TestAssignment.objects.select_related("application__user_id", "application__job_id", "test", "test__vacancy"),
        id=assignment_id,
        application__user_id=curr_user,
    )
    return render(request, "take_test_result.html", {
        "base_template": "base.html",
        "assignment": assignment,
    })



    
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


