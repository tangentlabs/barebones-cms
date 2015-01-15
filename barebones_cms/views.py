from django.views.generic import View, TemplateView, FormView
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader, Context

from barebones_cms.services import (
    PageService, RegionService, ContentBlockService, URLService)
from barebones_cms import forms


class ServeCMSPageView(View):
    def dispatch(self, request, *args, **kwargs):
        service = PageService()
        page = service.get_page_from_path(request.path)
        if not page:
            raise Http404

        context = {'page': page}
        for region in page.page_template.region_set.all():
            content_blocks = service.get_content_blocks_for_region(region, page)
            rendered_blocks = []
            for block in content_blocks:
                block_template = loader.get_template(block.partial.path)
                block_context = {'content_block': block}
                block_context.update(context)
                rendered_blocks.append(block_template.render(Context(block_context)))
            context[region.block_name] = {'content_blocks': rendered_blocks}

        return render(request, page.page_template.template_file.path, context)


class DashboardPagesView(TemplateView):
    template_name = 'dashboard/cms/pages_index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(DashboardPagesView, self).get_context_data(*args, **kwargs)
        service = PageService()
        root_pages = service.get_all_active_root_pages()

        page_tree = {}
        for page in root_pages:
            page_tree[page] = page.get_descendants()

        context['page_tree'] = page_tree
        context['page_tree_rendered'] = ''
        for page in root_pages:
            context['page_tree_rendered'] += self.get_page_render(page)

        return context

    def get_page_render(self, page):
        edit_url = URLService().get_page_edit_url(page.pk)
        page_html = '<ul>'
        if page.is_leaf_node():
            page_html += "<li><a href='%s'>%s</a></li>" % (
                edit_url, page.slug)
        else:
            page_html += "<li><a href='%s'>%s</a></li><ul>%s</ul>" % (
                edit_url, page.slug, self.get_tree_render(page.children.all()))
        page_html += '</ul>'
        return page_html

    def get_tree_render(self, pages):
        page_html = ''
        for page in pages:
            edit_url = URLService().get_page_edit_url(page.pk)
            if page.is_leaf_node():
                page_html += "<li><a href='%s'>%s</a></li>" % (
                    edit_url, page.slug)
            else:
                page_html = "<li><a href='%s'>%s</a></li><ul>%s</ul>" % (
                    edit_url, page.slug, self.get_tree_render(page.children.all()))
        return page_html


class DashboardPageCreateView(FormView):
    template_name = 'dashboard/cms/pages_create.html'
    form_class = forms.PageForm

    def form_valid(self, form):
        PageService().create_new_page(**form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return URLService().get_page_index_url()


class DashboardPageTemplateCreateView(FormView):
    template_name = 'dashboard/cms/page_template_create.html'
    form_class = forms.PageTemplateForm

    def form_valid(self, form):
        PageService().create_page_template(self.request.FILES['template_file'])
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return URLService().get_page_create_url()


class DashboardPageEditView(FormView):
    template_name = 'dashboard/cms/pages_edit.html'
    form_class = forms.PageForm

    def dispatch(self, request, *args, **kwargs):
        self.object = PageService().get_page_by_pk(self.kwargs['pk'])
        return super(DashboardPageEditView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return PageService().get_page_fields_as_dict(self.object)

    def get_context_data(self, *args, **kwargs):
        context = super(DashboardPageEditView, self).get_context_data(*args, **kwargs)

        service = PageService()
        page_template = service.get_page_template_by_page(self.object)

        context['page'] = self.object
        context['page_template'] = page_template
        region_context = {}
        for region in self.object.page_template.region_set.all():
            content_blocks = service.get_content_blocks_for_region(region, self.object)
            region_context[region] = content_blocks
        context['regions'] = region_context
        context['allowed_content_blocks'] = ContentBlockService().get_allowed_content_blocks()
        return context

    def form_valid(self, form):
        PageService().edit_page(self.kwargs['pk'], **form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return URLService().get_page_index_url()


class DashboardTemplateRegionCreateView(FormView):
    template_name = 'dashboard/cms/region_create.html'
    form_class = forms.RegionForm

    def get_context_data(self, *args, **kwargs):
        context = super(DashboardTemplateRegionCreateView, self).get_context_data(*args, **kwargs)
        context.update(self.kwargs)
        return context

    def get_initial(self, *args, **kwargs):
        return {'page_template': self.kwargs['template']}

    def form_valid(self, form):
        RegionService().create_region(form.cleaned_data['name'],
                                      form.cleaned_data['block_name'],
                                      form.cleaned_data['page_template'])
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return URLService().get_page_edit_url(int(self.kwargs['page']))


class DashboardContentBlockCreateView(TemplateView):
    template_name = 'dashboard/cms/contentblock_create.html'

    def post(self, request, *args, **kwargs):
        # Do some form validation
        form_class = self.get_form_class()
        form = form_class(request.POST, request.FILES)
        form_valid = form.is_valid()
        if form_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(DashboardContentBlockCreateView, self).get_context_data(*args, **kwargs)
        context.update(self.kwargs)

        if 'form' in kwargs.keys():
            form = kwargs['form']
        else:
            form = self.get_form_class()()
        context['form'] = form
        return context

    def get_form_class(self):
        contentblock_model = ContentBlockService().get_contentblock_model(
            self.kwargs['content_type'])
        form_class = forms.get_modelform(contentblock_model)
        return form_class

    def form_valid(self, form):
        service = ContentBlockService()
        block = service.create_new_block_from_form(form)
        service.link_block(
            block,
            self.kwargs['page'],
            self.kwargs['region'],
            self.kwargs['content_type'])

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return URLService().get_page_edit_url(int(self.kwargs['page']))
