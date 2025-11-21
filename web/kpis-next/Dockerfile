# syntax=docker/dockerfile:1

FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci && npm cache clean --force

FROM node:20-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY package*.json ./
COPY next.config.js ./
COPY public ./public
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD node -e "process.exit(0)"
CMD ["npm", "run", "start"]




