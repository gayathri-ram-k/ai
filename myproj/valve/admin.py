from django.contrib import admin

#register models
from .models import DiseaseDetection

admin.site.register(DiseaseDetection)
