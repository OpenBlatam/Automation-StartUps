docker_repo:
  pkgrepo.managed:
    - name: deb https://download.docker.com/linux/ubuntu {{ grains['oscodename'] }} stable
    - distarch: amd64
    - file: /etc/apt/sources.list.d/docker.list
    - key_url: https://download.docker.com/linux/ubuntu/gpg
    - require_in:
      - pkg: docker_ce

docker_ce:
  pkg.installed:
    - name: docker-ce
    - refresh: True

docker_service:
  service.running:
    - name: docker
    - enable: True
    - require:
      - pkg: docker_ce


