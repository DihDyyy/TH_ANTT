set -e
set -x
npm install --no-audit --no-fund --fetch-retries=0 --fetch-timeout=15000
npm run build
