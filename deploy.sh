#!/bin/bash
# deploy.sh — 100% автоматический деплой GoaNest бота в Cloud Run
# Просто: chmod +x deploy.sh && ./deploy.sh

set -e  # Останавливаем скрипт при любой ошибке

echo "Запуск деплоя GoaNest бота в Google Cloud Run..."

# Проверяем, что мы в правильном проекте
CURRENT_PROJECT=$(gcloud config get-value project)
if [ "$CURRENT_PROJECT" != "botolxkvartir" ]; then
  echo "Переключаемся на проект botolxkvartir..."
  gcloud config set project botolxkvartir
fi

# Убедимся, что секрет существует (если нет — создадим)
if ! gcloud secrets describe firebase-credentials >/dev/null 2>&1; then
  echo "Секрет firebase-credentials не найден — создаём..."
  gcloud secrets create firebase-credentials \
    --data-file=./botolxkvartir-firebase-adminsdk-fbsvc-63c5cc654e.json
  echo "Секрет успешно создан!"
else
  echo "Секрет firebase-credentials уже существует"
fi

# Сам деплой — одна большая команда (ВСЁ В ОДНОЙ СТРОКЕ — gcloud так любит)
echo "Запускаем деплой в Cloud Run..."
gcloud run deploy botolxkvartir \
  --source . \
  --region us-east4 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --quiet \
  --set-env-vars=TELEGRAM_BOT_TOKEN=8418832255:AAEw6E4OjFKMseNEYW2KOsBkfRwv_ZCW07I,\
GROK_API_KEY=xai-caIC1K55vaSe1xyeiXjVxHimgzKohPeYGiWqmja1yrFRnygovMktVNFgwxxLudwhcfYy11j0hwXNn8F7,\
OPENAI_API_KEY=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,\
OPENROUTER_API_KEY=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,\
ADMIN_ID=123456789,\
WEBHOOK_BASE_URL=https://botolxkvartir-498789354610.us-east4.run.app,\
FIREBASE_CREDENTIALS_PATH=/secrets/firebase-service-account.json \
  --update-secrets=/secrets/firebase-service-account.json=firebase-credentials:latest

echo "ДЕПЛОЙ УСПЕШНО ЗАВЕРШЁН!"
echo "Твой бот живёт здесь:"
echo "https://botolxkvartir-498789354610.us-east4.run.app"
echo ""
echo "Бот в продакшене"