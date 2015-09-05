neo4j_setup:
  cmd.run:
   - name: |
        wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -
        echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
        apt-get update

neo4j:
  pkg:
    - installed

  service:
    - running
    - reload: True
    - watch:
      - pkg: neo4j
      - file: /etc/neo4j/neo4j.properties
      - file: /etc/neo4j/neo4j-server.properties

vagrant:
  group.present:
    - addusers:
      - neo4j
    - require:
      - pkg: neo4j


/etc/neo4j/neo4j.properties:
  file:
    - managed
    - source: salt://neo4j/neo4j.properties
    - user: neo4j
    - group: adm
    - mode: 644

/etc/neo4j/neo4j-server.properties:
  file:
    - managed
    - source: salt://neo4j/neo4j-server.properties
    - user: neo4j
    - group: adm
    - mode: 644