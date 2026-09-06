from django.db import models


class Specialty(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="specialty title")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Doctor(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, null=True, blank=True, related_name="doctor_profile")
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    visit_fee = models.DecimalField(max_digits=9, decimal_places=0, default=0)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.doctor} | {self.start_time} - {self.end_time}"

