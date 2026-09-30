from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bingo_app.urls')), # መነሻው ሊንክ ወደ bingo_app እንዲሄድ ያደርጋል
]