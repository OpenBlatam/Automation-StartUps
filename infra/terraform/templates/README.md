# Terraform Templates

Templates para crear nuevos módulos y configuraciones rápidamente.

## 📁 Templates Disponibles

### Module Template
Plantilla completa para crear módulos reutilizables de Terraform.

**Ubicación:** `templates/module-template/`

**Archivos incluidos:**
- `main.tf` - Recursos principales
- `variables.tf` - Variables del módulo
- `outputs.tf` - Outputs del módulo
- `README.md` - Documentación del módulo

**Uso:**
```bash
cp -r templates/module-template modules/my-new-module
# Editar archivos según necesidad
```

## 🎯 Mejores Prácticas para Módulos

1. **Documentación:**
   - README.md claro y completo
   - Descripciones en variables y outputs
   - Ejemplos de uso

2. **Versionado:**
   - Usar versiones semánticas
   - Tag releases en Git

3. **Testing:**
   - Probar en dev antes de prod
   - Validar con terraform validate
   - Probar con diferentes inputs

4. **Naming:**
   - Nombres descriptivos
   - Convenciones consistentes

5. **Outputs:**
   - Exportar información útil
   - Evitar outputs sensibles innecesarios

## 📚 Crear un Nuevo Módulo

```bash
# 1. Copiar template
cp -r templates/module-template modules/my-module

# 2. Editar archivos
cd modules/my-module
# Editar main.tf, variables.tf, outputs.tf

# 3. Documentar
# Editar README.md con detalles del módulo

# 4. Validar
terraform init
terraform validate

# 5. Probar
# Crear ejemplo de uso
```

## 🔗 Enlaces Útiles

- [Terraform Module Best Practices](https://www.terraform.io/docs/modules/index.html)
- [Module Registry](https://registry.terraform.io/)
- [Module Composition](https://www.terraform.io/docs/modules/composition.html)

