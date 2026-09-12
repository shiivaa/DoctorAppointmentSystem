from django.urls import path

from . import views

app_name = 'appointment'

urlpatterns = [
    path('doctor/<int:doctor_pk>/days/',views.doctor_working_days,name='doctor-appointment-days'),

    path('doctor/<int:doctor_pk>/times/<str:date>/',views.doctor_appointment_times,
         name='doctor-appointment-times'),

    path('doctor/<int:doctor_pk>/book/',views.book_appointment,name='book-appointment'),

    path('my-appointments/',views.my_appointments,name='my-appointments'),
]