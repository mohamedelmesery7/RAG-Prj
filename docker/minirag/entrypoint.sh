#!/bin/bash
set -e

echo "Running database migrations..."
# الانتقال للمجلد الذي يحتوي على alembic.ini
cd /app/models/db_shcemas/minirag/

# تنفيذ التهجير
alembic upgrade head

# العودة للمجلد الرئيسي للتطبيق
cd /app

echo "Starting FastAPI..."
# هذا السطر يمرر الأمر CMD من Dockerfile إلى النظام
exec "$@"