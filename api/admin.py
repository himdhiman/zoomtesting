from django.contrib import admin
from api import models

admin.site.register([
    models.CustomUser,
    models.Licence,
    models.Subject,
    models.Batch,
    models.Category,
    models.SubCategory,
    models.Course
])