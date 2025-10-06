#!/bin/bash

# Get AWS credentials from SSO and export them as environment variables
# This script works around Terraform's SSO issues

PROFILE="AWSAdministratorAccess-149999906241"

echo "🔑 Getting AWS credentials from SSO..."

# Check if we're logged in
if ! aws sts get-caller-identity --profile $PROFILE > /dev/null 2>&1; then
    echo "🔐 SSO session expired, logging in..."
    aws sso login --profile $PROFILE
fi

# Get the credentials
CREDS=$(aws configure export-credentials --profile $PROFILE --format env)

if [ $? -eq 0 ]; then
    echo "✅ Successfully retrieved AWS credentials"
    echo "$CREDS"
    echo ""
    echo "🚀 To use these credentials with Terraform, run:"
    echo "eval \"\$($0)\""
    echo "terraform plan -var-file=dev.tfvars"
else
    echo "❌ Failed to get AWS credentials"
    exit 1
fi
