Barebones CMS
=============

This is a very simple project to create the boilerplace
for a service orientated CMS.

It is not meant to be a complete CMS solution, just the base
for projects to use when the project does not want or need
something as complete as DjangoCMS.

Issues should be tracked on Mantis, though issues that are ***not***
to do with the basic CMS should be tracked against the project that
extended things.


Getting Started
---------------

To use the CMS you should perform the following steps:

 - Update your requirements to include the barebone-cms project


Local Development
-----------------

If you'd like to make changes but don't have the CMS in your own project, you
can use the development project in the sites directory. It is a basic django
project intended to do nothing except give a face to the CMS structure.

Vagrant
'''''''

If you want to use vagrant for development, there is a complete vagrant + salt
setup:

  cd vagrant

  vagrant up

  vagrant ssh

  make install

Docker
''''''

There is no docker file at the moment. If you want to create one then please
feel free to do so and make a pull request.
It can use any DB as the project is not database reliant.


Structure
---------

Pages
'''''

Pages contain information about the page itself. It does not contain any
information that is not useful for routing or whether or not the page is
published (with the exception of title).

Page Templates
''''''''''''''

Page templates have two functions:

 - To tell the user where

Settings
---------
BB_CMS_APP_NAME - name of override app
BB_DASHBOARD_NAMESPACE - dashboard namespace to use for cms management pages
