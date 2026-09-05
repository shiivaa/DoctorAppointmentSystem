from django.urls import path
from .import views

app_name = 'user'
urlpatterns = [
    path("send-otp/", views.SendOtpView.as_view() ,name="send_otp"),
    path("verify-otp/", views.VerifyOtpView.as_view() ,name="verify_otp"),
]