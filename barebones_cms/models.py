from mptt.models import MPTTModel, TreeForeignKey

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


# Allow the cms app to be completely overridden with another namespace
CMS_APP = getattr(settings, 'BB_CMS_APP_NAME', 'apps.cms').split('.')[-1]


class BasePageTemplate(models.Model):
    name = models.CharField(max_length=200)
    template_file = models.FileField(upload_to='templates/cms/', max_length=200)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class BasePage(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=100)
    page_template = models.ForeignKey("%s.PageTemplate" % CMS_APP, related_name="template")
    is_deleted = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    def __unicode__(self):
        if self.parent:
            return "%s > %s" % (self.parent, self.slug)
        else:
            return self.slug

    class Meta:
        abstract = True


class BaseRegion(models.Model):
    name = models.CharField(max_length=255)
    block_name = models.CharField(max_length=255)
    template = models.ForeignKey("%s.PageTemplate" % CMS_APP)

    class Meta:
        abstract = True


class BaseContentBlockLink(models.Model):
    """ Creates a generic link between content blocks and the page / regions.
        Required in order to make blocks of different types.
    """
    page = models.ForeignKey("%s.Page" % CMS_APP)
    region = models.ForeignKey("%s.Region" % CMS_APP, null=True, blank=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_type = models.ForeignKey(ContentType, db_index=True)
    model_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True


class BaseContentBlock(models.Model):
    name = models.CharField(max_length=255)
    partial = models.FileField(upload_to='templates/cms/', max_length=200)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


# Content Blocks
class SimpleContentBlock(BaseContentBlock):
    content = models.CharField(max_length=255)


# Register allowed content blocks by adding them here
REGISTERED_CONTENT_BLOCKS = [
    ('Simple Content Block', SimpleContentBlock),
]
