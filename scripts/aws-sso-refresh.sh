#!/bin/bash

# AWS SSO Auto-Refresh Script
# This script automatically refreshes your AWS SSO session

PROFILE="AWSAdministratorAccess-149999906241"

echo "🔄 Refreshing AWS SSO session..."

# Check if we're already logged in
if aws sts get-caller-identity --profile $PROFILE > /dev/null 2>&1; then
    echo "✅ AWS SSO session is still valid"
    aws sts get-caller-identity --profile $PROFILE
else
    echo "🔑 AWS SSO session expired, logging in..."
    aws sso login --profile $PROFILE

    if [ $? -eq 0 ]; then
        echo "✅ Successfully logged in to AWS SSO"
        aws sts get-caller-identity --profile $PROFILE
    else
        echo "❌ Failed to login to AWS SSO"
        exit 1
    fi
fi

echo "🚀 Ready to use AWS CLI and Terraform!"
