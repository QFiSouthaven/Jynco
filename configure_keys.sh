#!/bin/bash

# Jynco API Keys Configuration Script
# Interactive script to help configure all required API keys

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${BOLD}${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║     🔑 Jynco API Keys Configuration Wizard 🔑        ║${NC}"
echo -e "${BOLD}${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "This script will help you configure all required API keys."
echo "You can skip any key by pressing Enter (use defaults)."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
fi

# Backup existing .env
cp .env .env.backup
echo -e "${GREEN}✓ Backed up existing .env to .env.backup${NC}"
echo ""

# Function to read current value from .env
get_current_value() {
    local key=$1
    grep "^${key}=" .env | cut -d '=' -f2- || echo ""
}

# Function to update .env value
update_env_value() {
    local key=$1
    local value=$2

    # Escape special characters for sed
    local escaped_value=$(echo "$value" | sed 's/[\/&]/\\&/g')

    # Update the value in .env
    if grep -q "^${key}=" .env; then
        sed -i "s|^${key}=.*|${key}=${escaped_value}|" .env
    else
        echo "${key}=${value}" >> .env
    fi
}

# Function to validate non-empty
validate_not_empty() {
    local value=$1
    [ -n "$value" ] && [ "$value" != "your_access_key" ] && [ "$value" != "your_secret_key" ] && [ "$value" != "your_runway_api_key" ] && [ "$value" != "your_stability_api_key" ] && [ "$value" != "your-secret-key-change-in-production" ]
}

# ============================================================================
# 1. AWS CREDENTIALS
# ============================================================================

echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}1/5: AWS Credentials (S3 Storage)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "AWS credentials are required for storing generated videos."
echo "Get them from: https://console.aws.amazon.com/iam/"
echo ""
echo -e "${YELLOW}How to get:${NC}"
echo "  1. Go to AWS IAM Console"
echo "  2. Create user with S3 access"
echo "  3. Copy Access Key ID and Secret Access Key"
echo ""

# AWS Access Key ID
current_aws_key=$(get_current_value "AWS_ACCESS_KEY_ID")
echo -e "${BLUE}Current AWS Access Key ID:${NC} ${current_aws_key}"
read -p "Enter new AWS Access Key ID (or press Enter to keep current): " aws_access_key
if [ -n "$aws_access_key" ]; then
    update_env_value "AWS_ACCESS_KEY_ID" "$aws_access_key"
    echo -e "${GREEN}✓ Updated AWS Access Key ID${NC}"
fi

# AWS Secret Access Key
current_aws_secret=$(get_current_value "AWS_SECRET_ACCESS_KEY")
echo -e "${BLUE}Current AWS Secret Access Key:${NC} ${current_aws_secret:0:10}... (hidden)"
read -sp "Enter new AWS Secret Access Key (or press Enter to keep current): " aws_secret_key
echo ""
if [ -n "$aws_secret_key" ]; then
    update_env_value "AWS_SECRET_ACCESS_KEY" "$aws_secret_key"
    echo -e "${GREEN}✓ Updated AWS Secret Access Key${NC}"
fi

# AWS Region
current_aws_region=$(get_current_value "AWS_REGION")
echo -e "${BLUE}Current AWS Region:${NC} ${current_aws_region}"
read -p "Enter AWS Region (or press Enter to keep current) [us-east-1]: " aws_region
if [ -n "$aws_region" ]; then
    update_env_value "AWS_REGION" "$aws_region"
    echo -e "${GREEN}✓ Updated AWS Region${NC}"
fi

# S3 Bucket
current_s3_bucket=$(get_current_value "S3_BUCKET")
echo -e "${BLUE}Current S3 Bucket:${NC} ${current_s3_bucket}"
echo -e "${YELLOW}Note: Bucket must already exist in S3${NC}"
read -p "Enter S3 Bucket name (or press Enter to keep current): " s3_bucket
if [ -n "$s3_bucket" ]; then
    update_env_value "S3_BUCKET" "$s3_bucket"
    echo -e "${GREEN}✓ Updated S3 Bucket${NC}"
fi

echo ""

# ============================================================================
# 2. RUNWAY API KEY
# ============================================================================

echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}2/5: Runway API Key (AI Video Generation)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Runway Gen-3 is used for AI video generation."
echo "Get your key from: https://app.runwayml.com/settings/api"
echo ""
echo -e "${YELLOW}How to get:${NC}"
echo "  1. Sign up at https://runwayml.com/"
echo "  2. Go to Settings → API"
echo "  3. Create new API key"
echo "  4. Add credits to your account"
echo ""
echo -e "${YELLOW}Cost: ~$0.05 per second of video (~$3/minute)${NC}"
echo ""

current_runway_key=$(get_current_value "RUNWAY_API_KEY")
echo -e "${BLUE}Current Runway API Key:${NC} ${current_runway_key:0:10}... (hidden)"
read -sp "Enter Runway API Key (starts with 'rw_') (or press Enter to keep current): " runway_key
echo ""
if [ -n "$runway_key" ]; then
    if [[ $runway_key == rw_* ]]; then
        update_env_value "RUNWAY_API_KEY" "$runway_key"
        echo -e "${GREEN}✓ Updated Runway API Key${NC}"
    else
        echo -e "${RED}⚠️  Warning: Runway API keys usually start with 'rw_'${NC}"
        read -p "Continue anyway? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            update_env_value "RUNWAY_API_KEY" "$runway_key"
            echo -e "${GREEN}✓ Updated Runway API Key${NC}"
        fi
    fi
fi

echo ""

# ============================================================================
# 3. STABILITY AI API KEY
# ============================================================================

echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}3/5: Stability AI API Key (AI Image/Video)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Stability AI is used for image and video generation."
echo "Get your key from: https://platform.stability.ai/account/keys"
echo ""
echo -e "${YELLOW}How to get:${NC}"
echo "  1. Sign up at https://platform.stability.ai/"
echo "  2. Go to Account → API Keys"
echo "  3. Create new API key"
echo "  4. Purchase credits"
echo ""
echo -e "${YELLOW}Cost: Varies by model, starting at $0.002 per image${NC}"
echo ""

current_stability_key=$(get_current_value "STABILITY_API_KEY")
echo -e "${BLUE}Current Stability API Key:${NC} ${current_stability_key:0:10}... (hidden)"
read -sp "Enter Stability AI API Key (starts with 'sk-') (or press Enter to keep current): " stability_key
echo ""
if [ -n "$stability_key" ]; then
    if [[ $stability_key == sk-* ]]; then
        update_env_value "STABILITY_API_KEY" "$stability_key"
        echo -e "${GREEN}✓ Updated Stability AI API Key${NC}"
    else
        echo -e "${RED}⚠️  Warning: Stability AI keys usually start with 'sk-'${NC}"
        read -p "Continue anyway? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            update_env_value "STABILITY_API_KEY" "$stability_key"
            echo -e "${GREEN}✓ Updated Stability AI API Key${NC}"
        fi
    fi
fi

echo ""

# ============================================================================
# 4. APPLICATION SECRET KEY
# ============================================================================

echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}4/5: Application Secret Key (Security)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Secret key is used for JWT tokens and session encryption."
echo ""

current_secret_key=$(get_current_value "SECRET_KEY")
echo -e "${BLUE}Current Secret Key:${NC} ${current_secret_key:0:10}... (hidden)"
echo ""
echo "Options:"
echo "  1. Generate a new random key (recommended)"
echo "  2. Enter your own key"
echo "  3. Keep current key"
echo ""
read -p "Choose option (1/2/3) [1]: " secret_option
secret_option=${secret_option:-1}

if [ "$secret_option" = "1" ]; then
    # Generate random key
    if command -v python3 &> /dev/null; then
        new_secret=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        update_env_value "SECRET_KEY" "$new_secret"
        echo -e "${GREEN}✓ Generated and saved new secret key${NC}"
    elif command -v openssl &> /dev/null; then
        new_secret=$(openssl rand -base64 32)
        update_env_value "SECRET_KEY" "$new_secret"
        echo -e "${GREEN}✓ Generated and saved new secret key${NC}"
    else
        echo -e "${RED}✗ Could not generate key (python3 or openssl required)${NC}"
        echo "Please enter a random string manually."
    fi
