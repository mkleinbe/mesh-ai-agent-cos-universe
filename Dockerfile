# syntax=docker/dockerfile:1.7
ARG NODE_IMAGE=node:24.18.0-bookworm-slim
FROM ${NODE_IMAGE} AS build
WORKDIR /build
COPY mcp/package.json mcp/package-lock.json ./mcp/
RUN cd mcp && npm ci
COPY mcp/tsconfig.json ./mcp/tsconfig.json
COPY mcp/src ./mcp/src
RUN cd mcp && npm run build && npm prune --omit=dev

FROM ${NODE_IMAGE} AS runtime
ARG VCS_REF=unknown
ARG BUILD_DATE=unknown
ARG IMAGE_VERSION=4.0.0-qnap-candidate
LABEL org.opencontainers.image.title="mesh-cos-mcp" org.opencontainers.image.version="${IMAGE_VERSION}" org.opencontainers.image.revision="${VCS_REF}" org.opencontainers.image.created="${BUILD_DATE}" org.opencontainers.image.source="https://github.com/mkleinbe/mesh-ai-agent-cos-universe"
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates && rm -rf /var/lib/apt/lists/* && groupadd --gid 65532 mesh && useradd --uid 65532 --gid 65532 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin mesh
WORKDIR /opt/mesh
COPY --chown=65532:65532 pyproject.toml ./
COPY --chown=65532:65532 agents ./agents
COPY --chown=65532:65532 chatgpt ./chatgpt
COPY --chown=65532:65532 config ./config
COPY --chown=65532:65532 contracts ./contracts
COPY --chown=65532:65532 src ./src
COPY --chown=65532:65532 deployment/qnap/runtime_preflight.py ./deployment/qnap/runtime_preflight.py
COPY --chown=65532:65532 deployment/qnap/sqlite_backup.py ./deployment/qnap/sqlite_backup.py
COPY --from=build --chown=65532:65532 /build/mcp/dist ./mcp/dist
COPY --from=build --chown=65532:65532 /build/mcp/node_modules ./mcp/node_modules
ENV NODE_ENV=production PYTHONPATH=/opt/mesh/src PYTHONDONTWRITEBYTECODE=1 MESH_COS_PYTHON_BIN=python3 MCP_BIND_HOST=0.0.0.0 MCP_PORT=8080 HOME=/tmp
USER 65532:65532
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 CMD ["node","-e","fetch('http://127.0.0.1:'+(process.env.MCP_PORT||'8080')+'/healthz').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"]
CMD ["node","mcp/dist/remote.js"]
