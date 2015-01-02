from django.db import models

from barebones_cms import models as bb_models


class Page(bb_models.BasePage):
    custom_field = models.CharField(max_length=255, null=True, blank=True)


class PageTemplate(bb_models.BasePageTemplate):
    pass


class ContentBlockLink(bb_models.BaseContentBlockLink):
    pass


class Region(bb_models.BaseRegion):
    pass

