# Common packages installation

common_packages:
  pkg.installed:
    - pkgs: {{ pillar.get('packages', {}).get('common', []) }}
    - refresh: true


