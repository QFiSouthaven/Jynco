# Video Foundry (Jynco) - Security Architecture v3.0

## Executive Summary

This document defines the comprehensive security architecture for Video Foundry (Jynco), implementing a three-tier execution model that balances security, usability, and operational flexibility across different deployment scenarios.

**Version:** 3.0
**Status:** Implementation Ready
**Last Updated:** 2025-11-14

## Table of Contents

1. [Core Security Principles](#core-security-principles)
2. [Three-Tier Execution Model](#three-tier-execution-model)
3. [Architecture Components](#architecture-components)
4. [Deployment Scenarios](#deployment-scenarios)
5. [Security Controls Matrix](#security-controls-matrix)
6. [Implementation Guide](#implementation-guide)
7. [Threat Model](#threat-model)
8. [Compliance & Audit](#compliance--audit)

---

## Core Security Principles

Video Foundry's security architecture is built on five foundational principles:

### 1. Zero Trust
- **Principle:** No component is trusted by default
- **Implementation:** All interactions require explicit authentication and authorization
- **Scope:** Applies to service-to-service, user-to-service, and external integrations

### 2. Defense in Depth
- **Principle:** Multiple, layered security controls prevent single point of failure
- **Implementation:** Network isolation, sandboxing, RBAC, RLS, and audit logging
- **Scope:** Every tier has redundant security mechanisms

### 3. Principle of Least Privilege
- **Principle:** Components receive minimum necessary permissions
- **Implementation:** Role-based access control, scoped API keys, container-level restrictions
- **Scope:** Tailored to operational context (production vs. development)

### 4. Secure by Default
- **Principle:** Most secure configuration is the default
- **Implementation:** Production mode is default; less secure options require explicit configuration
- **Scope:** All configuration parameters default to most restrictive settings

### 5. Context-Aware Security
- **Principle:** Controls adapt to deployment environment
- **Implementation:** Three-tier execution model with environment-specific policies
- **Scope:** Workflow vetting, sandboxing, storage, and secrets management

---

## Three-Tier Execution Model

The system operates in one of three modes, configured via `JYNCO_EXECUTION_MODE` environment variable.

### Tier 1: Production Mode

**Target Environment:** Multi-tenant SaaS deployments

**Configuration:**
```bash
JYNCO_EXECUTION_MODE=production
```

**Security Controls:**

| Component | Configuration | Enforcement |
|-----------|---------------|-------------|
| **Workflow Vetting** | Strict allow-list only | Mandatory |
| **Sandboxing** | gVisor/Firecracker micro-VM | Mandatory |
| **Internet Egress** | ZERO (completely blocked) | Mandatory |
| **Artifact Repository** | Internal only (vetted assets) | Mandatory |
| **IAM/RBAC** | Full authentication + authorization | Mandatory |
| **Database RLS** | User-scoped row-level security | Mandatory |
| **Secrets Management** | Vault (HashiCorp/AWS) | Mandatory |
| **Storage** | Cloud (S3/equivalent) with user isolation | Mandatory |
| **Audit Logging** | Full audit trail | Mandatory |

**Startup Validation:**
- System will **fail to start** if vault is not configured
- System will **fail to start** if cloud storage is not configured
- System will **fail to start** if IAM provider is not configured

**Use Cases:**
- Public SaaS offering
- Multi-tenant platforms
- Regulated industries (HIPAA, SOC2, GDPR)

---

### Tier 2: Self-Hosted Production Mode

**Target Environment:** Single-tenant, self-hosted enterprise deployments

**Configuration:**
```bash
JYNCO_EXECUTION_MODE=self-hosted-production
```

**Security Controls:**

| Component | Configuration | Enforcement |
|-----------|---------------|-------------|
| **Workflow Vetting** | Admin-configurable allow-list | Mandatory |
| **Sandboxing** | gVisor/Firecracker micro-VM | Mandatory |
| **Internet Egress** | Controlled via admin-approved proxy | Optional (admin-configured) |
| **Artifact Repository** | Admin-approved sources | Configurable |
| **IAM/RBAC** | Recommended (can use basic auth) | Recommended |
| **Database RLS** | Recommended | Recommended |
| **Secrets Management** | Vault recommended (.env fallback allowed) | Recommended |
| **Storage** | Cloud recommended (local volume allowed) | Configurable |
| **Audit Logging** | Full audit trail | Mandatory |

**Startup Validation:**
- System will **warn** if vault is not configured (but will start)
- System will **warn** if using local storage instead of cloud
- System will **warn** if IAM is not fully configured

**Administrator Controls:**
- Approve specific Git repositories for custom nodes
- Approve specific model sources (e.g., Hugging Face)
- Configure egress allowlist (domains/IPs)
- Manage internal user permissions

**Use Cases:**
- Private enterprise deployments
- On-premise installations
- Air-gapped environments (with pre-vetted assets)

---

### Tier 3: Developer Mode

**Target Environment:** Local development, R&D, experimentation

**Configuration:**
```bash
JYNCO_EXECUTION_MODE=developer
```

**Security Controls:**

| Component | Configuration | Enforcement |
|-----------|---------------|-------------|
| **Workflow Vetting** | Log-and-warn (permissive) | Optional |
| **Sandboxing** | Mandatory (prevents host compromise) | Mandatory |
| **Internet Egress** | Proxied and logged | Allowed |
| **Artifact Repository** | Public repositories allowed | Allowed |
| **IAM/RBAC** | Optional (single-user mode) | Optional |
| **Database RLS** | Optional | Optional |
| **Secrets Management** | .env files allowed | Fallback |
| **Storage** | Local volume (default) | Default |
| **Audit Logging** | Basic logging | Basic |

**Startup Warnings:**
- Prominent warning: "Developer mode is NOT secure for production use"
- Warning about .env-based secrets
- Warning about permissive workflow execution

**UI/UX Indicators:**
- Projects using unvetted workflows flagged as "Experimental"
- Security warnings displayed prominently in frontend
- Red indicator in header when in developer mode

**Use Cases:**
- Local development workstations
- Research and experimentation
- Prototyping with untrusted workflows

---

## Architecture Components

### 1. Workflow Vetting Service

**Purpose:** Validate and authorize ComfyUI workflows before execution

**Location:** `backend/services/workflow_vetting.py`

**Functionality by Tier:**

#### Production Mode
```python
class ProductionVettingPolicy:
    def validate(self, workflow):
        # Only allow pre-approved nodes from allow-list
        allowed_nodes = self.load_platform_allowlist()
        for node in workflow.nodes:
            if node.type not in allowed_nodes:
                raise SecurityViolation(f"Node {node.type} not approved")

        # Only allow vetted models from internal repository
        for model_ref in workflow.models:
            if not self.is_model_vetted(model_ref):
                raise SecurityViolation(f"Model {model_ref} not vetted")

        return True
```

#### Self-Hosted Production Mode
```python
class SelfHostedVettingPolicy:
    def validate(self, workflow):
        # Check against admin-configured allow-list
        admin_config = self.load_admin_allowlist()

        for node in workflow.nodes:
            if node.requires_custom_repo():
                if node.repo_url not in admin_config.approved_repos:
                    raise SecurityViolation(f"Repo {node.repo_url} not approved by admin")

        # Allow admin-approved model sources
        for model_ref in workflow.models:
            source = self.get_model_source(model_ref)
            if source not in admin_config.approved_sources:
                raise SecurityViolation(f"Model source {source} not approved")

        return True
```

#### Developer Mode
```python
class DeveloperVettingPolicy:
    def validate(self, workflow):
        # Log all external dependencies
        logger.warning(f"DEVELOPER MODE: Allowing workflow {workflow.id}")

        for node in workflow.nodes:
            if node.requires_custom_repo():
                logger.warning(f"Fetching from untrusted repo: {node.repo_url}")

        for model_ref in workflow.models:
            logger.warning(f"Using model: {model_ref}")

        # Always allow (but log)
        return True
```

**Database Schema:**
```sql
CREATE TABLE workflow_allowlist (
    id SERIAL PRIMARY KEY,
    execution_mode VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL, -- 'node', 'model', 'repo'
    resource_identifier TEXT NOT NULL,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    UNIQUE(execution_mode, resource_type, resource_identifier)
);
```

---

### 2. Sandboxed Execution Environment

**Purpose:** Isolate untrusted workflow execution from host system

**Technology Options:**

1. **gVisor** (Recommended for Kubernetes)
   - User-space kernel for container isolation
   - Strong syscall filtering
   - Lower overhead than VMs

2. **Firecracker** (Recommended for bare-metal/EC2)
   - Lightweight micro-VMs
   - KVM-based isolation
   - Sub-second startup

**Docker Compose Configuration:**

```yaml
ai_worker:
  # ... existing config ...
  security_opt:
    - no-new-privileges:true
    - seccomp:unconfined  # gVisor provides syscall filtering
  runtime: runsc  # gVisor runtime

  # Network isolation (production mode)
  networks:
    - isolated_workers

  # No internet access in production mode
  dns: []  # Disable DNS resolution
```

**Network Policy (Kubernetes):**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-worker-isolation
spec:
  podSelector:
    matchLabels:
      app: ai-worker
  policyTypes:
    - Egress
  egress:
    # Production: Only internal artifact repository
    - to:
      - podSelector:
          matchLabels:
            app: artifact-repository
      ports:
        - protocol: TCP
          port: 443

    # Self-hosted: Admin-configured allowlist
    # (managed via ConfigMap)
```

---

### 3. Identity and Access Management (IAM)

**Purpose:** Authenticate users and authorize API operations

**Technology Stack:**
- **Authentication:** Keycloak (OIDC/SAML) or Auth0
- **Authorization:** Role-Based Access Control (RBAC)
- **Token Management:** JWT with short expiration

**Roles:**

| Role | Permissions |
|------|-------------|
| **Admin** | All operations, user management, system configuration |
| **User** | CRUD on own projects, read shared projects, execute workflows |
| **Viewer** | Read-only access to shared projects |

**Database Schema:**

```sql
-- User table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    external_id VARCHAR(255) UNIQUE, -- From OIDC provider
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Row-Level Security (RLS)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY projects_isolation ON projects
    USING (owner_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY projects_admin_access ON projects
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = current_setting('app.current_user_id')::UUID
            AND role = 'admin'
        )
    );
```

**API Middleware:**

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, settings.jwt_secret)
        user_id = payload.get("sub")

        # Set user context for RLS
        await db.execute(f"SET app.current_user_id = '{user_id}'")

        return User(id=user_id, role=payload.get("role"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/projects")
async def list_projects(user: User = Depends(get_current_user)):
    # RLS automatically filters to user's projects
    return await db.query(Project).all()
```

---

### 4. Secrets Management

**Purpose:** Securely store and retrieve sensitive credentials

**Tier-Specific Implementation:**

#### Production Mode (Mandatory Vault)

```python
from hvac import Client as VaultClient

class ProductionSecretsManager:
    def __init__(self):
        vault_addr = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")

        if not vault_addr or not vault_token:
            raise StartupError("VAULT_ADDR and VAULT_TOKEN required in production mode")

        self.client = VaultClient(url=vault_addr, token=vault_token)

    def get_secret(self, path: str) -> str:
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response['data']['data']
```

#### Self-Hosted Production Mode (Vault Recommended)

```python
class SelfHostedSecretsManager:
    def __init__(self):
        vault_addr = os.getenv("VAULT_ADDR")

        if vault_addr:
            self.backend = VaultBackend(vault_addr)
        else:
            logger.warning(
                "⚠️  WARNING: Using .env for secrets in self-hosted-production mode. "
                "This is NOT recommended for production. Please configure a vault."
            )
            self.backend = EnvFileBackend()
```

#### Developer Mode (Fallback to .env)

```python
class DeveloperSecretsManager:
    def __init__(self):
        logger.warning(
            "⚠️  DEVELOPER MODE: Using .env for secrets. "
            "This is insecure and only suitable for local development."
        )
        self.backend = EnvFileBackend()
```

**Vault Structure:**

```
secret/
├── videofoundry/
│   ├── production/
│   │   ├── database
│   │   ├── aws_credentials
│   │   ├── jwt_secret
│   │   └── api_keys/
│   │       ├── runway
│   │       └── stability
│   ├── self-hosted/
│   │   └── [customer-specific]
│   └── developer/
│       └── [optional]
```

---

### 5. Context-Aware Storage

**Purpose:** Provide secure, scalable storage with tier-appropriate fallbacks

**Storage Backend Selection:**

```python
class StorageFactory:
    @staticmethod
    def create_backend(execution_mode: str):
        if execution_mode == "production":
            # S3 is mandatory
            if not settings.s3_bucket:
                raise StartupError("S3_BUCKET required in production mode")
            return S3StorageBackend()

        elif execution_mode == "self-hosted-production":
            # Prefer S3, allow local with warning
            if settings.s3_bucket:
                return S3StorageBackend()
            else:
                logger.warning(
                    "⚠️  Using local storage in self-hosted-production mode. "
                    "For production deployments, S3 is strongly recommended."
                )
                return LocalStorageBackend(volume="/videos")

        else:  # developer
            # Default to local for ease of setup
            return LocalStorageBackend(volume="/videos")
```

**S3 User Isolation (Production):**

```python
class S3StorageBackend:
    def get_user_prefix(self, user_id: str) -> str:
        return f"users/{user_id}/"

    async def upload(self, user_id: str, file_data: bytes, filename: str) -> str:
        key = f"{self.get_user_prefix(user_id)}{filename}"

        # Upload with user-specific prefix
        await self.s3_client.put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=file_data,
            ServerSideEncryption="AES256",
            Metadata={"user_id": user_id}
        )

        return key

    async def download(self, user_id: str, key: str) -> bytes:
        # Verify user owns this object
        if not key.startswith(self.get_user_prefix(user_id)):
            raise PermissionDenied("Access to this file is not allowed")

        response = await self.s3_client.get_object(
            Bucket=settings.s3_bucket,
            Key=key
        )

        return await response['Body'].read()
```

**Local Storage (Developer/Self-Hosted):**

```python
class LocalStorageBackend:
    def __init__(self, volume: str):
        self.base_path = Path(volume)

        # Ensure writes are confined to volume
        if not self.base_path.is_absolute():
            raise ValueError("Storage volume must be absolute path")

    async def upload(self, user_id: str, file_data: bytes, filename: str) -> str:
        user_dir = self.base_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        file_path = user_dir / filename

        # Prevent path traversal
        if not file_path.resolve().is_relative_to(self.base_path.resolve()):
            raise SecurityViolation("Path traversal detected")

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        return str(file_path.relative_to(self.base_path))
```

---

## Security Controls Matrix

| Control | Production | Self-Hosted Production | Developer |
|---------|------------|------------------------|-----------|
| **Workflow Vetting** | ✅ Strict allow-list | ✅ Admin allow-list | ⚠️ Log-and-warn |
| **Kernel Sandboxing** | ✅ Mandatory | ✅ Mandatory | ✅ Mandatory |
| **Internet Egress** | ❌ Blocked | ⚠️ Admin-controlled | ✅ Proxied/logged |
| **IAM/RBAC** | ✅ Mandatory | ⚠️ Recommended | ❌ Optional |
| **Database RLS** | ✅ Mandatory | ⚠️ Recommended | ❌ Optional |
| **Vault Secrets** | ✅ Mandatory | ⚠️ Recommended | ❌ Fallback .env |
| **Cloud Storage** | ✅ Mandatory | ⚠️ Recommended | ❌ Local default |
| **Audit Logging** | ✅ Full | ✅ Full | ⚠️ Basic |
| **Startup Validation** | ✅ Fail on missing | ⚠️ Warn on missing | ℹ️ Permissive |

**Legend:**
- ✅ Mandatory / Enforced
- ⚠️ Recommended / Configurable
- ❌ Disabled / Not enforced
- ℹ️ Informational only

---

## Threat Model

### Primary Threats

1. **Remote Code Execution (RCE) via Untrusted Workflows**
   - **Attack Vector:** Malicious ComfyUI workflow executes arbitrary code
   - **Mitigation:** Workflow vetting + kernel-level sandboxing
   - **Residual Risk:** LOW (defense in depth)

2. **Data Exfiltration**
   - **Attack Vector:** Compromised workflow attempts to steal user data
   - **Mitigation:** Network egress controls + storage isolation + RLS
   - **Residual Risk:** LOW (production), MEDIUM (self-hosted), HIGH (developer)

3. **Privilege Escalation**
   - **Attack Vector:** User attempts to access other users' data/projects
   - **Mitigation:** RBAC + Row-Level Security + API authorization
   - **Residual Risk:** LOW (with IAM), HIGH (without IAM)

4. **Supply Chain Attack**
   - **Attack Vector:** Malicious custom node or model repository
   - **Mitigation:** Strict allow-listing + internal artifact repository
   - **Residual Risk:** LOW (production), MEDIUM (self-hosted), HIGH (developer)

5. **Secrets Leakage**
   - **Attack Vector:** Exposure of API keys, database credentials
   - **Mitigation:** Vault-based secrets management + no hardcoded secrets
   - **Residual Risk:** LOW (with vault), MEDIUM (.env with proper permissions)

### Attack Surface by Tier

| Tier | Attack Surface | Risk Level |
|------|----------------|------------|
| **Production** | Minimal (trusted workflows only) | **LOW** |
| **Self-Hosted Production** | Medium (admin-approved sources) | **MEDIUM** |
| **Developer** | High (arbitrary code execution) | **HIGH** |

---

## Deployment Scenarios

### Scenario 1: Multi-Tenant SaaS (Production Mode)

```bash
# Environment Configuration
JYNCO_EXECUTION_MODE=production
VAULT_ADDR=https://vault.company.com
VAULT_TOKEN=s.xyz123
S3_BUCKET=videofoundry-prod
OIDC_PROVIDER_URL=https://auth.company.com
DATABASE_URL=postgresql://...

# Required Infrastructure
# - HashiCorp Vault or AWS Secrets Manager
# - S3 or compatible object storage
# - Keycloak/Auth0 for authentication
# - gVisor-enabled Kubernetes cluster
# - Network policies enforcing egress restrictions
```

**Checklist:**
- [ ] Vault configured and accessible
- [ ] S3 bucket with IAM policies for user isolation
- [ ] OIDC/SAML provider integrated
- [ ] Database RLS policies applied
- [ ] gVisor runtime installed
- [ ] Network policies deployed
- [ ] Workflow allow-list populated
- [ ] Audit logging configured

---

### Scenario 2: Enterprise Self-Hosted (Self-Hosted Production Mode)

```bash
# Environment Configuration
JYNCO_EXECUTION_MODE=self-hosted-production
VAULT_ADDR=https://vault.internal.corp  # Optional but recommended
S3_BUCKET=videofoundry-internal  # Optional, can use local
ADMIN_ALLOWLIST_PATH=/config/allowlist.yaml

# Recommended Infrastructure
# - Internal vault (recommended)
# - S3-compatible storage (MinIO acceptable)
# - Basic authentication or LDAP integration
# - Docker with gVisor runtime
```

**Checklist:**
- [ ] Admin allow-list configured
- [ ] Vault or secure .env storage
- [ ] Storage backend selected (S3 or local volume)
- [ ] Egress proxy configured (if needed)
- [ ] Audit logging enabled
- [ ] Regular security reviews scheduled

---

### Scenario 3: Local Development (Developer Mode)

```bash
# Environment Configuration
JYNCO_EXECUTION_MODE=developer
DATABASE_URL=postgresql://localhost:5432/videofoundry
REDIS_URL=redis://localhost:6379

# Minimal Infrastructure
# - Docker Desktop
# - Local volumes for storage
# - .env file for secrets (acceptable)
```

**Checklist:**
- [ ] Understand security risks of developer mode
- [ ] Never use on public networks
- [ ] Do not process sensitive data
- [ ] Do not expose ports to internet
- [ ] Treat all workflows as potentially malicious

---

## Implementation Guide

### Phase 1: Core Infrastructure (Week 1-2)

1. **Execution Mode Configuration**
   - Add `JYNCO_EXECUTION_MODE` to settings
   - Implement mode validation and startup checks
   - Add mode indicator to logs and UI

2. **Workflow Vetting Service**
   - Create `backend/services/workflow_vetting.py`
   - Implement three policy classes
   - Add allowlist database table and management API

3. **Sandboxing Setup**
   - Install gVisor runtime
   - Update docker-compose with security options
   - Test sandbox escape prevention

### Phase 2: IAM & Access Control (Week 3-4)

4. **Authentication Integration**
   - Integrate Keycloak/Auth0
   - Add JWT middleware
   - Implement role-based authorization

5. **Row-Level Security**
   - Apply RLS policies to all user-scoped tables
   - Add user context setting in middleware
   - Test multi-user isolation

### Phase 3: Secrets & Storage (Week 5-6)

6. **Secrets Management**
   - Implement vault integration
   - Add tier-specific secrets managers
   - Migrate existing .env secrets to vault (production)

7. **Context-Aware Storage**
   - Implement storage backend factory
   - Add S3 user isolation
   - Add local storage path traversal protection

### Phase 4: Network & Monitoring (Week 7-8)

8. **Network Policies**
   - Configure egress restrictions
   - Set up admin-configurable proxy (self-hosted)
   - Implement DNS blocking (production)

9. **Audit Logging**
   - Add comprehensive audit trail
   - Log all security-relevant events
   - Implement log aggregation and alerting

### Phase 5: Testing & Documentation (Week 9-10)

10. **Security Testing**
    - Penetration testing
    - Attempt sandbox escapes
    - Test authorization bypass attempts
    - Verify RLS effectiveness

11. **Documentation & Training**
    - Deployment guides for each tier
    - Security runbooks
    - Incident response procedures

---

## Compliance & Audit

### Audit Trail Requirements

All security-relevant events must be logged with:
- Timestamp (UTC)
- User ID (if authenticated)
- Action performed
- Resource affected
- Outcome (success/failure)
- Source IP
- Execution mode

**Example Audit Log Entry:**

```json
{
  "timestamp": "2025-11-14T10:30:00Z",
  "event_type": "workflow.executed",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "execution_mode": "production",
  "workflow_id": "comfyui-video-gen-v1",
  "vetting_result": "approved",
  "resources_accessed": ["model:stable-diffusion-v1.5"],
  "outcome": "success",
  "source_ip": "192.168.1.100"
}
```

### Compliance Mappings

| Requirement | Control | Evidence |
|-------------|---------|----------|
| **SOC 2 - CC6.1** (Logical access) | IAM/RBAC + RLS | User audit logs |
| **SOC 2 - CC6.6** (Encryption) | S3 SSE + TLS | Storage config |
| **SOC 2 - CC7.2** (Security monitoring) | Audit logging | Log retention |
| **GDPR Art. 25** (Data protection by design) | RLS + user isolation | Architecture docs |
| **GDPR Art. 32** (Security measures) | Sandboxing + encryption | Pen test reports |

---

## Appendix A: Configuration Reference

### Environment Variables

```bash
# Execution Mode (REQUIRED)
JYNCO_EXECUTION_MODE=production|self-hosted-production|developer

# Secrets Management
VAULT_ADDR=https://vault.example.com
VAULT_TOKEN=s.xyz123
VAULT_NAMESPACE=videofoundry  # Optional

# Authentication (Production/Self-Hosted)
OIDC_PROVIDER_URL=https://auth.example.com
OIDC_CLIENT_ID=videofoundry
OIDC_CLIENT_SECRET=<from-vault>

# Storage
S3_BUCKET=videofoundry-prod
S3_ENDPOINT=https://s3.amazonaws.com  # Optional for S3-compatible
AWS_ACCESS_KEY_ID=<from-vault>
AWS_SECRET_ACCESS_KEY=<from-vault>
AWS_REGION=us-east-1

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Sandboxing
DOCKER_RUNTIME=runsc  # gVisor
ENABLE_NETWORK_ISOLATION=true

# Admin Configuration (Self-Hosted)
ADMIN_ALLOWLIST_PATH=/config/allowlist.yaml
EGRESS_PROXY_URL=http://proxy.internal:8080
EGRESS_ALLOWLIST=github.com,huggingface.co

# Audit Logging
AUDIT_LOG_PATH=/var/log/videofoundry/audit.log
AUDIT_LOG_LEVEL=INFO
AUDIT_LOG_RETENTION_DAYS=90
```

### Allowlist Configuration (YAML)

```yaml
# Production allowlist (managed by platform admins)
execution_mode: production
nodes:
  - type: "LoadImage"
    version: "1.0"
    approved_by: "security-team"
    approved_at: "2025-11-01"

  - type: "SaveImage"
    version: "1.0"
    approved_by: "security-team"
    approved_at: "2025-11-01"

models:
  - identifier: "stable-diffusion-v1-5"
    source: "internal-repository"
    checksum: "sha256:abc123..."
    approved_by: "security-team"
    approved_at: "2025-11-01"

repositories:
  # None allowed in production mode
  - null

---
# Self-hosted allowlist (managed by instance admin)
execution_mode: self-hosted-production
nodes:
  # Inherit all production nodes
  - inherit: production

  # Additional custom nodes approved by admin
  - type: "CustomVideoNode"
    repository: "https://github.com/company/custom-nodes"
    branch: "v1.0.0"
    approved_by: "admin@company.com"
    approved_at: "2025-11-10"

models:
  - identifier: "company-fine-tuned-model"
    source: "https://huggingface.co/company/model"
    approved_by: "admin@company.com"
    approved_at: "2025-11-10"

repositories:
  - url: "https://github.com/company/custom-nodes"
    allowed_branches: ["v1.0.0", "v1.1.0"]
    approved_by: "admin@company.com"
```

---

## Appendix B: Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                ┌───────────▼──────────┐
                │   Load Balancer      │
                │   (TLS Termination)  │
                └───────────┬──────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐
│   Frontend     │  │   API Gateway  │  │   Keycloak  │
│   (React)      │  │   (FastAPI)    │  │   (IAM)     │
└────────────────┘  └───────┬────────┘  └─────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
        ┌───────▼─────┐ ┌──▼────┐ ┌────▼─────┐
        │  PostgreSQL │ │ Redis │ │ RabbitMQ │
        │  (with RLS) │ └───────┘ └────┬─────┘
        └─────────────┘                │
                                       │
                        ┌──────────────┼──────────────┐
                        │              │              │
                ┌───────▼────────┐ ┌───▼───────┐ ┌───▼───────┐
                │  AI Worker     │ │ AI Worker │ │ AI Worker │
                │  (Sandboxed)   │ │(Sandboxed)│ │(Sandboxed)│
                └────────┬───────┘ └─────┬─────┘ └─────┬─────┘
                         │               │             │
                         └───────────────┼─────────────┘
                                         │
                         ┌───────────────▼──────────────┐
                         │  Internal Artifact Repo      │
                         │  (Vetted Models & Nodes)     │
                         └──────────────────────────────┘
```

### Execution Mode Decision Tree

```
[Startup]
    │
    ▼
[Read JYNCO_EXECUTION_MODE]
    │
    ├─[production]──────────┐
    │                       ▼
    │               [Validate Vault]──[FAIL?]──► [EXIT with error]
    │                       │
    │                       ▼
    │               [Validate S3]────[FAIL?]──► [EXIT with error]
    │                       │
    │                       ▼
    │               [Validate IAM]───[FAIL?]──► [EXIT with error]
    │                       │
    │                       ▼
    │               [Start with Production Policy]
    │
    ├─[self-hosted-production]──┐
    │                           ▼
    │                   [Validate Vault]──[FAIL?]──► [WARN + continue]
    │                           │
    │                           ▼
    │                   [Check S3]──[MISSING?]──► [WARN + use local]
    │                           │
    │                           ▼
    │                   [Start with Self-Hosted Policy]
    │
    └─[developer]───────────────┐
                                ▼
                        [Show Security Warnings]
                                │
                                ▼
                        [Start with Developer Policy]
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-01 | Initial draft | Security Team |
| 2.0 | 2025-10-15 | Added two-tier model | Security Team |
| 3.0 | 2025-11-14 | Three-tier model with self-hosted tier | Security Agent |

---

## References

1. OWASP Top 10 - https://owasp.org/www-project-top-ten/
2. gVisor Documentation - https://gvisor.dev/
3. Firecracker Documentation - https://firecracker-microvm.github.io/
4. HashiCorp Vault - https://www.vaultproject.io/
5. SOC 2 Compliance Guide - https://www.aicpa.org/soc
6. GDPR Technical Guidelines - https://gdpr.eu/

---

**END OF DOCUMENT**
