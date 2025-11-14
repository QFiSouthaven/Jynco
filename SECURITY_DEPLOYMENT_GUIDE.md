# Security Architecture Deployment Guide

## Quick Start by Execution Mode

### Developer Mode (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco

# 2. Copy environment file
cp .env.example .env

# 3. Set execution mode
echo "JYNCO_EXECUTION_MODE=developer" >> .env

# 4. Start services
docker-compose up -d

# 5. Verify
docker-compose logs -f backend
```

**Developer Mode Warnings:**
- NOT secure for production
- Uses .env for secrets
- No IAM enforcement
- Permissive workflow vetting
- DO NOT expose to public networks

---

### Self-Hosted Production Mode

```bash
# 1. Install gVisor (recommended)
./scripts/install-gvisor.sh

# 2. Configure environment
cp .env.example .env
vim .env  # Set JYNCO_EXECUTION_MODE=self-hosted-production

# 3. Configure workflow allowlist
vim config/workflow_allowlist.yaml

# 4. (Optional) Set up Vault
# Follow: https://www.vaultproject.io/docs/install

# 5. Start with self-hosted override
docker-compose -f docker-compose.yml -f docker-compose.self-hosted.yml up -d

# 6. Apply database migrations
docker-compose exec backend python -m alembic upgrade head
docker-compose exec postgres psql -U postgres -d videofoundry -f /app/backend/migrations/002_row_level_security.sql

# 7. Create admin user
docker-compose exec backend python scripts/create_admin_user.py
```

---

### Production Mode (Multi-Tenant SaaS)

```bash
# 1. Prerequisites
- Kubernetes cluster with gVisor runtime class
- HashiCorp Vault or AWS Secrets Manager
- S3 bucket with IAM policies
- Keycloak/Auth0 configured

# 2. Configure secrets in Vault
vault kv put secret/videofoundry/production/database password=<strong-password>
vault kv put secret/videofoundry/production/jwt secret=<random-secret>
vault kv put secret/videofoundry/production/aws access_key=<key> secret_key=<secret>

# 3. Configure environment
cp .env.production.example .env.production
vim .env.production  # Fill in Vault, OIDC, S3 details

# 4. Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/rabbitmq.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/ai-worker.yaml
kubectl apply -f k8s/frontend.yaml

# 5. Apply database migrations
kubectl exec -it <postgres-pod> -- psql -U postgres -d videofoundry -f /migrations/002_row_level_security.sql

# 6. Verify security posture
kubectl exec -it <backend-pod> -- python scripts/validate_security.py
```

---

## Component-Specific Setup

### 1. gVisor Sandboxing

```bash
# Ubuntu/Debian
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list > /dev/null
sudo apt-get update
sudo apt-get install -y runsc

# Configure Docker
sudo cp config/docker-daemon-gvisor.json /etc/docker/daemon.json
sudo systemctl restart docker

# Verify
docker run --rm --runtime=runsc hello-world
```

### 2. Vault Integration

```bash
# Install Vault (Development)
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_1.15.0_linux_amd64.zip
sudo mv vault /usr/local/bin/

# Start Vault (Dev mode for testing)
vault server -dev &

# Initialize secrets
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN=root
vault kv put secret/videofoundry/database password=mydbpass
vault kv put secret/videofoundry/jwt secret=$(openssl rand -base64 32)

# Production: Use real Vault cluster with TLS
```

### 3. OIDC/Keycloak Setup

```bash
# Run Keycloak (Docker)
docker run -d \
  --name keycloak \
  -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev

# Configure:
# 1. Create realm: videofoundry
# 2. Create client: videofoundry-backend
# 3. Enable OIDC
# 4. Configure redirect URLs
# 5. Create roles: admin, user, viewer
# 6. Create users and assign roles

# Update .env:
OIDC_PROVIDER_URL=http://localhost:8080/realms/videofoundry
OIDC_CLIENT_ID=videofoundry-backend
OIDC_CLIENT_SECRET=<from-keycloak>
```

### 4. Row-Level Security

```bash
# Apply RLS migration
docker-compose exec postgres psql -U postgres -d videofoundry

# Run migration
\i /app/backend/migrations/002_row_level_security.sql

# Verify policies
SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public';

# Test (as user)
SET app.current_user_id = '<user-uuid>';
SELECT * FROM projects;  -- Should only show user's projects
```

### 5. S3 User Isolation

```bash
# Create S3 bucket
aws s3 mb s3://videofoundry-production

