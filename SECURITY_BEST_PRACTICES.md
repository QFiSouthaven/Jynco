# 🔒 Security Best Practices for Jynco Video Foundry

This document outlines security best practices for deploying and operating the Jynco Video Foundry platform.

## Table of Contents

1. [Environment Variables & Secrets Management](#1-environment-variables--secrets-management)
2. [AWS Security](#2-aws-security)
3. [API Keys Management](#3-api-keys-management)
4. [Database Security](#4-database-security)
5. [Network Security](#5-network-security)
6. [Container Security](#6-container-security)
7. [Authentication & Authorization](#7-authentication--authorization)
8. [Production Deployment](#8-production-deployment)
9. [Monitoring & Incident Response](#9-monitoring--incident-response)
10. [Compliance & Data Privacy](#10-compliance--data-privacy)

---

## 1. Environment Variables & Secrets Management

### ✅ DO:

- **Never commit .env files to git**
  - `.env` is already in `.gitignore`
  - Always verify before committing: `git status`

- **Use different credentials for each environment**
  ```
  .env.development
  .env.staging
  .env.production
  ```

- **Rotate secrets regularly**
  - API keys: Every 90 days
  - Database passwords: Every 90 days
  - Application secret key: Every 180 days

- **Use secrets management services in production**
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault
  - Google Secret Manager

- **Set appropriate file permissions**
  ```bash
  chmod 600 .env
  chmod 700 .env.*
  ```

### ❌ DON'T:

- Never share .env files via email, Slack, or other messaging
- Never hardcode secrets in source code
- Never log sensitive environment variables
- Never use default/example secrets in production
- Never store secrets in version control

---

## 2. AWS Security

### IAM Best Practices

#### Create Dedicated IAM User

```bash
# DO: Create user with minimal permissions
aws iam create-user --user-name jynco-video-foundry
```

#### Use Least Privilege Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name"
    }
  ]
}
```

### S3 Bucket Security

#### Bucket Configuration

```bash
# Enable versioning (helps with recovery)
aws s3api put-bucket-versioning \
  --bucket your-bucket-name \
  --versioning-configuration Status=Enabled

# Enable encryption at rest
aws s3api put-bucket-encryption \
  --bucket your-bucket-name \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access (unless you need public URLs)
aws s3api put-public-access-block \
  --bucket your-bucket-name \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

#### Bucket Lifecycle Policy

```json
{
  "Rules": [
    {
      "Id": "DeleteOldVideos",
      "Status": "Enabled",
      "Expiration": {
        "Days": 90
      },
      "Filter": {
        "Prefix": "temp/"
      }
    }
  ]
}
```

### ✅ DO:

- Use IAM roles for EC2/ECS instead of access keys when possible
- Enable MFA for IAM users
- Enable CloudTrail for audit logging
- Use VPC endpoints for S3 access
- Enable S3 bucket logging

### ❌ DON'T:

- Never use root AWS account credentials
- Never make S3 buckets fully public
- Never disable encryption
- Never share IAM access keys

---

## 3. API Keys Management

### Runway API Key

#### Securing Your Key

```bash
# Set appropriate permissions if storing in file
chmod 600 .env
```

#### Monitoring Usage

1. Check usage regularly: https://app.runwayml.com/billing
2. Set up billing alerts
3. Monitor for unexpected API calls

#### Rotating Keys

```bash
# 1. Generate new key in Runway dashboard
# 2. Update .env with new key
# 3. Restart services
docker-compose restart backend ai_worker
# 4. Verify new key works
# 5. Delete old key in Runway dashboard
```

### Stability AI API Key

#### Similar practices as Runway:

1. Monitor usage: https://platform.stability.ai/account/billing
2. Set spending limits
3. Rotate every 90 days
4. Use separate keys for dev/prod

### ✅ DO:

- Monitor API usage and costs daily
- Set up spending alerts
- Rotate keys on a schedule
- Keep backup keys (inactive) for emergency rotation
- Log all API errors (but not the keys themselves)

### ❌ DON'T:

- Never expose API keys in client-side code
- Never log API keys
- Never share keys between environments
- Never commit keys to git

---

## 4. Database Security

### PostgreSQL Security

#### Strong Passwords

```bash
# Generate strong password
openssl rand -base64 32
```

#### Connection Security

```yaml
# docker-compose.yml - Use SSL in production
DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/videofoundry?sslmode=require
```

#### Database Configuration

```conf
# postgresql.conf (production)
ssl = on
password_encryption = scrypt
```

#### Backup Strategy

```bash
# Automated daily backups
0 2 * * * docker-compose exec postgres pg_dump -U postgres videofoundry | gzip > /backups/videofoundry-$(date +\%Y\%m\%d).sql.gz

# Keep 30 days of backups
find /backups -name "videofoundry-*.sql.gz" -mtime +30 -delete
```

### ✅ DO:

- Use strong passwords (32+ characters)
- Enable SSL/TLS for database connections
- Encrypt backups
- Store backups in different location than database
- Test backup restoration regularly
- Use read replicas for scaling
- Implement connection pooling

### ❌ DON'T:

- Never use default passwords in production
- Never expose database port to internet
- Never skip backups
- Never store passwords in plain text

---

## 5. Network Security

### Docker Network Isolation

```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

services:
  frontend:
    networks:
      - frontend
  backend:
    networks:
      - frontend
      - backend
  postgres:
    networks:
      - backend  # Not accessible from frontend
```

### Firewall Rules

```bash
# Allow only necessary ports
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### HTTPS/TLS

#### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### ✅ DO:

- Use HTTPS/TLS in production
- Implement rate limiting
- Use firewall rules
- Segment networks
- Use VPN for administrative access
- Implement CORS properly

### ❌ DON'T:

- Never expose internal services to internet
- Never use HTTP in production
- Never disable firewalls
- Never use default ports in production

---

## 6. Container Security

### Docker Security

#### Keep Images Updated

```bash
# Regularly update base images
docker-compose pull
docker-compose up -d --build
```

#### Use Non-Root Users

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Switch to non-root user
USER appuser

# Rest of Dockerfile...
```

#### Scan Images for Vulnerabilities

```bash
# Using Docker Scout
docker scout cves backend:latest

# Using Trivy
trivy image backend:latest
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

### ✅ DO:

- Use official base images
- Keep images updated
- Scan for vulnerabilities
- Use multi-stage builds
- Implement resource limits
- Run as non-root user
- Use read-only filesystems where possible

### ❌ DON'T:

- Never run containers as root in production
- Never use `:latest` tag in production
- Never disable security scanning
- Never include unnecessary packages

---

## 7. Authentication & Authorization

### JWT Configuration

```python
# Secure JWT settings
JWT_SECRET_KEY = os.getenv('SECRET_KEY')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### Password Hashing

```python
# Use bcrypt with high cost factor
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # High cost factor
)
```

### User Sessions

```python
# Implement session timeout
SESSION_TIMEOUT_MINUTES = 30

# Implement refresh token rotation
REFRESH_TOKEN_ROTATION = True
```

### ✅ DO:

- Use strong password hashing (bcrypt, argon2)
- Implement rate limiting on login
- Use JWT with short expiration
- Implement refresh token rotation
- Require strong passwords (min 12 chars)
- Implement 2FA for admin accounts
- Log authentication attempts

### ❌ DON'T:

- Never store passwords in plain text
- Never use weak hashing (MD5, SHA1)
- Never allow unlimited login attempts
- Never use predictable session IDs
- Never skip input validation

---

## 8. Production Deployment

### Pre-Deployment Checklist

- [ ] All secrets rotated from development
- [ ] HTTPS/TLS configured
- [ ] Database backups configured
- [ ] Monitoring and alerting configured
- [ ] Firewall rules configured
- [ ] Resource limits configured
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Log aggregation configured
- [ ] Health checks configured
- [ ] Disaster recovery plan documented

### Environment Variables Audit

```bash
# Check for default/weak values
grep -E "(password|secret|key)" .env | grep -E "(your_|example|default|changeme|password)"
```

### Security Scanning

```bash
# Run security audit
npm audit (for frontend)
safety check (for Python)
docker scan
```

### ✅ DO:

- Use managed services (RDS, ElastiCache, etc.) in production
- Implement automated backups
- Use infrastructure as code (Terraform, CloudFormation)
- Implement blue-green deployments
- Use container orchestration (Kubernetes, ECS)
- Implement auto-scaling
- Use CDN for static assets

### ❌ DON'T:

- Never deploy without testing
- Never skip security scanning
- Never use development credentials
- Never disable logging

---

## 9. Monitoring & Incident Response

### Logging

```python
# Centralized logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/app.log'),
        logging.StreamHandler()
    ]
)

# Never log sensitive data
logger.info(f"User login: {user_id}")  # Good
logger.info(f"User password: {password}")  # BAD!
```

### Monitoring Metrics

- API response times
- Error rates
- Database connection pool usage
- S3 storage usage
- API costs (Runway, Stability)
- Worker queue lengths
- Memory/CPU usage

### Alerting

```yaml
# Example alert rules
alerts:
  - name: HighErrorRate
    condition: error_rate > 5%
    notification: email, slack

  - name: HighAPICost
    condition: daily_cost > $100
    notification: email, pagerduty

  - name: DatabaseDown
    condition: db_health == false
    notification: pagerduty, sms
```

### Incident Response Plan

1. **Detect**: Monitoring alerts trigger
2. **Assess**: Determine severity and impact
3. **Contain**: Isolate affected systems
4. **Eradicate**: Fix root cause
5. **Recover**: Restore normal operations
6. **Learn**: Post-mortem and improvements

### ✅ DO:

- Implement comprehensive logging
- Set up alerts for critical metrics
- Have incident response plan
- Conduct regular security audits
- Keep audit logs for 90+ days
- Test disaster recovery regularly

---

## 10. Compliance & Data Privacy

### GDPR Considerations

- Implement data deletion on user request
- Provide data export functionality
- Document data retention policies
- Implement consent management

### Data Retention

```python
# Example retention policy
DATA_RETENTION_DAYS = {
    'user_videos': 90,
    'audit_logs': 365,
    'user_data': 730,  # 2 years
    'temp_files': 7
}
```

### Privacy Considerations

- Encrypt sensitive data at rest
- Encrypt data in transit
- Implement access controls
- Minimize data collection
- Document data processing

---

## Quick Security Checklist

### Development
- [x] .env in .gitignore
- [ ] No secrets in code
- [ ] Dependencies updated
- [ ] Security scanning enabled

### Staging
- [ ] Separate credentials from dev
- [ ] HTTPS enabled
- [ ] Monitoring configured
- [ ] Backups configured

### Production
- [ ] All secrets rotated
- [ ] HTTPS/TLS enforced
- [ ] WAF configured
- [ ] DDoS protection enabled
- [ ] Backups automated
- [ ] Disaster recovery tested
- [ ] Compliance requirements met
- [ ] Security audit completed

---

## Resources

### Tools
- **Secrets Management**: AWS Secrets Manager, HashiCorp Vault
- **Vulnerability Scanning**: Trivy, Docker Scout, Snyk
- **SAST**: SonarQube, Bandit (Python), ESLint (JS)
- **Monitoring**: Prometheus, Grafana, DataDog
- **Logging**: ELK Stack, CloudWatch, Splunk
- **WAF**: AWS WAF, Cloudflare

### Learning Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CIS Docker Benchmark: https://www.cisecurity.org/
- AWS Security Best Practices: https://aws.amazon.com/security/
- Docker Security: https://docs.docker.com/engine/security/

---

## Getting Help

For security concerns or questions:
1. Review this document
2. Check OWASP guidelines
3. Consult security team
4. Report vulnerabilities responsibly

**Remember: Security is not a one-time task, it's an ongoing process!** 🔒
