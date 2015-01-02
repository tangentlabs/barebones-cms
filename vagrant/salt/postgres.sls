template1_remove:
  cmd.script:
    - user: postgres
    - name: salt://remove_template.sh
    - shell: /bin/bash

template1_create:
  postgres_database:
    - present
    - name: template1
    - encoding: UTF8
    - lc_collate: en_GB.UTF8
    - lc_ctype: en_GB.UTF8
    - template: template0
    - runas: postgres

cms_user:
  postgres_user.present:
    - name: cms_vagrant
    - password: vagrant
    - createdb: true
    - runas: postgres
    - superuser: true

cms_db:
  postgres_database:
    - present
    - name: cms_vagrant
    - encoding: UTF8
    - lc_collate: en_GB.UTF8
    - lc_ctype: en_GB.UTF8
    - template: template1
    - runas: postgres
