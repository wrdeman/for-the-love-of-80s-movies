/etc/supervisor/conf.d/website_gunicorn.conf:
  file:
    - managed
    - create: True
    - source: salt://website/supervisord.conf
    - template: jinja
    - require_in:
      - supervisored_gunicorn
    - require:
      - pkg: supervisor

{{ pillar ['website_gunicorn_conf_path'] }}:
  file:
    - managed
    - source: salt://website/gunicorn.conf.py
    - user: vagrant
    - group: vagrant
    - require_in:
      - supervisored_gunicorn

supervisor:
  pkg:
    - installed

gunicorn:
  pip.installed:
    #- name: gunicorn
    - bin_env: {{ pillar ['website_venv_bin'] }}
    #- cmd: /home/vagrant/venv/bin
    - require:
      - pkg: python-pip

supervisored_gunicorn:
  supervisord:
    - running
    - name: website_gunicorn
    - update: True
    - restart: True
    - watch:
      - file: /etc/supervisor/conf.d/website_gunicorn.conf
      - file: /home/vagrant/gunicorn.conf.py
    - require:
      - pkg: supervisor
      - pip: gunicorn