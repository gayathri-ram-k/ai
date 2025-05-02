
from django.db import models

class DiseaseDetection(models.Model):
    disease_name = models.CharField(max_length=255)
    audio = models.FileField(upload_to='audio/')
    remarks = models.TextField()


# class DiseaseDetection(models.Model):
#     disease_name = models.CharField(max_length=255)
#     remarks = models.TextField()
#     audio_file = models.CharField(max_length=255)  # Add this if not present
#     def _str_(self):
#         return self.disease_name