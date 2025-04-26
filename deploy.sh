#!/bin/bash

# === CONFIGURATION ===
PROJECT_ID="round-kit-450201-r9"        # ⬅️ Update this
SERVICE_NAME="frono-automation"         # ⬅️ Update this
REGION="asia-south1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# === STEP 1: Build Docker Image ===
echo "🔧 Building Docker image..."
gcloud builds submit --tag "$IMAGE_NAME"

# === STEP 2: Deploy to Cloud Run (env vars already set in Cloud UI) ===
echo "🚀 Deploying to Cloud Run..."
# gcloud run deploy "$SERVICE_NAME" \
#   --image "$IMAGE_NAME" \
#   --platform managed \
#   --region "$REGION" \
#   --allow-unauthenticated \
#   --memory 1Gi \
#   --timeout 900

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_NAME" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 900 \
  --service-account mis1-178@round-kit-450201-r9.iam.gserviceaccount.com
