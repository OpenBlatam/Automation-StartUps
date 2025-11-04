# Common security configurations

# Actualizar sistema
system_update:
  pkg.upgraded:
    - refresh: true

# Configurar firewall básico (ufw)
configure_ufw:
  cmd.run:
    - name: ufw --force enable
    - unless: "ufw status | grep -q 'Status: active'"

# Permitir SSH
allow_ssh:
  cmd.run:
    - name: ufw allow ssh
    - unless: "ufw status | grep -q '22/tcp'"


