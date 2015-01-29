from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_model
from django.forms import model_to_dict

from barebones_cms.models import REGISTERED_CONTENT_BLOCKS


# Allow the cms app to be completely overridden with another namespace
CMS_APP = getattr(settings, 'BB_CMS_APP_NAME', 'apps.cms').split('.')[-1]
# Allow url namespacing for the dashboard
DASHBOARD_NAMESPACE = getattr(settings, 'BB_DASHBOARD_NAMESPACE', None)


# Import models using get_model so we get the right ones
Page = get_model(CMS_APP, 'Page')
PageTemplate = get_model(CMS_APP, 'PageTemplate')
Region = get_model(CMS_APP, 'Region')
ContentBlockLink = get_model(CMS_APP, 'ContentBlockLink')


class PageService(object):
    def get_page_from_path(self, path):
        # Get rid of leading and ending slashes. Then split the path into parts
        parts = path.lstrip('/').rstrip('/').split('/')

        # Get the root page for the path
        try:
            root_page = self.get_root_page_by_slug(parts.pop(0))
        except (Page.DoesNotExist, MultipleObjectsReturned):
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
        except (Page.DoesNotExist, MultipleObjectsReturned):
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
            page = Page.objects.get(
                slug=slug, parent=None, is_deleted=False, is_published=True)
        except MultipleObjectsReturned:
            # Something is very wrong. There is most likely a data integrity
            # problem!
            raise
        return page

    def get_content_blocks_for_region(self, region, page):
        block_links = ContentBlockLink.objects.filter(region=region, page=page)
        return [block.model_object for block in block_links]

    def get_content_blocks_info_for_region(self, region, page):
        block_links = ContentBlockLink.objects.filter(region=region, page=page)
        region_blocks = []
        for block in block_links:
            block_dict = {
                'model_object': block.model_object,
                'content_type': block.content_type.pk}
            region_blocks.append(block_dict)
        return region_blocks

    def get_all_active_root_pages(self):
        return Page.objects.filter(is_deleted=False, parent=None)

    def get_page_templates(self):
        return PageTemplate.objects.all()

    def get_page_template_by_page(self, page):
        return page.page_template

    def get_page_template_by_pk(self, pk):
        return PageTemplate.objects.get(pk=pk)

    def create_page_template(self, name, template_file, **extra_fields):
        return PageTemplate.objects.create(
            name=name, template_file=template_file, **extra_fields)

    def edit_page_template(self, template_pk, **fields_to_update):
        page_template = self.get_page_template_by_pk(template_pk)
        for field_name, value in fields_to_update.iteritems():
            setattr(page_template, field_name, value)
        page_template.save()
        return page_template

    def create_page(self, title, slug, page_template, parent=None,
                    is_published=False, **extra_fields):
        return Page.objects.create(title=title,
                                   slug=slug,
                                   page_template=page_template,
                                   parent=parent,
                                   is_published=is_published,
                                   **extra_fields)

    def check_slug_conflict(self, slug, parent, page_pk=None):
        """ Tries to find a conflicting slug. If the parent has a child with
            the same proposed slug, return True as there is a conflict
        """
        try:
            page = Page.objects.get(parent=parent, slug=slug, is_published=True)
        except Page.DoesNotExist:
            return False

        if page_pk and int(page_pk) == page.pk:
            return False
        return True

    def create_new_page(self, title, slug, page_template, parent=None,
                        is_published=False, **extra_fields):
        if is_published:
            # Try and get a page that would conflict with this new one first.
            # We don't do this for unpublished pages as there can be mulitple
            # drafts of the same page.
            conflicts = self.check_slug_conflict(slug, parent)
            if conflicts:
                raise PageConflictingSlugException
        return self.create_page(title, slug,
                                page_template,
                                parent=parent,
                                is_published=is_published,
                                **extra_fields)

    def edit_page(self, page_pk, **fields_to_update):
        page = self.get_page_by_pk(page_pk)
        is_published = fields_to_update.get('is_published', page.is_published)
        slug = fields_to_update.get('slug', page.slug)
        parent = fields_to_update.get('parent', page.parent)
        if is_published:
            conflicts = self.check_slug_conflict(slug, parent, page_pk=page_pk)
            if conflicts:
                raise PageConflictingSlugException
        for field_name, value in fields_to_update.iteritems():
            setattr(page, field_name, value)
        page.save()
        return page

    def get_page_by_pk(self, page_pk):
        return Page.objects.get(pk=page_pk)

    def get_pages(self):
        return Page.objects.filter(is_deleted=False)

    def get_page_fields_as_dict(self, page):
        return model_to_dict(page)

    def get_page_template_fields_as_dict(self, page_template):
        return model_to_dict(page_template)


class RegionService(object):
    def create_region(self, name, block_name, template, **extra_fields):
        Region.objects.create(
            name=name, block_name=block_name, template=template, **extra_fields)

    def get_regions_for_page(self, page):
        return page.page_template.region_set.all()


class ContentBlockService(object):
    def get_allowed_content_blocks(self):
        return [(model[0], ContentType.objects.get_for_model(model[1]).pk) for model in REGISTERED_CONTENT_BLOCKS]

    def get_model_content_type(self, model):
        return ContentType.objects.get_for_model(model).pk

    def get_contentblock_model(self, content_type):
        content_type = ContentType.objects.get(pk=content_type)
        model_class = content_type.model_class()
        return model_class

    def get_contentblock_by_pk(self, pk, model_class):
        return model_class.objects.get(pk=pk)

    def save_block_from_form(self, form):
        """ This takes a model form and creates the block object.
            This is not done explicitly because the forms are dynamic.
        """
        block_instance = form.save()
        return block_instance

    def link_block(self, block, page_pk, region_pk, block_content_type):
        content_type = ContentType.objects.get(pk=block_content_type)
        page = Page.objects.get(pk=page_pk)
        region = Region.objects.get(pk=region_pk)
        ContentBlockLink.objects.create(page=page,
                                        region=region,
                                        object_id=block.pk,
                                        content_type=content_type,
                                        model_object=block)

    def relink_block(self, block, page_pk, region_pk, block_content_type):
        content_type = ContentType.objects.get(pk=block_content_type)
        page = Page.objects.get(pk=page_pk)
        region = Region.objects.get(pk=region_pk)
        content_block_link = ContentBlockLink.objects.get(object_id=block.pk)
        return content_block_link


class URLService(object):
    def get_page_edit_url(self, pk):
        default_name = 'edit-page'
        if DASHBOARD_NAMESPACE is None:
            return reverse_lazy(default_name, kwargs={'pk': pk})
        return reverse_lazy(DASHBOARD_NAMESPACE + ':' + default_name,
                            kwargs={'pk': pk})

    def get_page_create_url(self):
        default_name = 'create-page'
        if DASHBOARD_NAMESPACE is None:
            return reverse_lazy(default_name)
        return reverse_lazy(DASHBOARD_NAMESPACE + ':' + default_name)

    def get_page_index_url(self):
        default_name = 'pages-index'
        if DASHBOARD_NAMESPACE is None:
            return reverse_lazy(default_name)
        return reverse_lazy(DASHBOARD_NAMESPACE + ':' + default_name)

    def get_page_template_index_url(self):
        default_name = 'page-template-index'
        if DASHBOARD_NAMESPACE is None:
            return reverse_lazy(default_name)
        return reverse_lazy(DASHBOARD_NAMESPACE + ':' + default_name)


# Helper exceptions
class PageConflictingSlugException(Exception):
    pass
