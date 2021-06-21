from django.contrib import admin

# Register your models here.

from .models import USER_INFO, User, Airline_Company, AIRPLANE, AIRPORT, ACCESS, FLIGHT_TRIP, SEAT, PASSENGER, FARE

admin.site.register(USER_INFO)
admin.site.register(Airline_Company)
admin.site.register(AIRPLANE)
admin.site.register(AIRPORT)
admin.site.register(ACCESS)
admin.site.register(FLIGHT_TRIP)
admin.site.register(SEAT)
admin.site.register(PASSENGER)
admin.site.register(FARE)
