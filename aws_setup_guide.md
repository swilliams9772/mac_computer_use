# 🚀 AWS Claude Sonnet 4 Setup Guide

Your codebase already supports AWS Claude Sonnet 4! Here's how to set it up:

## 📋 Prerequisites

1. **AWS Account** with access to Amazon Bedrock
2. **Claude 4 Model Access** enabled in Bedrock
3. **AWS CLI** installed and configured
4. **Proper IAM permissions** for Bedrock

## 🔧 Step 1: Install and Configure AWS CLI

### Install AWS CLI
```bash
# macOS with Homebrew
brew install awscli

# Or download from AWS
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Configure AWS Credentials
```bash
# Option 1: Interactive configuration (recommended)
aws configure

# You'll be prompted for:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]  
# Default region name: us-east-1 (or your preferred region)
# Default output format: json
```

### Alternative Credential Methods
```bash
# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
export AWS_DEFAULT_REGION=us-east-1

# Option 3: AWS Profile
aws configure --profile claude-bedrock
export AWS_PROFILE=claude-bedrock
```

### Verify AWS Configuration
```bash
# Test your credentials
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

## 🏗️ Step 2: Enable Claude 4 Model Access in Bedrock

### Via AWS Console
1. Open [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model Access** in the left sidebar
3. Click **Request model access**
4. Find and enable these Claude 4 models:
   - ✅ **Claude Opus 4** (`anthropic.claude-opus-4-20250514-v1:0`)
   - ✅ **Claude Sonnet 4** (`anthropic.claude-sonnet-4-20250514-v1:0`)
   - ✅ **Claude 3.7 Sonnet** (`anthropic.claude-3-7-sonnet-20250219-v1:0`)

### Via AWS CLI
```bash
# List available foundation models
aws bedrock list-foundation-models --region us-east-1 --by-provider anthropic

# Request access to Claude Sonnet 4
aws bedrock put-model-invocation-logging-configuration \
    --region us-east-1 \
    --logging-config \
    cloudWatchConfig='{logGroupName=bedrock-model-invocation-logs,roleArn=arn:aws:iam::YOUR_ACCOUNT:role/service-role/AmazonBedrockExecutionRoleForLogging_RANDOM}',\
    s3Config='{bucketName=YOUR_S3_BUCKET,keyPrefix=bedrock-logs/}'
```

### Verify Model Access
```bash
# Check available models
aws bedrock list-foundation-models \
    --region us-east-1 \
    --by-provider anthropic \
    --query "modelSummaries[?contains(modelId, 'claude-sonnet-4')].modelId"

# Expected output:
# [
#     "anthropic.claude-sonnet-4-20250514-v1:0"
# ]
```

## 🎯 Step 3: Configure Your Application

### Available Claude 4 Models in Bedrock
Your app already supports these models:

| Model | Bedrock Model ID | Capabilities |
|-------|------------------|--------------|
| **Claude Opus 4** | `anthropic.claude-opus-4-20250514-v1:0` | Most capable, 32k output |
| **Claude Sonnet 4** | `anthropic.claude-sonnet-4-20250514-v1:0` | High performance, 64k output |
| **Claude 3.7 Sonnet** | `anthropic.claude-3-7-sonnet-20250219-v1:0` | Extended thinking, 64k output |

### Environment Setup
```bash
# Set provider to Bedrock
export API_PROVIDER=bedrock

# Set AWS region (if different from default)
export AWS_REGION=us-east-1

# Optional: Set default model
export DEFAULT_MODEL=anthropic.claude-sonnet-4-20250514-v1:0
```

## 🚀 Step 4: Run with Claude Sonnet 4

### CLI Interface
```bash
# Activate your environment
source activate.sh

# Run with Claude Sonnet 4 (interactive)
python cli.py --provider bedrock

# Run with specific model
python cli.py \
    --provider bedrock \
    --model anthropic.claude-sonnet-4-20250514-v1:0 \
    --thinking-budget 20000

# Run with Claude Opus 4 for complex tasks
python cli.py \
    --provider bedrock \
    --model anthropic.claude-opus-4-20250514-v1:0 \
    --thinking-budget 25000 \
    --max-tokens 32000
```

### Streamlit Interface
```bash
# Launch web interface
streamlit run app.py

# In the sidebar:
# 1. Select "bedrock" as provider
# 2. Choose Claude Sonnet 4 from the model dropdown
# 3. Enable Extended Thinking if desired
# 4. Configure thinking budget (10k-64k tokens)
```

## ⚙️ Step 5: IAM Permissions

### Required IAM Policy
Create an IAM policy with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
            ]
        }
    ]
}
```

### Attach to User/Role
```bash
# Create policy
aws iam create-policy \
    --policy-name BedrockClaudeAccess \
    --policy-document file://bedrock-policy.json

