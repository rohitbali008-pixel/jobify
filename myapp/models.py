from django.db import models


class User(models.Model):
    fullname = models.CharField(max_length=100)
    dateofbirth= models.IntegerField() 
    mobileno= models.IntegerField()
    email = models.EmailField(unique=True)
    address = models.TextField()
    password = models.CharField(max_length=100 )

    def __str__(self):
        return self.fullname


class Profile(models.Model):
    profile_pic = models.ImageField(upload_to='avatars/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True)
    gender = models.CharField(max_length=50, default="male")
    experience = models.IntegerField(null=True , blank= True)

    def __str__(self):
        return f"Profile of {self.user.fullname}"
    
    
class Company(models.Model):
    name= models.CharField(max_length=100)
    logo=models.ImageField()
    email= models.EmailField(unique=True)
    gstin=models.TextField()

    def __str__(self):
        return self.name
    
    
class Employee(models.Model):
    fullname = models.CharField(max_length=100)
    designation= models.CharField(max_length=100)
    joiningdate= models.DateField()
    sallary= models.IntegerField()
    email=models.EmailField(unique=True)
    password= models.CharField(max_length=100)
    company=models.ForeignKey(Company , on_delete=models.CASCADE, related_name="employees")
        
    def __str__(self):
        return self.fullname
    

class Jobs(models.Model):
    title = models.CharField( max_length=100)
    
    experience= models.IntegerField()
    discription= models.CharField( max_length=100)
    skills = models.CharField( max_length=100)
    education = models.CharField( max_length=100)
    minsalary =models.IntegerField()
    maxsalary =models.IntegerField()
    created_by =models.ForeignKey(Employee , on_delete=models.CASCADE, related_name="jobs")
    deadline= models.DateField()
    vacancies= models.IntegerField()
    location= models.CharField( max_length=50)
           
    def __str__(self):
        return self.title
    
class Application(models.Model):
    choices =[
        ('A','choice1'),
        ('B','choice2')
    ]
    job_id = models.ForeignKey(Jobs , on_delete=models.CASCADE, related_name="jobs")
    user_id =models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    resume = models.FileField(upload_to='media/', blank=True, null=True)
    skills = models.CharField(max_length=100)
    experience=models.IntegerField()
    current_salary=models.IntegerField()
    apply_date=models.DateTimeField()
    status=  models.CharField(max_length=1, choices=choices, default='A')
    education=models.CharField( max_length=50 , null =True)\
    
class Category(models.Model):
    name=models.CharField(max_length=100)
    company=models.ForeignKey(Company , on_delete=models.CASCADE, related_name="company")


class Questions(models.Model):
    job_profile=models.ForeignKey(Category,on_delete=models.CASCADE, related_name="job_profile")
    questions=models.CharField(max_length=100)
    opt_a= models.CharField(max_length=50)
    opt_b=models.CharField(max_length=50)
    opt_c=models.CharField(max_length=50)
    opt_d=models.CharField(max_length=50)
    answer=models.CharField(max_length=50)
    marks=models.IntegerField()
    added_by=models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True, related_name="employee")
    



