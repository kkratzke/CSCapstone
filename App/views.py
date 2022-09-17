from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views import View
from App.models import *
import datetime


class Home(View):
    def get(self, request):
        #  For the get method of home, clear the current user as the first line of code. So going to the home page (via get) is equivalent to logging out.
        request.session.pop("username", None)
        return render(request, "main/home.html")

    def post(self, request):
        try:
            user = User.objects.get(username=request.POST['username'])
        except User.DoesNotExist:
            return render(request, "main/home.html", {'error': 'Something went wrong..'})

        if user.password == request.POST['password']:
            request.session["username"] = request.POST["username"]

            if user.role == "Admin":
                return redirect('AdminMain')
            else:
                return redirect('Main')

        return render(request, "main/home.html", {'error': 'username/password incorrect'})


class AccountCreation(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")

        user = map(str, list(User.objects.all()))
        return render(request, "AdminPages/CreateAccount.html", {"user": user})

    def post(self, request):
        username_first = request.POST['user_first_name']
        username_last = request.POST['user_last_name']
        email = request.POST['email']
        user_role = request.POST['role']
        user_password = "123456"  # we can set it to a default password like 123456

        if username_first != '' or user_role != '':
            User.objects.create(username=email, role=user_role, password=user_password, user_last_name=username_last,
                                user_first_name=username_first, email=email)
            message = "Account creation successful"

        return render(request, "AdminPages/CreateAccount.html", {"message": message})


class AllUsers(View):
    def get(self, request, **kwargs):
        if not request.session.get("username"):
            return redirect("home")

        all_users = User.objects.all()

        try:
            user = self.kwargs["username"]
        except KeyError:
            return render(request, "AdminPages/AllUsers.html", {'name': all_users})  # change names to name

        User.objects.filter(email=user).delete()

        return render(request, "AdminPages/AllUsers.html", {'name': all_users})  # change names to name

    def post(self, request):
        return render(request, "AdminPages/AllUsers.html")


class AdminHome(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")
        return render(request, "AdminPages/AdminMain.html")

    def post(self, request):
        return render(request, "AdminPages/AdminMain.html")


class Classes(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")
        course = Course.objects.all()
        return render(request, "AdminPages/Classes.html", {"course": course})

    def post(self, request):
        return render(request, "AdminPages/Classes.html")


class Users(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")
        user = User.objects.get(username=request.session['username'])
        return render(request, "Users/Main.html", {"user": user})

    def post(self, request):
        user = User.objects.get(username=request.session['username'])
        return render(request, "Users/Main.html", {"user": user})


class UserEdit(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")

        user = User.objects.get(username=request.session['username'])

        return render(request, "Users/Edit.html", {"user": user})

    def post(self, request):
        user = User.objects.get(username=request.session['username'])
        message = None

        if request.POST['password'] != '':
            user_password = request.POST['password']
            user.password = user_password
            message = "Account changes successful"
        if request.POST['second_email'] != '':
            user_secondEmail = request.POST['second_email']
            user.secondary_email = user_secondEmail
            message = "Account changes successful"
        if request.POST['phone_number'] != '':
            user_phone = request.POST['phone_number']
            user.number = user_phone
            message = "Account changes successful"

        user.save()

        return render(request, "Users/Edit.html", {"message": message, "user": user})


class UserClasses(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")
        user = User.objects.get(username=request.session['username'])
        if user.role == "Instructor":
            course = Course.objects.filter(instructor=user.user_first_name + " " + user.user_last_name)

        print(user)
        print(user.user_first_name + user.user_last_name)
        print(course)
        return render(request, "Users/UserClasses.html", {"course": course})

    def post(self, request):
        return render(request, "Users/UserClasses.html")


class CreateCourse(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("home")

        return render(request, "AdminPages/CreateCourse.html")

    def post(self, request):
        course_name = request.POST['course_name']
        course_code = request.POST['course_code']

        # If any Sections, Format to remove white spaces(Null course sections)
        course_sections = [request.POST['course_section1'], request.POST['course_section2'],
                           request.POST['course_section3']]

        course_sections = formatSections(course_sections)

        print(course_sections)

        scale = "No Grade Scale"  # temp will change
        week = "whenever"         # temp will change
        data = datetime.datetime.now()

        # Defaults the current instructor to admin
        if course_name != '' and course_code != '':
            created_course = Course.objects.create(courseName=course_name, courseCode=course_code, instructor=User.objects.get(username=request.session['username']))
            for i in course_sections:
                Section.objects.create(user=User.objects.get(username=request.session['username']), sectionNumber=i,
                                       course=created_course, week=week, data=data)

            message = "Course Successfully created!"

        return render(request, "AdminPages/CreateCourse.html", {"message": message})


class EditCourse(View):
    def get(self, request, **kwargs):
        course = self.kwargs["course"]
        section = Section.objects.filter(course__courseName=course)

        course_info = Course.objects.filter(courseName=course)
        course1 = Course.objects.get(courseName=course)
        instructors = User.objects.filter(role="Instructor")

        current_instructor = course1.instructor

        return render(request, "AdminPages/EditCourse.html", {"course": course_info, "section_info": section, "instructors": instructors, "current_instructor": current_instructor})

    def post(self, request):
        instructor = request.POST['Instructor']
        course_name = request.POST['course1']
        course_code = request.POST['course_code']

        course_info = Course.objects.get(courseName=course_name, courseCode=course_code)
        course_info.instructor = instructor
        course_info.save()

        message = "Changes saved"
        course = Course.objects.all()

        return render(request, "AdminPages/Classes.html", {"message": message, "course": course})


class DeleteCourse(View):
    def get(self, request, **kwargs):
        to_delete = self.kwargs["delete"]
        Course.objects.filter(courseName=to_delete).delete()
        course = Course.objects.all()
        return render(request, "AdminPages/Classes.html", {"course": course})

    def post(self, request):
        return render(request, "AdminPages/Classes.html")


class ViewSections(View):
    def get(self, request, **kwargs):
        current_TA = []
        course = self.kwargs["course"]
        section = Section.objects.filter(course__courseName=course)
        print(section)
        for i in section:
            current_TA.append(i.user)

        print(current_TA)

        TA = User.objects.filter(role="TA")
        user = User.objects.get(username=request.session['username'])
        return render(request, "AdminPages/ViewSections.html", {"course": course, "section_info": section, "TA": TA, "current_TA": current_TA, "user": user})

    def post(self, request):
        current_TA = []
        TA_current = request.POST['TA']
        name = TA_current.split()
        course = request.POST['course2']
        current_section = request.POST['section_number']
        section = Section.objects.get(course__courseName=course, sectionNumber=current_section)
        to_send = Section.objects.filter(course__courseName=course)
        user = User.objects.get(user_first_name=name[0], user_last_name=name[1])
        section.user = user
        section.save()

        for i in to_send:
            current_TA.append(i.user)

        All_TA = User.objects.filter(role="TA")
        user = User.objects.get(username=request.session['username'])
        return render(request, "AdminPages/ViewSections.html", {"course": course, "section_info": to_send, "TA": All_TA, "current_TA": current_TA, "user": user})


class DeleteSection(View):
    def get(self, request, **kwargs):
        section = self.kwargs["delete_section"]
        all_sections = Section.objects.all()
        got = getSection(section)

        for i in all_sections:
            y = i.id.__str__()
            if y == got:
                to_delete = i

        sections = Section.objects.filter(course__courseName=to_delete.course.courseName)
        Section.objects.filter(course__courseName=to_delete.course.courseName, sectionNumber=to_delete.sectionNumber).delete()
        message = "course successfully delete"
        TA = User.objects.filter(role="TA")
        return render(request, "AdminPages/ViewSections.html", {"section_info": sections, "TA": TA})

    def post(self, request):
        return render(request, "AdminPages/ViewSections.html")


class AddSection(View):

    def get(self, request):
        return render(request, "AdminPages/AddSection.html")

    def post(self, request):
        return render(request, "AdminPages/AddSection.html")


def formatSections(self):
    send = []
    for section in self:
        if section.__str__() != '':
            send.append(section)

    return send


def getSection(self):
    section = ''
    for char in self.__str__():
        if char.isnumeric():
            section += char

    return section