# Attach to user
aws iam attach-user-policy \
    --user-name your-username \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT:policy/BedrockClaudeAccess
```

## 🧪 Step 6: Test Your Setup

### Quick Test Script
```python
# test_bedrock.py
import boto3
import json

def test_bedrock_claude():
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test Claude Sonnet 4
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello! Can you confirm you're Claude Sonnet 4 running on AWS Bedrock?"}]
                }
            ]
        })
        
        response = bedrock.invoke_model(
            body=body,
            modelId='anthropic.claude-sonnet-4-20250514-v1:0',
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        print("✅ SUCCESS! Claude Sonnet 4 response:")
        print(response_body["content"][0]["text"])
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_bedrock_claude()
```

Run the test:
```bash
python test_bedrock.py
```

## 🌟 Advanced Configuration

### Extended Thinking with Claude 4
```bash
# Enable extended thinking for complex reasoning
python cli.py \
    --provider bedrock \
    --model anthropic.claude-sonnet-4-20250514-v1:0 \
    --thinking-budget 32000  # Up to 64k for Sonnet 4
```

### Cost Optimization
```bash
# Use Sonnet 4 for most tasks (cost-effective)
export DEFAULT_MODEL=anthropic.claude-sonnet-4-20250514-v1:0

# Use Opus 4 only for complex tasks
# Pricing: Sonnet 4 ($3/$15 per 1M tokens) vs Opus 4 ($15/$75 per 1M tokens)
```

### Region Selection
```bash
# Available regions for Claude 4:
# - us-east-1 (N. Virginia) ✅ All models
# - us-east-2 (Ohio) ✅ All models  
# - us-west-2 (Oregon) ✅ All models

export AWS_REGION=us-west-2  # Change as needed
```

## 🔍 Troubleshooting

### Common Issues

**1. "ValidationException: Access denied" Error**
```bash
# Solution: Enable model access in Bedrock console
# Go to: AWS Console > Bedrock > Model Access
```

**2. "NoCredentialsError" Error**
```bash
# Solution: Configure AWS credentials
aws configure
# or
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**3. "Model not found" Error**
```bash
# Solution: Check model availability in your region
aws bedrock list-foundation-models --region us-east-1 --by-provider anthropic
```

**4. "Rate limit exceeded" Error**
```bash
# Solution: Implement exponential backoff (already built into the app)
# Or request quota increase in AWS Service Quotas
```

### Verification Commands
```bash
# Check AWS credentials
aws sts get-caller-identity

# List available models
aws bedrock list-foundation-models --region us-east-1 --by-provider anthropic

# Test model access
aws bedrock invoke-model \
    --region us-east-1 \
    --model-id anthropic.claude-sonnet-4-20250514-v1:0 \
    --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":[{"type":"text","text":"Hello"}]}]}' \
    --content-type application/json \
    --accept application/json /tmp/response.json && cat /tmp/response.json
```

## 🎉 You're Ready!

Your setup is complete! You can now use:

- ✅ **Claude Sonnet 4** on AWS Bedrock
- ✅ **Extended Thinking** for complex reasoning  
- ✅ **Up to 64k output tokens**
- ✅ **Native macOS integration**
- ✅ **Cost-effective pricing** through AWS

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 4 Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Anthropic Model Documentation](https://docs.anthropic.com/en/api/claude-on-amazon-bedrock)

Happy building with Claude Sonnet 4! 🚀 