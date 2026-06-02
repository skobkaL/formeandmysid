#!/bin/bash
set -e

# Применение миграций
python manage.py migrate --noinput

# Создание суперпользователя если нет пользователей
if [ "$(python manage.py shell -c "from apps.accounts.models import CustomUser; print(CustomUser.objects.count())")" -eq "0" ]; then
    echo "from apps.accounts.models import CustomUser; CustomUser.objects.create_superuser('admin', 'admin@builder.local', 'admin123')" | python manage.py shell
    echo "✅ Создан суперпользователь: admin / admin123"
fi

# Запуск сервера
exec gunicorn sid_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -