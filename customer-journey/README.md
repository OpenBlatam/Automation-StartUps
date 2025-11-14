# Customer Journey Mapper

Una aplicación web moderna para mapear el customer journey completo desde el primer contacto hasta la compra, incluyendo todos los touchpoints, necesidades de contenido y triggers de automatización.

## Características

- 🎯 **Gestión de Buyer Personas**: Crea y gestiona múltiples buyer personas con sus características, pain points y objetivos
- 🗺️ **Mapeo Visual del Journey**: Visualiza el journey completo con todas sus etapas
- 📍 **Touchpoints**: Define puntos de contacto en cada etapa del journey
- ⚡ **Automatizaciones**: Configura triggers de automatización para cada etapa
- 📝 **Necesidades de Contenido**: Identifica qué contenido se necesita en cada etapa
- 💾 **Exportación**: Exporta el journey completo en formato JSON

## Tecnologías

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide React (iconos)

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Estructura del Proyecto

```
customer-journey/
├── src/
│   ├── components/
│   │   ├── ui/          # Componentes UI base (Button, Card, Input, etc.)
│   │   ├── BuyerPersonaSelector.tsx
│   │   ├── JourneyStage.tsx
│   │   └── JourneyVisualization.tsx
│   ├── types/
│   │   └── journey.ts   # Tipos TypeScript
│   ├── lib/
│   │   └── utils.ts     # Utilidades
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tailwind.config.ts
└── vite.config.ts
```

## Uso

1. **Crear Buyer Persona**: Haz clic en "Nueva Persona" y completa la información
2. **Seleccionar Persona**: Selecciona un buyer persona para comenzar a mapear su journey
3. **Definir Etapas**: Cada journey incluye 4 etapas por defecto (Awareness, Consideration, Decision, Purchase)
4. **Agregar Touchpoints**: Para cada etapa, agrega los puntos de contacto con el cliente
5. **Configurar Automatizaciones**: Define triggers que activarán acciones automáticas
6. **Especificar Contenido**: Indica qué contenido se necesita en cada etapa
7. **Visualizar**: Cambia a la vista de visualización para ver el journey completo
8. **Exportar**: Descarga el journey en formato JSON

## Etapas del Journey

- **Awareness**: El cliente descubre tu marca o producto
- **Consideration**: El cliente evalúa opciones y compara soluciones
- **Decision**: El cliente está listo para tomar una decisión de compra
- **Purchase**: El cliente completa la compra




