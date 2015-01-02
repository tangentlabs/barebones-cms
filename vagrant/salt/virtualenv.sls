cms_env:
  file.directory:
    - name: /cms_virtualenv
    - user: vagrant
    - group: vagrant
    - recurse:
      - user
      - group
      - mode

/cms_virtualenv:
  virtualenv.managed:
    - use_wheel : False
    - system_site_packages: False
    - requirements: /var/www/requirements.txt
    - user: vagrant

