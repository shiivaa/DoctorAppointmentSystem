from django.urls import path
from .import views

urlpatterns = [
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("complete-registration/", views.complete_registration, name="complete_registration"),
    path("logout/", views.logout_user, name="logout"),
    path("profile/", views.patient_profile, name="patient_profile"),
    path("profile/update/", views.update_patient_profile, name="update_patient_profile"),
    path("wallet/", views.wallet, name="wallet"),
    path("wallet/transactions/", views.transactions, name="wallet_transactions"),
    path("home/", views.home, name="home"),
]