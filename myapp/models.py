from django.db import models


class User(models.Model):
    fullname = models.CharField(max_length=100)
    dateofbirth= models.DateField() 
    mobileno= models.IntegerField()
    email = models.EmailField(unique=True)
    address = models.TextField()
    password = models.CharField(max_length=100 )

    def __str__(self):
        return self.fullname


class Profile(models.Model):
    CHOICES=[
        ("Fresher", "Fresher"),
        ("0-1 years", "0-1 years"),
        ("1-2 years", "1-2 years"),
        ("2-3 years", "2-3 years"),
        ("3+ years", "More than 3 years"),
        ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True)
    profile_pic = models.ImageField(upload_to='avatars/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    gender = models.CharField(max_length=50, default="male") 
    experience = models.CharField(max_length=100,choices=CHOICES)
    education=models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"Profile of {self.user.fullname}"
    
    
class Company(models.Model):
    name= models.CharField(max_length=100)
    logo=models.ImageField()
    email= models.EmailField(unique=True)
    location = models.CharField( max_length=100, null=True, blank=True)
    gstin=models.TextField()
    phone=models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_date=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
    
class Employee(models.Model):
    company=models.ForeignKey(Company , on_delete=models.CASCADE, related_name="employees")
    profile_pic = models.ImageField(upload_to='emp_pp/', blank=True, null=True)
    fullname = models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15, null=True, blank=True)
    password= models.CharField(max_length=100)
    joiningdate= models.DateField()
    sallary= models.IntegerField()

    designation=models.CharField(max_length=100, null=True, blank=True, choices=(
     ('Software Developer', 'Software Developer'),
     ('Senior Developer', 'Senior Developer'),
     ('Full Stack Developer', 'Full Stack Developer'),
     ('Backend Developer', 'Backend Developer'),
     ('Frontend Developer', 'Frontend Developer'),
     ('Data Analyst', 'Data Analyst'),
     ('QA Tester', 'QA Tester'),
     ('Accountant', 'Accountant'),
     ('Sales Executive', 'Sales Executive'),
     ('Marketing Executive', 'Marketing Executive'),
     ('Technician', 'Technician'),
     ('Manager', 'Manager'),
     ('HR', 'HR')
     ))
    
    role=models.CharField(max_length=100, choices=(('HR Executive', 'HR Executive'),('Employee' ,'Employee'), ('Manager','Manager')), default='Employee')
 
   
    def __str__(self):
        return self.fullname
    

class Job(models.Model):
    title = models.CharField( max_length=100)
    experience= models.IntegerField()
    discription= models.CharField( max_length=100)
    skills = models.CharField( max_length=100)
    qualification = models.CharField( max_length=100)
    minsalary =models.IntegerField()
    maxsalary =models.IntegerField()
    created_by =models.ForeignKey(Employee , on_delete=models.SET_NULL, null=True, blank=True)
    deadline= models.DateField()
    vacancies= models.IntegerField()
    location= models.CharField( max_length=50)
           
    def __str__(self):
        return self.title
    
class Application(models.Model):
 
    job_id = models.ForeignKey(Job , on_delete=models.CASCADE, related_name="jobs")
    user_id =models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resume = models.FileField(upload_to='media/', blank=True, null=True)
    skills = models.CharField(max_length=100)
    experience = models.IntegerField(default=0)
    apply_date=models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=(
            ("Under Review", "Under Review"),
            ("Shortlisted", "Shortlisted"),
            ("Rejected", "Rejected"),
            ("Selected", "Selected"),
        ),
        default="Under Review"
    )
  
    ats_score = models.FloatField(null=True, blank=True) 
    applied_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user_id.fullname} - {self.job_id.title}" 
    
 






class Category(models.Model):
    logo = models.ImageField(upload_to='cat_logo/', blank=True, null=True)
    name=models.CharField(max_length=100)
    company=models.ForeignKey(Company , on_delete=models.CASCADE, related_name="company")


    def __str__(self):
        return f"{self.name}" 


class Question(models.Model):
    job_profile=models.ForeignKey(Category,on_delete=models.CASCADE, related_name="job_profile")
    questions=models.CharField(max_length=100)
    opt_a= models.CharField(max_length=50)
    opt_b=models.CharField(max_length=50)
    opt_c=models.CharField(max_length=50)
    opt_d=models.CharField(max_length=50)
    answer=models.CharField(max_length=50)
    marks=models.IntegerField()
    added_by=models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True, related_name="employee")
    

class Test(models.Model):
    title = models.CharField(max_length=100)
    vacancy = models.ForeignKey(Job, on_delete = models.CASCADE)
    questions = models.ManyToManyField(Question)
    duration_minutes = models.IntegerField()
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    created_by = models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.title

class TestAssignment(models.Model):

    application = models.ForeignKey( Application, on_delete=models.CASCADE )
    test = models.ForeignKey( Test, on_delete=models.CASCADE )
    score = models.IntegerField(default=0 )
    percentage = models.FloatField(default=0 )
    assigned_on = models.DateTimeField(auto_now_add=True )
    completed_on = models.DateTimeField( null=True,blank=True)

    status = models.CharField(
        max_length=20,
        choices=(
            ('Pending','Pending'),
            ('Completed','Completed'),
            ('Expired','Expired'),
        ),default='Pending' )

    def __str__(self):
        return f"{self.application.user_id.fullname}"