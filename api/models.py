from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.contrib.auth.base_user import BaseUserManager

_branches = [
    ("ALL","All"),
    ("CSE","Computer Science & Engineering"),
    ("IT","Information Technology"),
    ("AI&DS","Artificial Intelligence & Data Science"),
    ("CS-AI","Computer Science & Engineering with AI"),
    ("EE","Electrical Engineering"),
    ("ECE","Electronics & Communication Engineering"),
    ("ME","Mechanical Engineering"),
    ("CE","Civil Engineering"),
]

_difficulties = [
    ('h',"Hard"),
    ('m',"Medium"),
    ('e',"Easy")
]

_status = [
    ('A','Accepted'),
    ('R','Accepted'),
]

class UserManager(BaseUserManager):
    use_in_migrations=True

    def create_user(self,email=None,phone=None,password=None,**extra):
        if not email:
            raise ValueError('Email  is required')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self,password,**extra):
        extra.setdefault('is_staff',True)
        extra.setdefault('is_superuser',True)
        extra.setdefault('is_active',True)

        if extra.get('is_staff') is not True:
            raise ValueError(('is_staff should be True for Superuser'))

        return self.create_user(password=password,**extra) 
    

class User(AbstractUser):
    # username = None
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(blank=True,null=True)
    phone = models.CharField(blank=True,null=True,max_length=15)
    branch = models.CharField(max_length=5,choices=_branches,blank=True,null=True)
    batch = models.PositiveSmallIntegerField(blank=True,null=True)
    # objects = UserManager()

    # USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Contest(models.Model):
    name = models.CharField(max_length=50)
    branch = models.CharField(max_length=5,choices=_branches)
    description = models.TextField(null=True,blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField('Problem', through='ContestProblem', related_name='contests')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Problem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    input = models.TextField()
    output = models.TextField()
    constraints = models.TextField()
    difficulty = models.CharField(choices=_difficulties,max_length=1)
    points = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Submission(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, verbose_name="Problem", on_delete=models.CASCADE)
    status = models.CharField(choices=_status,max_length=3)
    detail = models.TextField()
    passed_testcases = models.PositiveSmallIntegerField()
    total_testcases = models.PositiveSmallIntegerField()
    
class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('contest', 'problem')
        
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    visible = models.BooleanField(default=False)
    input_data = models.TextField()
    expected_output = models.TextField()

    class Meta:
        unique_together = ('problem','input_data')
    
    
