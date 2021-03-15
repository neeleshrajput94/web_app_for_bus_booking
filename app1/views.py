from django.shortcuts import render
from decimal import Decimal

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Bus, Book
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal

import re
from django.contrib import messages


def home(request):
    if request.user.is_authenticated:
        return render(request, 'app1/home.html')
    else:
        return render(request, 'app1/signin.html')


def search_bus(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date=date_r)
        if bus_list:
            return render(request, 'app1/list.html', locals())
        else:
            context["error"] = "Sorry no buses available"
            return render(request, 'app1/search_bus.html', context)
    else:
        return render(request, 'app1/search_bus.html')

EMAIL_REGIX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-copyZ0-9._-]+\.[a-zA-Z]+$')

def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')
        if not EMAIL_REGIX.match(request.POST["email"]):
            messages.add_message(request, messages.ERROR, "invalid email fromat! ex: test@test.com")
            return render(request, 'app1/signup.html', context)        
        if User.objects.filter(email=request.POST["email"]).count() > 0:
            messages.add_message(request, messages.ERROR, "A user with this email already exixts!")
            return render(request, 'app1/signup.html', context)
        if request.POST["password"] != request.POST["confirm_password"]:
            messages.add_message(request, messages.ERROR, "password and password comfirmation must match!")
            return render(request, 'app1/signup.html', context)

        user = User.objects.create_user(name_r, email_r, password_r, )
        if user:
            login(request, user)
            return render(request, 'app1/thank.html')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'app1/signup.html', context)
    else:
        return render(request, 'app1/signup.html', context)



def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            # username = request.session['username']
            context["user"] = name_r
            context["id"] = request.user.id
            return render(request, 'app1/success.html', context)
            # return HttpResponseRedirect('success')
        else:
            messages.add_message(request, messages.ERROR, "invalid username or password!")
            return render(request, 'app1/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'app1/signin.html', context)


def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'app1/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'app1/success.html', context)


@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        seats_r = int(request.POST.get('no_seats'))
        bus = Bus.objects.get(id=id_r)
        if bus:
            if bus.rem >= int(seats_r):
                name_r = bus.bus_name
                cost = int(seats_r) * bus.price
                source_r = bus.source
                dest_r = bus.dest
                nos_r = Decimal(bus.nos)
                price_r = bus.price
                date_r = bus.date
                time_r = bus.time

                username_r = request.user.username
                email_r = request.user.email
                userid_r = request.user.id
                rem_r = bus.rem - seats_r

                Bus.objects.filter(id=id_r).update(rem=rem_r)

                book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                                           source=source_r, busid=id_r,
                                           dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                           status='BOOKED')
                print('------------book id-----------', book.id)

                # book.save()
                return render(request, 'app1/bookings.html', locals())
            else:
                context["error"] = "Sorry select fewer number of seats"
                return render(request, 'app1/search_bus.html', context)

    else:
        return render(request, 'app1/search_bus.html')


@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        if len(request.POST["bus_id"]) < 1:
            context["error"] = "Sorry You have not booked that bus"
            return render(request, 'app1/error.html', context)
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Book.objects.get(id=id_r)
            bus = Bus.objects.get(id=book.busid)
            rem_r = bus.rem + book.nos
            Bus.objects.filter(id=book.busid).update(rem=rem_r)
            #nos_r = book.nos - seats_r
            Book.objects.filter(id=id_r).update(status='CANCELLED')
            Book.objects.filter(id=id_r).update(nos=0)
            return redirect(seebookings)
        except Book.DoesNotExist:
            context["error"] = "Sorry You have not booked that bus"
            return render(request, 'app1/error.html', context)
    else:
        return render(request, 'app1/search_bus.html')

@login_required(login_url='signin')
def seebookings(request,new={}):
    context = {}
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'app1/booklist.html', locals())
    else:
        context["error"] = "Sorry no buses booked"
        return render(request, 'app1/search_bus.html', context)

def services_page(request):
    return render(request, 'app1/services.html')

def gallery_page(request):
    return render(request, 'app1/gallery.html')

def about_page(request):
    return render(request, 'app1/about.html')

def contact_page(request):
    return render(request, 'app1/contact.html')
