FROM node:22-alpine AS build

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . ./

# Caddy reads this value at runtime to proxy browser requests from /api.
ARG API_UPSTREAM_BASE_URL
ENV API_UPSTREAM_BASE_URL=${API_UPSTREAM_BASE_URL}

RUN pnpm build

FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]