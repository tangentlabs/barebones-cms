import os

from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from barebones_cms import models


class PageService(object):
    def get_page_from_path(self, path):
        # Get rid of leading and ending slashes. Then split the path into parts
        parts = path.lstrip('/').rstrip('/').split('/')

        # Get the root page for the path
        try:
            root_page = self.get_root_page_by_slug(parts.pop(0))
        except (models.Page.DoesNotExist, MultipleObjectsReturned):
            # At least one slug failed to match. Return nothing
            return

        if not parts:
            # If there are no more parts, this was a root page
            return root_page
        parent_page = root_page

        # Be greedy! In some cases it would be more efficient to be lazy, but
        # being greedy will always ensure the correct page is returned.
        try:
            page = self.get_published_child(root_page, parts)
        except (models.Page.DoesNotExist, MultipleObjectsReturned):
            # At least one slug failed to match. Return nothing
            return
        return page

    def get_published_child(self, parent_page, slug_parts):
        page_slug = slug_parts.pop(0)
        page = parent_page.children.get(
            slug=page_slug, is_deleted=False, is_published=True)
        if not slug_parts:
            return page
        # Otherwise recurse
        return self.get_published_child(page, slug_parts)

    def get_root_page_by_slug(self, slug):
        try:
            page = models.Page.objects.get(
                slug=slug, parent=None, is_deleted=False, is_published=True)
        except MultipleObjectsReturned:
            # Something is very wrong. There is most likely a data integrity
            # problem!
            raise
        return page

    def get_content_blocks_for_region(self, region, page):
        block_links = models.ContentBlockLink.objects.filter(region=region, page=page)
        return [block.model_object for block in block_links]

    def get_all_active_root_pages(self):
        return models.Page.objects.filter(is_deleted=False, parent=None)

    def get_page_templates(self):
        return models.PageTemplate.objects.all()

    def get_page_template_by_page(self, page):
        return page.template

    def create_page_template(self, uploaded_file):
        models.PageTemplate.objects.create(template_file=uploaded_file)

    def create_page(self, title, slug, page_template, parent=None, is_published=False):
        models.Page.objects.create(title=title,
                            slug=slug,
                            template=page_template,
                            parent=parent,
                            is_published=is_published)

    def check_slug_conflict(self, slug, parent, page_pk=None):
        """ Tries to find a conflicting slug. If the parent has a child with
            the same proposed slug, return True as there is a conflict
        """
        try:
            page = models.Page.objects.get(parent=parent, slug=slug, is_published=True)
        except models.Page.DoesNotExist:
            return False

        if page_pk and int(page_pk) == page.pk:
            return False
        return True

    def create_new_page(self, title, slug, page_template, parent=None, is_published=False):
        if is_published:
            # Try and get a page that would conflict with this new one first.
            # We don't do this for unpublished pages as there can be mulitple
            # drafts of the same page.
            conflicts = self.check_slug_conflict(slug, parent)
            if conflicts:
                raise PageConflictingSlugException
        self.create_page(title, slug,
                         page_template,
                         parent=parent,
                         is_published=is_published)

    def edit_page(self, page_pk, title, slug, page_template, parent, is_published):
        if is_published:
            conflicts = self.check_slug_conflict(slug, parent, page_pk=page_pk)
            if conflicts:
                raise PageConflictingSlugException
        page = self.get_page_by_pk(page_pk)
        page.title = title
        page.slug = slug
        page.template = page_template
        page.parent = parent
        page.is_published = is_published
        page.save()

    def get_page_by_pk(self, page_pk):
        return models.Page.objects.get(pk=page_pk)

    def get_pages(self):
        return models.Page.objects.filter(is_deleted=False)


class RegionService(object):
    def create_region(self, name, block_name, template):
        models.Region.objects.create(
            name=name, block_name=block_name, template=template)


class ContentBlockService(object):
    def get_allowed_content_blocks(self):
        return [(model[0], ContentType.objects.get_for_model(model[1]).pk) for model in models.REGISTERED_CONTENT_BLOCKS]

    def get_contentblock_model(self, content_type):
        content_type = ContentType.objects.get(pk=content_type)
        model_class = content_type.model_class()
        return model_class

    def create_new_block_from_form(self, form):
        """ This takes a model form and creates the block object.
            This is not done explicitly because the forms are dynamic.
        """
        block_instance = form.save()
        return block_instance

    def link_block(self, block, page_pk, region_pk, block_content_type):
        content_type = ContentType.objects.get(pk=block_content_type)
        page = models.Page.objects.get(pk=page_pk)
        region = models.Region.objects.get(pk=region_pk)
        models.ContentBlockLink.objects.create(page=page,
                                               region=region,
                                               object_id=block.pk,
                                               content_type=content_type,
                                               model_object=block)


# Helper exceptions
class PageConflictingSlugException(Exception):
    pass
