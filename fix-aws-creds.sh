#!/bin/bash

echo "🔑 AWS Credentials Fix Helper"
echo "============================="

echo "📋 Current AWS configuration:"
aws configure list

echo ""
echo "🔍 Checking AWS access..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "✅ AWS credentials are working!"
    aws sts get-caller-identity
    exit 0
else
    echo "❌ AWS credentials are expired or invalid"
fi

echo ""
echo "🛠️  To fix your AWS credentials, choose one option:"
echo ""
echo "1. Get new temporary credentials from AWS Console:"
echo "   - Go to AWS Console → IAM → Users → Your User → Security Credentials"
echo "   - Create new access keys"
echo "   - Update ~/.aws/credentials with new keys"
echo ""
echo "2. Use AWS SSO (if configured):"
echo "   aws sso login --profile your-profile"
echo ""
echo "3. Configure new credentials:"
echo "   aws configure"
echo ""

echo "📝 After fixing your credentials, test with:"
echo "   aws sts get-caller-identity"
echo ""
echo "🚀 Then run the deployment:"
echo "   ./deploy-aws.sh"
