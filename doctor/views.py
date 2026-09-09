from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from .models import Doctor


def home(request):
    q = request.GET.get("q", "").strip()

    doctors = (
        Doctor.objects.select_related("user", "specialty")
        .annotate(
            avg_rating=Avg("received_feedbacks__rate"),
            feedbacks_count=Count("received_feedbacks"),
        )
        .all()
    )

    if q:
        doctors = doctors.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(specialty__title__icontains=q)
        )

    doctors = doctors.order_by("-avg_rating")

    page_obj = Paginator(doctors, 30).get_page(request.GET.get("page"))

    return render(
        request,
        "doctors/home.html",
        {"page_obj": page_obj, "q": q}
    )

