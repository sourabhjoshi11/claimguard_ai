from django.urls import path
from .views import upload_claim

urlpatterns=[
    path('uploads/',upload_claim)
]