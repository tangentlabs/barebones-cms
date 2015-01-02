from mptt.models import MPTTModel, TreeForeignKey

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class BasePage(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.CharField(max_length=100)
    template = models.ForeignKey('cms.PageTemplate')
    is_deleted = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    def __unicode__(self):
        if self.parent:
            return "%s > %s" % (self.parent, self.slug)
        else:
            return self.slug

    class Meta:
        abstract = True


class Page(BasePage):
    """ Separated this out to make sure things are a little more extendable
    """
    pass


class PageTemplate(models.Model):
    template_file = models.FileField(upload_to='templates/cms/', max_length=200)

    def __unicode__(self):
        return self.template_file.name

    def __str__(self):
        return self.__unicode__()


class Region(models.Model):
    name = models.CharField(max_length=255)
    block_name = models.CharField(max_length=255)
    template = models.ForeignKey('cms.PageTemplate')


class ContentBlockLink(models.Model):
    """ Creates a generic link between content blocks and the page / regions.
        Required in order to make blocks of different types.
    """
    page = models.ForeignKey('cms.Page')
    region = models.ForeignKey('cms.Region', null=True, blank=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_type = models.ForeignKey(ContentType, db_index=True)
    model_object = generic.GenericForeignKey('content_type', 'object_id')


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
