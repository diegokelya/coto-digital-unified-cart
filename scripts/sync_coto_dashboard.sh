#!/bin/bash
# Wrapper para sincronizar dashboard de Coto Digital en Home Assistant
# Carga variables de entorno de Hermes antes de ejecutar el sincronizador

# Cargar variables de entorno de Hermes
if [ -f "$HOME/.hermes/.env" ]; then
    set -a
    source "$HOME/.hermes/.env"
    set +a
fi

# Ejecutar sincronizador
exec node "$HOME/.hermes/scripts/sync_coto_dashboard.mjs"
