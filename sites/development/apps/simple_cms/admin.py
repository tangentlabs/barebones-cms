from django.contrib import admin  # pragma: no cover

from apps.simple_cms import models  # pragma: no cover
from barebones_cms.models import SimpleContentBlock


admin.site.register(models.Page)  # pragma: no cover
admin.site.register(models.PageTemplate)  # pragma: no cover
admin.site.register(models.Region)  # pragma: no cover
admin.site.register(SimpleContentBlock)  # pragma: no cover
admin.site.register(models.ContentBlockLink)  # pragma: no cover

