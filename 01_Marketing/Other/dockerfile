# Multi-stage build para optimización
FROM node:18-alpine AS base

# Instalar dependencias del sistema
RUN apk add --no-cache \
    curl \
    dumb-init \
    && rm -rf /var/cache/apk/*

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S feedback -u 1001

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
COPY tsconfig.json ./

# Instalar dependencias
RUN npm ci --only=production && npm cache clean --force

# Etapa de build
FROM base AS builder

# Instalar dependencias de desarrollo
RUN npm ci

# Copiar código fuente
COPY src/ ./src/

# Build de TypeScript
RUN npm run build

# Etapa de producción
FROM base AS production

# Copiar archivos de producción
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Crear directorios necesarios
RUN mkdir -p logs uploads && \
    chown -R feedback:nodejs /app

# Cambiar a usuario no-root
USER feedback

# Exponer puerto
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Comando de inicio
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/server.js"]

# Etapa para worker
FROM production AS worker

# Comando para worker
CMD ["node", "dist/worker.js"]

# Etapa para desarrollo
FROM base AS development

# Instalar dependencias de desarrollo
RUN npm ci

# Copiar código fuente
COPY . .

# Cambiar a usuario no-root
USER feedback

# Exponer puerto
EXPOSE 3001

# Comando de desarrollo
CMD ["npm", "run", "dev"]