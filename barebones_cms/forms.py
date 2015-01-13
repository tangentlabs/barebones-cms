from django import forms
from django.forms.models import modelform_factory

from barebones_cms.services import PageService


class PageForm(forms.Form):
    title = forms.CharField(max_length=255)
    slug = forms.CharField(max_length=255)
    page_template = forms.ModelChoiceField(queryset=None)
    parent = forms.ModelChoiceField(queryset=None, required=False)
    is_published = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['page_template'].queryset = self.get_page_template_queryset()
        self.fields['parent'].queryset = self.get_page_parent_queryset()

    def get_page_template_queryset(self):
        return PageService().get_page_templates()

    def get_page_parent_queryset(self):
        return PageService().get_pages()


class PageTemplateForm(forms.Form):
    template_file = forms.FileField(max_length=255)


class RegionForm(forms.Form):
    name = forms.CharField(max_length=255)
    block_name = forms.CharField(max_length=255)
    page_template = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super(RegionForm, self).__init__(*args, **kwargs)
        self.fields['page_template'].queryset = self.get_page_template_queryset()

    def get_page_template_queryset(self):
        return PageService().get_page_templates()


# This is used for creating model forms from the content blocks
def get_modelform(model):
    modelform_class = modelform_factory(model)
    return modelform_class
