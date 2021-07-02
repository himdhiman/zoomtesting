from django.contrib import admin
from api import models

admin.site.register([
    models.Licence,
    models.Subject,
    models.Teacher,
    models.Batch,
])