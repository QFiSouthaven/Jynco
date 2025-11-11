#!/usr/bin/env python3
"""
Jynco API Keys Validation Script
Validates all configured API keys and credentials
"""

import os
import sys
from typing import Dict, Tuple
import json

# Color codes for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'═' * 60}{Colors.NC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.NC}")

def load_env() -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}

    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print_info("Run ./configure_keys.sh to create one")
        sys.exit(1)

    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    return env_vars

def validate_aws_credentials(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate AWS credentials and S3 access"""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        access_key = env_vars.get('AWS_ACCESS_KEY_ID', '')
        secret_key = env_vars.get('AWS_SECRET_ACCESS_KEY', '')
        region = env_vars.get('AWS_REGION', 'us-east-1')
        bucket = env_vars.get('S3_BUCKET', '')

        # Check if keys are set
        if not access_key or access_key.startswith('your_'):
            return False, "AWS Access Key ID not configured"

        if not secret_key or secret_key.startswith('your_'):
            return False, "AWS Secret Access Key not configured"

        if not bucket or bucket.startswith('video-foundry-dev'):
            return False, f"S3 bucket not configured or using default: {bucket}"

        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Test credentials by listing buckets
        try:
            s3_client.head_bucket(Bucket=bucket)
            return True, f"Successfully accessed bucket '{bucket}' in {region}"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False, f"Bucket '{bucket}' not found. Please create it first."
            elif error_code == '403':
                return False, f"Access denied to bucket '{bucket}'. Check IAM permissions."
            else:
                return False, f"Error accessing bucket: {str(e)}"

    except ImportError:
        return False, "boto3 not installed. Run: pip install boto3"
    except NoCredentialsError:
        return False, "Invalid AWS credentials"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def validate_runway_api(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate Runway API key"""
    try:
        import requests

        api_key = env_vars.get('RUNWAY_API_KEY', '')

        # Check if key is set
        if not api_key or api_key.startswith('your_'):
            return False, "Runway API key not configured"

        # Check key format
        if not api_key.startswith('rw_'):
            print_warning("Runway API keys typically start with 'rw_'")

        # Test API key with a simple request
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Try to get user info or list tasks (light endpoint)
        response = requests.get(
            'https://api.runwayml.com/v1/tasks',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return True, "API key is valid and active"
        elif response.status_code == 401:
            return False, "API key is invalid or expired"
        elif response.status_code == 403:
            return False, "API key is valid but has no permissions"
        else:
            return False, f"Unexpected response: {response.status_code}"

    except ImportError:
        return False, "requests library not installed. Run: pip install requests"
    except requests.exceptions.Timeout:
        return False, "Request timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to Runway API. Check your internet connection."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def validate_stability_api(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate Stability AI API key"""
    try:
        import requests

        api_key = env_vars.get('STABILITY_API_KEY', '')

        # Check if key is set
        if not api_key or api_key.startswith('your_'):
            return False, "Stability AI API key not configured"

        # Check key format
        if not api_key.startswith('sk-'):
            print_warning("Stability AI keys typically start with 'sk-'")

        # Test API key with user/account endpoint
        headers = {
            'Authorization': f'Bearer {api_key}',
        }

        response = requests.get(
            'https://api.stability.ai/v1/user/account',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            email = data.get('email', 'N/A')
            return True, f"API key is valid (Account: {email})"
        elif response.status_code == 401:
            return False, "API key is invalid or expired"
        elif response.status_code == 403:
            return False, "API key is valid but has no permissions"
        else:
            return False, f"Unexpected response: {response.status_code}"

    except ImportError:
        return False, "requests library not installed. Run: pip install requests"
    except requests.exceptions.Timeout:
        return False, "Request timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to Stability API. Check your internet connection."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def validate_secret_key(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate application secret key"""
    secret_key = env_vars.get('SECRET_KEY', '')

    if not secret_key or secret_key.startswith('your-secret-key'):
        return False, "Secret key not configured (using default)"

    if len(secret_key) < 32:
        return False, f"Secret key too short ({len(secret_key)} chars, minimum 32)"

    if secret_key == 'your-secret-key-change-in-production':
        return False, "Using default secret key (change for production)"

    return True, f"Secret key is strong ({len(secret_key)} characters)"

def validate_database_config(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate database configuration"""
    db_url = env_vars.get('DATABASE_URL', '')

    if not db_url:
        return False, "DATABASE_URL not configured"

    # Check if using default password
    if 'password@postgres' in db_url or ':password@' in db_url:
        return True, "Using default password (OK for development)"

    return True, "Custom database password configured"

def validate_redis_config(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate Redis configuration"""
    redis_url = env_vars.get('REDIS_URL', '')

    if not redis_url:
        return False, "REDIS_URL not configured"

    return True, f"Redis configured: {redis_url}"

def validate_rabbitmq_config(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Validate RabbitMQ configuration"""
    rabbitmq_url = env_vars.get('RABBITMQ_URL', '')

    if not rabbitmq_url:
        return False, "RABBITMQ_URL not configured"

    return True, f"RabbitMQ configured: {rabbitmq_url.split('@')[0]}@..."

def main():
    """Main validation function"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 Jynco API Keys Validator 🔍{Colors.NC}\n")

    # Load environment variables
    print_info("Loading configuration from .env...")
    try:
        env_vars = load_env()
        print_success("Configuration loaded")
    except Exception as e:
        print_error(f"Failed to load configuration: {str(e)}")
        sys.exit(1)

    # Track results
    results = {}

    # 1. Validate AWS Credentials
    print_header("1. AWS Credentials (S3 Storage)")
    print_info("Validating AWS credentials...")
    success, message = validate_aws_credentials(env_vars)
    results['AWS'] = success
    if success:
        print_success(message)
    else:
        print_error(message)
        print_info("Get credentials from: https://console.aws.amazon.com/iam/")

    # 2. Validate Runway API
    print_header("2. Runway API (AI Video Generation)")
    print_info("Validating Runway API key...")
    success, message = validate_runway_api(env_vars)
    results['Runway'] = success
    if success:
        print_success(message)
    else:
        print_error(message)
        print_info("Get API key from: https://app.runwayml.com/settings/api")

    # 3. Validate Stability AI
    print_header("3. Stability AI (AI Image/Video)")
    print_info("Validating Stability AI API key...")
    success, message = validate_stability_api(env_vars)
    results['Stability'] = success
    if success:
        print_success(message)
    else:
        print_error(message)
        print_info("Get API key from: https://platform.stability.ai/account/keys")

    # 4. Validate Secret Key
    print_header("4. Application Secret Key")
    print_info("Checking secret key strength...")
    success, message = validate_secret_key(env_vars)
    results['Secret'] = success
    if success:
        print_success(message)
    else:
        print_error(message)
        print_info("Run: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\"")

    # 5. Validate Other Configs
    print_header("5. Other Configuration")

    print_info("Checking database configuration...")
    success, message = validate_database_config(env_vars)
    results['Database'] = success
    if success:
        print_success(message)
    else:
        print_error(message)

    print_info("Checking Redis configuration...")
    success, message = validate_redis_config(env_vars)
    results['Redis'] = success
    if success:
        print_success(message)
    else:
        print_error(message)

    print_info("Checking RabbitMQ configuration...")
    success, message = validate_rabbitmq_config(env_vars)
    results['RabbitMQ'] = success
    if success:
        print_success(message)
    else:
        print_error(message)

    # Summary
    print_header("Validation Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"Results: {passed}/{total} checks passed\n")

    for service, passed in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if passed else f"{Colors.RED}✗ FAIL{Colors.NC}"
        print(f"  {service:20} {status}")

    print()

    # Final verdict
    critical_services = ['AWS', 'Secret']
    critical_passed = all(results.get(s, False) for s in critical_services)

    if critical_passed:
        print_success("✓ All critical services configured correctly!")
        if not all(results.values()):
            print_warning("Some optional services need configuration")
            print_info("AI features require both Runway and Stability AI keys")
        print()
        print_info("You're ready to launch! Run: ./launch.sh")
    else:
        print_error("✗ Critical services not configured properly")
        print_info("Run ./configure_keys.sh to fix configuration")
        sys.exit(1)

    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation cancelled by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
