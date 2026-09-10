from django.urls import path
from feedback.views import feedback_create_view,doctor_feedback_list_view


urlpatterns = [
   path('appointment/<int:apponitment_pk>/add_feedback/',feedback_create_view,name='add_feedback'),
   path('doctor/<int:doctor_pk>/show_feedbacks',doctor_feedback_list_view,name='show_feedbacks'),
]
