#!/bin/bash

# CoPipes Codespace setup script
# Runs once after the dev container is created.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[*] Setting up CoPipes development environment..."

chmod +x "$ROOT_DIR/start.sh"

# ── Codespace-specific URL patching ────────────────────────────────────────
# NEXT_PUBLIC_* vars are embedded in client-side JavaScript, so they must
# point to the public Codespace URLs, not internal Docker hostnames.
if [ -n "$CODESPACE_NAME" ]; then
    echo "[*] GitHub Codespace detected: $CODESPACE_NAME"

    DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    SUPABASE_URL="https://${CODESPACE_NAME}-8001.${DOMAIN}"
    API_URL="https://${CODESPACE_NAME}-8000.${DOMAIN}"
    FRONTEND_URL="https://${CODESPACE_NAME}-3000.${DOMAIN}"

    echo "[*] Patching service URLs..."

    # Main .env – public-facing URLs used by browser-side code
    sed -i "s|NEXT_PUBLIC_SUPABASE_URL=.*|NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}|" "$ROOT_DIR/.env"
    sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=${API_URL}|" "$ROOT_DIR/.env"
    sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=${FRONTEND_URL}|" "$ROOT_DIR/.env"

    # supabase/.env – needed for auth redirects and Supabase Studio
    sed -i "s|SUPABASE_PUBLIC_URL=.*|SUPABASE_PUBLIC_URL=${SUPABASE_URL}|" "$ROOT_DIR/supabase/.env"
    sed -i "s|API_EXTERNAL_URL=.*|API_EXTERNAL_URL=${SUPABASE_URL}|" "$ROOT_DIR/supabase/.env"
    sed -i "s|SITE_URL=.*|SITE_URL=${FRONTEND_URL}|" "$ROOT_DIR/supabase/.env"

    echo "[+] URLs configured:"
    echo "    Frontend:  ${FRONTEND_URL}"
    echo "    FastAPI:   ${API_URL}"
    echo "    Supabase:  ${SUPABASE_URL}"
    echo ""
fi

echo "[+] Setup complete. Starting services..."
echo ""
"$ROOT_DIR/start.sh" up
