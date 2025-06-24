# frontend/Dockerfile

# Imagen base de Node.js
FROM node:22-alpine AS base

# Instalar dependencias solo cuando sea necesario
FROM base AS deps
# Verificar https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine para entender por qué se necesita libc6-compat.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Instalar dependencias basándose en el gestor de paquetes preferido
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild el código fuente solo cuando sea necesario
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Variables de entorno para la build
ENV NEXT_PUBLIC_API_URL=http://localhost:8000/api
ENV NODE_ENV=production

# Generar la aplicación
RUN npm run build

# Imagen de producción, copiar todos los archivos y ejecutar next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
# Deshabilitar telemetría durante el runtime.
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Aprovechar los outputs traces para reducir el tamaño de imagen
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

# Comando por defecto para producción con standalone
CMD ["node", "server.js"]