elif [ "$secret_option" = "2" ]; then
    read -sp "Enter your secret key (minimum 32 characters): " user_secret
    echo ""
    if [ ${#user_secret} -ge 32 ]; then
        update_env_value "SECRET_KEY" "$user_secret"
        echo -e "${GREEN}✓ Updated secret key${NC}"
    else
        echo -e "${RED}✗ Secret key too short (minimum 32 characters)${NC}"
        echo "Keeping current key."
    fi
fi

echo ""

# ============================================================================
# 5. DATABASE PASSWORD (OPTIONAL)
# ============================================================================

echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}5/5: Database Password (Optional)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Default database password is 'password' (fine for development)."
echo ""
read -p "Change database password? (y/N): " change_db_pass

if [[ $change_db_pass =~ ^[Yy]$ ]]; then
    read -sp "Enter new database password: " db_password
    echo ""
    read -sp "Confirm password: " db_password_confirm
    echo ""

    if [ "$db_password" = "$db_password_confirm" ]; then
        # Update DATABASE_URL
        update_env_value "DATABASE_URL" "postgresql://postgres:${db_password}@postgres:5432/videofoundry"
        echo -e "${GREEN}✓ Updated database password${NC}"
        echo -e "${YELLOW}⚠️  Remember to also update POSTGRES_PASSWORD in docker-compose.yml${NC}"
    else
        echo -e "${RED}✗ Passwords don't match. Keeping current password.${NC}"
    fi
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}Configuration Complete! ✓${NC}"
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check which keys are configured
aws_key_set=$(validate_not_empty "$(get_current_value 'AWS_ACCESS_KEY_ID')" && echo "✓" || echo "✗")
aws_secret_set=$(validate_not_empty "$(get_current_value 'AWS_SECRET_ACCESS_KEY')" && echo "✓" || echo "✗")
runway_set=$(validate_not_empty "$(get_current_value 'RUNWAY_API_KEY')" && echo "✓" || echo "✗")
stability_set=$(validate_not_empty "$(get_current_value 'STABILITY_API_KEY')" && echo "✓" || echo "✗")
secret_set=$(validate_not_empty "$(get_current_value 'SECRET_KEY')" && echo "✓" || echo "✗")

echo "Configuration Status:"
echo ""
echo -e "  AWS Access Key ID:        ${aws_key_set}"
echo -e "  AWS Secret Access Key:    ${aws_secret_set}"
echo -e "  Runway API Key:           ${runway_set}"
echo -e "  Stability AI API Key:     ${stability_set}"
echo -e "  Application Secret Key:   ${secret_set}"
echo ""

# Check if all required keys are set
if [[ "$aws_key_set" == "✓" && "$aws_secret_set" == "✓" && "$secret_set" == "✓" ]]; then
    echo -e "${GREEN}✓ All essential keys are configured!${NC}"
    echo ""
    if [[ "$runway_set" == "✗" || "$stability_set" == "✗" ]]; then
        echo -e "${YELLOW}⚠️  AI keys not configured. AI features will not work.${NC}"
        echo "  You can add them later by running this script again."
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  Some required keys are missing.${NC}"
    echo "  Run this script again to complete configuration."
    echo ""
fi

# Next steps
echo -e "${BOLD}${BLUE}Next Steps:${NC}"
echo ""
echo "1. ${BOLD}Validate your keys:${NC}"
echo "   ./validate_keys.py"
echo ""
echo "2. ${BOLD}Launch the platform:${NC}"
echo "   ./launch.sh"
echo ""
echo "3. ${BOLD}Access the application:${NC}"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Ask if user wants to validate now
read -p "Would you like to validate your keys now? (y/N): " validate_now
if [[ $validate_now =~ ^[Yy]$ ]]; then
    echo ""
    if [ -f "./validate_keys.py" ]; then
        python3 ./validate_keys.py
    else
        echo -e "${YELLOW}validate_keys.py not found. Run it manually after it's created.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Done! Your configuration has been saved to .env${NC}"
echo -e "${YELLOW}Backup saved to .env.backup${NC}"
echo ""
