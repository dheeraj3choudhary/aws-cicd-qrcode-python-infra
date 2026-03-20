#!/usr/bin/env bash
set -euo pipefail

echo "=== AfterInstall: pulling latest Docker image from ECR ==="

# Use IMDSv2 to get region
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
AWS_REGION=$(curl -s -H "X-aws-ec2-metadata-token: ${TOKEN}" \
  http://169.254.169.254/latest/meta-data/placement/region)

ACCOUNT_ID=$(aws sts get-caller-identity --region "${AWS_REGION}" --query Account --output text)
ECR_REPO_URI=$(aws ssm get-parameter \
  --name /qrcode/ecr/repo-uri \
  --region "${AWS_REGION}" \
  --query Parameter.Value \
  --output text)

echo "Region       : ${AWS_REGION}"
echo "Account      : ${ACCOUNT_ID}"
echo "ECR Repo URI : ${ECR_REPO_URI}"

echo "=== Logging in to ECR ==="
aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin "${ECR_REPO_URI}"

echo "=== Pulling image ==="
docker pull "${ECR_REPO_URI}:latest"

echo "=== Writing env file ==="
mkdir -p /opt/qrcode
cat > /opt/qrcode/.env << ENVEOF
ECR_REPO_URI=${ECR_REPO_URI}
AWS_REGION=${AWS_REGION}
ENVEOF

echo "=== AfterInstall complete ==="