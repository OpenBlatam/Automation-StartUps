# Multi-stage build for AI Marketing SaaS Platform
FROM node:18-alpine AS base

# Install dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Development stage
FROM base AS development

ENV NODE_ENV=development

# Copy application files
COPY . .

EXPOSE 5000

CMD ["node", "server.js"]

# Production stage
FROM base AS production

ENV NODE_ENV=production

# Copy application files
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Create necessary directories
RUN mkdir -p logs uploads && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]

# Start orchestrator in background
COPY --from=base /app/system_orchestrator.js /app/system_orchestrator.js
CMD ["sh", "-c", "node system_orchestrator.js & node server.js"]
