from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from .models import Doctor, Specialty
from django.contrib.auth.decorators import login_required


def doctor_list(request):
    q = request.GET.get("q", "").strip()
    specialty_slug = request.GET.get("specialty", "").strip()
    min_rating = request.GET.get("min_rating", "").strip()
    sort_by = request.GET.get("sort", "-rating")

    doctors = (
        Doctor.objects.select_related("user", "specialty")
        .annotate(
            avg_rating=Avg("received_feedbacks__rate"),
            feedbacks_count=Count("received_feedbacks"),
        )
    )

    if q:
        doctors = doctors.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(specialty__title__icontains=q)
        )

    if specialty_slug:
        doctors = doctors.filter(specialty__slug=specialty_slug)

    if min_rating and min_rating.isdigit():
        doctors = doctors.filter(avg_rating__gte=int(min_rating))

    sort_mapping = {
        "-rating": F("avg_rating").desc(nulls_last=True),
        "rating": F("avg_rating").asc(nulls_last=True),
        "fee": "visit_fee",
        "-fee": "-visit_fee",
        "name": "user__last_name",
    }
    order_field = sort_mapping.get(sort_by, F("avg_rating").desc(nulls_last=True))
    doctors = doctors.order_by(order_field)
    paginator = Paginator(doctors, 30)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "specialties": Specialty.objects.all(),
        "q": q,
        "selected_specialty": specialty_slug,
        "selected_min_rating": min_rating,
        "selected_sort": sort_by,
    }

    return render(request, "doctor/doctor_list.html", context)


@login_required(login_url="sign_in")
def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related("user", "specialty")
        .annotate(
            avg_rating=Avg("received_feedbacks__rate"),
            feedbacks_count=Count("received_feedbacks"),
        ),
        pk=pk,
    )
    return render(request, "doctor/doctor_detail.html", {"doctor": doctor})

