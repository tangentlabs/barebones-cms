from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from barebones_cms import views


urlpatterns = patterns('',
    url('^dashboard/cms/pages/$', views.DashboardPagesView.as_view(), name="pages-index"),
    url('^dashboard/cms/pages/create/', views.DashboardPageCreateView.as_view(), name="create-page"),
    url('^dashboard/cms/pages/edit/(?P<pk>\d+)/', views.DashboardPageEditView.as_view(), name="edit-page"),
    url('^dashboard/cms/page-template/create/', views.DashboardPageTemplateCreateView.as_view(), name="create-page-template"),
    url('^dashboard/cms/template-region/create/$', views.DashboardTemplateRegionCreateView.as_view(), name="create-template-region"),
    url('^dashboard/cms/template-region/create/(?P<page>\d+)/(?P<template>\d+)/$', views.DashboardTemplateRegionCreateView.as_view(), name="create-template-region-for-page"),
    url('^dashboard/cms/content-block/create/(?P<page>\d+)/(?P<region>\d+)/(?P<content_type>\d+)/', views.DashboardContentBlockCreateView.as_view(), name="create-content-block"),
    url(r'^((?:[\w\-]+/)*)$', views.ServeCMSPageView.as_view()),
)
