from django.db import models

# Create your models here.


ROLES = (
    ("TA", "TA"),
    ("Instructor", "Instructor"),
    ("Admin", "Admin"),
)


class User(models.Model):
    username = models.CharField(max_length=20)
    user_last_name = models.CharField(max_length=20)
    user_first_name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    secondary_email = models.CharField(max_length=30) #New
    number = models.CharField(max_length=20) #New
    password = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLES)

    def str(self):
        return self.username


class Syllabus(models.Model):
    A = models.IntegerField()
    B = models.IntegerField()
    C = models.IntegerField()
    D = models.IntegerField()
    F = models.IntegerField()
    policies = models.CharField(max_length=1000)


class Course(models.Model):
    courseName = models.CharField(max_length=20)
    courseCode = models.CharField(max_length=20)
    instructor = models.CharField(max_length=20)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)

    def str(self):
        return self.courseName


class Section(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateTimeField(max_length=30)
    week = models.CharField(max_length=5)
    room = models.CharField(max_length=10)
    sectionNumber = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def str(self):
        return self.sectionNumber