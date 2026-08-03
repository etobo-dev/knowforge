#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_CONFIG="${ROOT}/config/project.json"

AWS_REGION="${AWS_REGION:-$(jq -r '.aws.region' "${PROJECT_CONFIG}")}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REPOSITORY="${ECR_REPOSITORY:-$(jq -r '.back.ecr_repository' "${PROJECT_CONFIG}")}"
LAMBDA_FUNCTION_NAME="${LAMBDA_FUNCTION_NAME:-$(jq -r '.back.lambda_name' "${PROJECT_CONFIG}")}"

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_IMAGE="${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"

cd "$ROOT/back"

echo "==> ecr login"
aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

echo "==> build and push ${ECR_IMAGE}"
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --push \
  -t "${ECR_IMAGE}" \
  .

echo "==> update lambda ${LAMBDA_FUNCTION_NAME}"
aws lambda update-function-code \
  --function-name "${LAMBDA_FUNCTION_NAME}" \
  --image-uri "${ECR_IMAGE}" \
  --region "${AWS_REGION}" \
  >/dev/null

aws lambda wait function-updated \
  --function-name "${LAMBDA_FUNCTION_NAME}" \
  --region "${AWS_REGION}"

echo "==> deploy complete"