# Create IAM policy for user isolation
cat > videofoundry-s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::videofoundry-production"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::videofoundry-production/users/*"
    }
  ]
}
EOF

# Apply policy
aws iam create-policy --policy-name VideoFoundryS3Access --policy-document file://videofoundry-s3-policy.json
```

---

## Security Verification Checklist

### Production Deployment

- [ ] gVisor runtime installed and tested
- [ ] Vault configured with all secrets
- [ ] S3 bucket with user isolation IAM policies
- [ ] OIDC provider configured with correct redirect URLs
- [ ] Database RLS policies applied
- [ ] Workflow allowlist populated
- [ ] Network isolation enabled (NO internet for workers)
- [ ] All containers running as non-root
- [ ] Read-only root filesystems
- [ ] Capabilities dropped (no privileged containers)
- [ ] Audit logging configured
- [ ] Backup procedures in place
- [ ] Incident response plan documented

### Self-Hosted Deployment

- [ ] gVisor installed (recommended)
- [ ] Vault configured OR secure .env file permissions (0600)
- [ ] S3 configured OR local storage on dedicated volume
- [ ] IAM configured OR strong passwords for basic auth
- [ ] Database RLS applied
- [ ] Workflow allowlist configured by admin
- [ ] Egress proxy configured (if needed)
- [ ] Audit logging enabled
- [ ] Backup procedures in place

### Developer Mode

- [ ] Confirmed NOT on public network
- [ ] Confirmed NO sensitive data
- [ ] .env file permissions set (0600)
- [ ] Sandboxing enabled (gVisor recommended)

---

## Troubleshooting

### Issue: Backend won't start in production mode

**Error:** "VAULT_ADDR and VAULT_TOKEN are required in production mode"

**Solution:**
```bash
# Verify environment variables
docker-compose exec backend env | grep VAULT

# If missing, update .env
echo "VAULT_ADDR=https://vault.company.com" >> .env
echo "VAULT_TOKEN=s.xyz123..." >> .env

# Restart
docker-compose restart backend
```

### Issue: RLS blocking admin access

**Error:** User sees no projects despite being admin

**Solution:**
```sql
-- Verify user role
SELECT id, username, role FROM users WHERE id = '<user-uuid>';

-- If not admin, update
UPDATE users SET role = 'admin' WHERE id = '<user-uuid>';

-- Test again
```

### Issue: S3 access denied

**Error:** "Access denied: file does not belong to user"

**Solution:**
```python
# Check file path format
# Correct: users/<user-id>/projects/<project-id>/file.mp4
# Incorrect: projects/<project-id>/file.mp4

# Files must be under users/<user-id>/ prefix
```

---

## Monitoring and Alerts

### Metrics to Monitor

1. **Authentication Failures**
   ```bash
   docker-compose logs backend | grep "authentication failed"
   ```

2. **Workflow Vetting Rejections**
   ```bash
   docker-compose logs backend | grep "security violations"
   ```

3. **Unauthorized Access Attempts**
   ```sql
   SELECT * FROM audit_logs WHERE success = false ORDER BY timestamp DESC LIMIT 100;
   ```

4. **Sandbox Escapes (should be zero)**
   ```bash
   sudo grep "sandbox violation" /var/log/runsc/*/log
   ```

---

## Compliance

### SOC 2 Requirements

- **CC6.1 (Logical Access):** IAM/RBAC + RLS
- **CC6.6 (Encryption):** S3 SSE + TLS
- **CC7.2 (Monitoring):** Audit logs

### GDPR Requirements

- **Art. 25 (Data Protection by Design):** RLS + user isolation
- **Art. 32 (Security Measures):** Sandboxing + encryption

---

## Migration from Developer to Production

```bash
# 1. Backup all data
docker-compose exec postgres pg_dump -U postgres videofoundry > backup.sql

# 2. Set up Vault
# ... configure Vault

# 3. Migrate secrets
# Move from .env to Vault

# 4. Update environment
vim .env  # Change to JYNCO_EXECUTION_MODE=production

# 5. Restart with production override
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# 6. Verify
docker-compose logs -f backend
```

---

## Support

- Documentation: /home/user/Jynco/SECURITY_ARCHITECTURE.md
- Sandboxing Guide: /home/user/Jynco/SANDBOXING_SETUP_GUIDE.md
- Issues: https://github.com/QFiSouthaven/Jynco/issues

---

**Last Updated:** 2025-11-14
**Version:** 3.0
