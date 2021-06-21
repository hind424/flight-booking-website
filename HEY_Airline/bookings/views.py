from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from bookings.forms import UserForm, UserProfileInfoForm, passengerSet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from bookings.models import AIRPORT, USER_INFO, Airline_Company, AIRPLANE, AIRPORT, ACCESS, FLIGHT_TRIP, SEAT, PASSENGER, FARE

# Create your views here.
def index(request):
    airport = AIRPORT.objects.all()
    return render(request,'bookings/index.html', {'airports' : airport})


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
    
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                print('found it')
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'bookings/registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                request.session['userId'] = user.id
                request.session['discount'] = USER_INFO.objects.get(user_id = user.id).DISCOUNT
                print(user.id)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'bookings/login.html', {})



@login_required
def payment(request):
    trip = int(request.session["trip"])
    airplane = int(request.session["airplane"])
    passengers = request.session["passengers"]
    num_tickets = len(passengers)

    if request.method == 'GET':
        fare = FARE.objects.get(trip_id = trip)
        amount = fare.AMOUNT
        tax = fare.TAX
        print(tax)
        currency = fare.CURRENCY
        content ={"num_tickets":num_tickets, "amount":amount, "tax":tax,"currency":currency}
        return render(request, 'bookings/payment.html',content )
    elif request.method == 'POST':
        F=0
        B=0
        E=0
        for passenger in passengers:
            fname = passenger['FNAME']
            lname = passenger['LNAME']
            phone = passenger['PHONE']
            sex = passenger['SEX']
            Class = passenger['CLASS']
            if Class == 'F':
                F+=1
            elif Class == 'B':
                B+=1
            elif Class == 'E':
                E+=1
            seat = SEAT.objects.get(airplane_number = airplane, trip_id = trip)
            First = seat.FIRST
            Business = seat.BUSINESS
            Economy = seat.ECONOMY
            if (First - F) and (Business - B) and (Economy - E) !=0:
                p = PASSENGER.objects.create(FNAME=fname, LNAME=lname, PHONE = phone, airplane_number_id = airplane, SEX = sex, CLASS = Class, trip_id_id =trip)
                p.save()
                print("INSERTED")
                seat = SEAT.objects.filter(airplane_number = airplane, trip_id = trip).update(FIRST = First -F, BUSINESS = Business - B, ECONOMY = Economy - E)
                return HttpResponseRedirect(reverse('index'))
            else:
                print("Not enough seats available")
                messages.error(request,'There are no seats available for the selected preference !')
                return redirect('book')
        return render(request,'bookings/payment.html')

@login_required
def search(request):
    if request.method == 'POST':
        fromPlace = request.POST.get('from')
        toPlace = request.POST.get('to')
        tripWay = request.POST.get('tripWay')
        # roundTrip = request.POST.get('round-trip')
        departure = request.POST.get('departure-date')
        returnDate = request.POST.get('return-date')
        travellers = request.POST.get('number-of-travellers')
        seatClass = request.POST.get('class')
        print(fromPlace,toPlace,tripWay,departure,returnDate,travellers,seatClass)

        flightTrip = FLIGHT_TRIP.objects.filter(DEPARTURE_AIRPORT__exact = fromPlace , ARIVAL_AIRPORT__exact = toPlace, )
        
        if tripWay == '1':
            flightTrip = flightTrip.select_related('airplane_number').filter(DEPART_TIME__date = departure).values()
            airplanes = flightTrip.values_list('airplane_number','TRIP_ID')
            airports = flightTrip.values_list('DEPARTURE_AIRPORT','ARIVAL_AIRPORT')
            if flightTrip and airplanes != None:
                airplane_number, trip_id= zip(*airplanes)
                depart, arival = zip(*airports)
                seat = SEAT.objects.filter(airplane_number__in = airplane_number, trip_id__in = trip_id)
                fare = FARE.objects.filter(trip_id__in = trip_id)
                departAirport = AIRPORT.objects.filter(AIRPORT_CODE__in = depart).values_list('AIRPORT_NAME',flat=True)
                arivalAirport = AIRPORT.objects.filter(AIRPORT_CODE__in = arival).values_list('AIRPORT_NAME',flat=True)
                # print(flightTrip.values(), seat.values(), fare.values())
                # print(departAirport[0])
                content = {
                    'planes' : zip(flightTrip.values(), seat.values(), fare.values()),
                    'd' : departAirport[0],
                    'a' : arivalAirport[0]
                }
                print("Inside oneway")
                return render(request, "bookings/result.html", content)
            else:
                return render(request, "bookings/result.html", {'available' : False})
        elif tripWay == '2':
            flightTrip = flightTrip.select_related('airplane_number').filter(DEPART_TIME__date = departure, ARIVAL_TIME__date = returnDate).values()
            airplanes = flightTrip.values_list('airplane_number','TRIP_ID')
            airports = flightTrip.values_list('DEPARTURE_AIRPORT','ARIVAL_AIRPORT')

            if flightTrip and airplanes != None:
                airplane_number, trip_id= zip(*airplanes)
                depart, arival = zip(*airports)
                seat = SEAT.objects.filter(airplane_number__in = airplane_number, trip_id__in = trip_id)
                fare = FARE.objects.filter(trip_id__in = trip_id)
                departAirport = AIRPORT.objects.filter(AIRPORT_CODE__in = depart).values_list('AIRPORT_NAME',flat=True)
                arivalAirport = AIRPORT.objects.filter(AIRPORT_CODE__in = arival).values_list('AIRPORT_NAME',flat=True)
               
                content = {
                    'planes' : zip(flightTrip.values(), seat.values(), fare.values()),
                    'd' : departAirport[0],
                    'a' : arivalAirport[0]
                }
                return render(request, "bookings/result.html", content)
            else:
                return render(request, "bookings/result.html", {'available' : False})
    return HttpResponseRedirect(reverse('index'))

@login_required
def trip(request,tripId,airplane_number_id):
    request.session["trip"] = tripId
    request.session["airplane"] = airplane_number_id
    request.session.modified = True
    return HttpResponseRedirect(reverse('book'))

@login_required
def book(request):

    if request.method == "GET":
        formset = passengerSet(queryset = PASSENGER.objects.none())
        return render(request, "bookings/book.html",{'passenger_set':formset})

    if request.method == "POST":
        formset = passengerSet(data=request.POST)
        if formset.is_valid():
            if formset.cleaned_data != {}:
                form = formset.cleaned_data
                _ = filter(None, form)
                p = []
                for passenger in _:
                    if passenger['DELETE'] == False:
                        p.append(passenger)
                request.session["passengers"] = p
                request.session.modified = True
           
            return HttpResponseRedirect(reverse("payment"))
        return render(request, "bookings/book.html",{'passenger_set':formset})
    return HttpResponseRedirect(reverse('book'))
