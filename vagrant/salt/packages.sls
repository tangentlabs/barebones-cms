/var/lib/locales/supported.d/local:
  file:
    - managed
    - source: salt://locale
    - user: root
    - group: root

regen_locale:
  cmd.run:
    - name: locale-gen

core:
  pkg.installed:
    - pkgs:
      - postgresql-9.3
      - postgresql-contrib-9.3
      - python-virtualenv
      - postfix
      - python
      - python-dev
      - python-pip
      - vim
      - libpq-dev
      - make
      - memcached
    - refresh: True

