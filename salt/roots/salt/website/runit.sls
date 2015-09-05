runit:
  pkg:
    - installed

/etc/sv/site:
  file.directory:
    - mode: 0755
    - user: vagrant
    - group: vagrant
    - recurse:
      - user
      - group
      - mode
    - require:
      - pkg: runit


/etc/sv/site/run:
  file:
    - managed
    - create: True
    - makedirs: True
    - source: salt://website/runit.conf
    - user: vagrant
    - group: vagrant
    - mode: 0775
    - template: jinja
    - require:
      - pkg: runit

{{ pillar ['website_gunicorn_conf_path'] }}:
  file:
    - managed
    - source: salt://website/gunicorn.conf.py
    - user: vagrant
    - group: vagrant
    - require_in:
      - supervisored_gunicorn

gunicorn:
  pip.installed:
    #- name: gunicorn
    - bin_env: {{ pillar ['website_venv_bin'] }}
    #- cmd: /home/vagrant/venv/bin
    - require:
      - pkg: python-pip

#supervisored_gunicorn:
#  supervisord:
#    - running
#    - name: website_gunicorn
#    - update: True
#    - restart: True
#    - watch:
#      - file: /etc/supervisor/conf.d/website_gunicorn.conf
#      - file: /home/vagrant/gunicorn.conf.py
#    - require:
#      - pkg: supervisor
#      - pip: gunicorn
