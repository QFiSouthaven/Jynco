# High-Level Security Design Proposal for Video Foundry (Jynco) - Version 3.0

**TO:** Video Foundry Development Team
**FROM:** The Security Agent
**SUBJECT:** REFINED Security Architecture Proposal (v3.0)
**STATUS:** FINAL
**DATE:** January 2025

---

## 1. Executive Summary

Following peer review of the v2.0 architecture, this document presents the final, refined security design. The previous version correctly established a tiered model to balance security and usability. However, feedback astutely pointed out that the binary `production` vs. `developer` distinction failed to adequately serve the crucial use case of self-hosted production environments.

This revised design addresses that gap by evolving the architecture into a more granular **three-tier security model**. The new tiers—`production` (for multi-tenant SaaS), `self-hosted-production`, and `developer`—provide tailored security postures for each distinct deployment scenario.

The core principle remains: **provide ironclad security by default**, but offer explicit, risk-aware configurations that empower users without compromising foundational security guarantees. This approach ensures Video Foundry can be a secure multi-tenant service, a resilient self-hosted enterprise tool, and a flexible R&D platform.

---

## 2. Core Security Principles (Unchanged)

Our architecture will continue to be guided by these foundational principles:

1. **Zero Trust**: No component is trusted by default. All interactions require authentication and authorization.
2. **Defense in Depth**: Multiple, layered security controls prevent a single failure from compromising the system.
3. **Principle of Least Privilege**: Components are granted the minimum permissions necessary for their function, tailored to their operational context.
4. **Secure by Default**: The most secure configuration is the default. Less secure options for development or experimentation require explicit user action and acknowledgment of risk.
5. **Context-Aware Security**: Controls and policies adapt based on the deployment environment and the selected execution mode.

---

## 3. Proposed Architectural Remediation (v3.0)

### 3.1. Mitigating RCE with a Three-Tier Execution Model

The primary RCE threat from untrusted workflows will be mitigated with a configurable, three-tier model. The system's mode is set by an environment variable (e.g., `JYNCO_EXECUTION_MODE=production | self-hosted-production | developer`).

#### 3.1.1. Tier 1: `production` Mode (For Multi-Tenant SaaS)

This is the **default and most restrictive mode**, mandatory for any public-facing, multi-tenant deployment.

**Strict Workflow Vetting Service:**
- The vetting service operates in a strict allow-list mode
- Only platform-administrator-approved ComfyUI nodes, models, and custom node repositories are permitted
- All workflow submissions are validated against the allow-list before execution

**Hardened, Isolated, and Muted AI Workers:**
- **Kernel-Level Sandboxing**: Each job runs in an ephemeral, single-use sandbox (gVisor or Firecracker micro-VM). This is non-negotiable.
- **No Internet Egress**: The sandbox has ZERO internet access
- **Immutable Infrastructure**: Workers pull exclusively from an Internal Artifact Repository containing only vetted assets
- **Resource Limits**: Strict CPU, memory, and disk quotas per job
- **Network Isolation**: Complete network segmentation between tenants

#### 3.1.2. Tier 2: `self-hosted-production` Mode (NEW)

This mode is designed for **secure, single-tenant, self-hosted deployments**, offering a balance of security and administrative flexibility.

**Administrator-Configurable Workflow Vetting:**
- The vetting service is mandatory
- The instance administrator can configure the allow-list
- Enables approval of specific custom node Git repositories or models for their private instance
- Admin UI for managing approved resources

**Hardened and Isolated AI Workers:**
- **Kernel-Level Sandboxing**: The strong sandbox from the Production Tier is still mandatory
- **Controlled Internet Egress**: The sandboxed environment is granted limited, auditable internet access via a proxy
- Egress is restricted to only the administrator-approved sources (e.g., specific Git repos, Hugging Face)
- All other traffic is blocked and logged
- **Audit Trail**: All network requests are logged for security review

#### 3.1.3. Tier 3: `developer` Mode (For Local/Private R&D)

This mode must be **explicitly enabled** and prioritizes flexibility for local development or private research.

**Permissive Workflow Vetting Service:**
- The service operates in a "log-and-warn" mode
- Allows dynamic fetching from arbitrary public Git repositories
- Logs verbose security warnings but does not block execution
- Clear warnings displayed in logs and UI

**Hardened, Isolated, and Audited AI Workers:**
- **Kernel-Level Sandboxing**: Sandboxing remains mandatory to prevent host-level compromise
- **General Internet Egress**: The sandbox has broader (but still proxied and logged) internet access to facilitate experimentation
- **UI/UX Warnings**: The frontend prominently flags projects using developer-mode workflows as "Experimental" and potentially insecure
- **Local-Only Recommendation**: Should only be used on trusted, non-production networks

---

### 3.2. Implementing Identity and Access Management (IAM)

This remains a non-negotiable requirement for any multi-user deployment (`production` and `self-hosted-production` modes).

**Centralized Authentication:**
- Integrate with an OIDC/SAML Identity Provider like Keycloak or Auth0
- Support for multiple authentication methods (OAuth2, SAML, LDAP)
- Session management with secure tokens (JWT with short expiry)
- MFA support for production environments

**Role-Based Access Control (RBAC):**
- Define roles: `SuperAdmin`, `Admin`, `User`, `Viewer`
- Granular permissions for projects, workflows, and system settings
- API-level authorization checks on all endpoints
- Audit logging of all access decisions

**Database Row-Level Security (RLS):**
- Implement RLS in PostgreSQL as a final defense
- Guarantees data isolation at the database level
- Prevents data leaks even if application-level checks fail
- Per-tenant isolation in production mode

---

### 3.3. Refined Approach to Data and Secrets Management

#### 3.3.1. Secure Secrets Management

**`production` & `self-hosted-production` Modes:**
- Using a dedicated vault (HashiCorp Vault, AWS Secrets Manager) is **mandatory**
- The application will fail to start if a vault configuration is not provided
- API keys, database credentials, and signing keys must be stored in vault
- Automatic secret rotation where supported

**`developer` Mode:**
- The system can fall back to using `.env` files for ease of setup
- Will issue a **prominent startup warning** about the insecurity of this method
- Recommendation to never use `.env` files with real production credentials

#### 3.3.2. Context-Aware Data Storage

The "intelligent fallback" for storage is now tied directly to the execution mode.

**`production` Mode:**
- Cloud storage (S3 or equivalent) is **mandatory**
- The local file storage option is disabled
- User data is strictly isolated using IAM policies scoped to user-specific prefixes
- Encryption at rest and in transit
- Bucket policies prevent cross-tenant access

**`self-hosted-production` Mode:**
- Cloud storage is the **recommended and default** option
- Administrators can explicitly configure the system to fall back to local file storage
- Writes are strictly confined to a dedicated Docker volume
- A startup warning will be issued when using local storage
- Backup and disaster recovery procedures must be documented

**`developer` Mode:**
- The system defaults to the secure local volume fallback
- Lowers the barrier to entry for local setup
- No cloud credentials required for getting started

---

## 4. High-Level Target Architecture Diagram

The logical flow is updated to reflect the policy variations across the three tiers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXECUTION MODE SELECTOR                      │
│  Environment Variable: JYNCO_EXECUTION_MODE                         │
│  Values: production | self-hosted-production | developer            │
└────────────┬────────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬─────────────────┬──────────────────┐
    │                 │                 │                  │
    ▼                 ▼                 ▼                  ▼
┌─────────┐     ┌──────────┐    ┌──────────┐      ┌──────────┐
│Frontend │     │ Backend  │    │ Workflow │      │   IAM    │
│   UI    │────▶│   API    │───▶│  Vetting │◀────▶│  System  │
└─────────┘     └────┬─────┘    │ Service  │      └──────────┘
                     │          └────┬─────┘
                     │               │
                     │          [Policy Enforcement]
                     │               │
                     ▼               ▼
              ┌──────────────────────────┐
              │    Job Queue (RabbitMQ)  │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │   AI Worker Orchestrator │
              │   (Execution Mode Aware) │
              └──────────┬───────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Sandboxed     │ │ Sandboxed     │ │ Sandboxed     │
│ AI Worker 1   │ │ AI Worker 2   │ │ AI Worker N   │
│ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │
│ │ gVisor or │ │ │ │ gVisor or │ │ │ │ gVisor or │ │
│ │Firecracker│ │ │ │Firecracker│ │ │ │Firecracker│ │
│ │  Sandbox  │ │ │ │  Sandbox  │ │ │ │  Sandbox  │ │
│ └─────┬─────┘ │ │ └─────┬─────┘ │ │ └─────┬─────┘ │
│       │       │ │       │       │ │       │       │
│   [Network    │ │   [Network    │ │   [Network    │
│    Policy]    │ │    Policy]    │ │    Policy]    │
│       │       │ │       │       │ │       │       │
└───────┼───────┘ └───────┼───────┘ └───────┼───────┘
        │                 │                 │
        └────────┬────────┴────────┬────────┘
                 │                 │
                 ▼                 ▼
        ┌─────────────┐   ┌─────────────┐
        │   Storage   │   │  Secrets    │
        │  (Mode-based│   │   Vault     │
        │  S3/Local)  │   │ (Mandatory) │
        └─────────────┘   └─────────────┘

Network Policy Enforcement by Mode:
─────────────────────────────────────
Production:              ❌ Internet  ✅ Internal Repo Only
Self-Hosted-Production:  🔒 Approved Sources Only (Proxied)
Developer:               ⚠️  Proxied & Logged Internet Access
```

---

## 5. Security Controls Matrix

| Security Control | Production | Self-Hosted-Prod | Developer |
|-----------------|------------|------------------|-----------|
| **Kernel Sandboxing** | ✅ Mandatory | ✅ Mandatory | ✅ Mandatory |
| **Internet Egress** | ❌ Blocked | 🔒 Approved Only | ⚠️ Logged |
| **Workflow Vetting** | ✅ Strict Allow-list | 🔧 Admin Config | ⚠️ Log & Warn |
| **IAM/RBAC** | ✅ Required | ✅ Required | ⚠️ Optional |
| **Secrets Vault** | ✅ Mandatory | ✅ Mandatory | ⚠️ Optional |
| **Cloud Storage** | ✅ Mandatory | 📋 Recommended | ⚠️ Optional |
| **Audit Logging** | ✅ Full | ✅ Full | ⚠️ Basic |
| **Multi-Tenancy** | ✅ Enforced | ❌ Single Tenant | ❌ Single User |

Legend:
- ✅ Fully Enforced
- 🔒 Restricted/Controlled
- 🔧 Configurable
- 📋 Recommended
- ⚠️ Optional/Warning
- ❌ Disabled/Not Applicable

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Implement execution mode selection system
- [ ] Create configuration validation for each mode
- [ ] Add startup warnings and mode detection
- [ ] Document mode requirements

### Phase 2: Workflow Vetting Service (Weeks 3-4)
- [ ] Build workflow vetting service architecture
- [ ] Implement allow-list management
- [ ] Create admin UI for self-hosted mode
- [ ] Add workflow validation endpoints

### Phase 3: Sandboxing & Isolation (Weeks 5-7)
- [ ] Integrate gVisor or Firecracker
- [ ] Implement network policies per mode
- [ ] Create ephemeral worker containers
- [ ] Add resource limiting

### Phase 4: IAM Integration (Weeks 8-10)
- [ ] Integrate OIDC/SAML authentication
- [ ] Implement RBAC system
- [ ] Add PostgreSQL RLS
- [ ] Create audit logging

### Phase 5: Secrets & Storage (Weeks 11-12)
- [ ] Integrate secrets vault
- [ ] Implement mode-aware storage
- [ ] Add encryption at rest
- [ ] Create backup procedures

### Phase 6: Testing & Hardening (Weeks 13-14)
- [ ] Security penetration testing
- [ ] Performance testing under load
- [ ] Documentation completion
- [ ] Compliance review

---

## 7. Risk Assessment

### Residual Risks (After Implementation)

**High Priority:**
- **Zero-Day Vulnerabilities in Sandbox**: Even with gVisor/Firecracker, kernel exploits exist
  - *Mitigation*: Keep sandbox software updated, monitor CVE feeds, consider defense-in-depth with network isolation

**Medium Priority:**
- **Administrator Misconfiguration (Self-Hosted)**: Admin may approve malicious resources
  - *Mitigation*: Provide clear documentation, security training, audit logging

**Low Priority:**
- **Developer Mode Misuse**: Users may run developer mode in production
  - *Mitigation*: Strong warnings, documentation, possibly require explicit flag

### Threat Modeling

**Threat 1: Malicious Workflow Execution (RCE)**
- *Attack Vector*: User uploads workflow with malicious custom nodes
- *Current Risk*: HIGH
- *Post-Implementation Risk*: LOW (production), MEDIUM (self-hosted), MEDIUM (developer)

**Threat 2: Data Exfiltration**
- *Attack Vector*: Compromised worker attempts to steal user data
- *Current Risk*: MEDIUM
- *Post-Implementation Risk*: LOW (network isolation + RLS)

**Threat 3: Privilege Escalation**
- *Attack Vector*: User attempts to access other users' resources
- *Current Risk*: MEDIUM (no IAM currently)
- *Post-Implementation Risk*: LOW (RBAC + RLS)

---

## 8. Compliance Considerations

### GDPR (EU Users)
- ✅ Data isolation per tenant
- ✅ Encryption at rest and in transit
- ✅ Audit logging for data access
- ✅ Right to deletion support
- ⚠️ Need: Data Processing Agreement (DPA) templates

### SOC 2 (Enterprise Customers)
- ✅ Access controls (RBAC)
- ✅ Encryption
- ✅ Audit logging
- ✅ Change management (git-based)
- ⚠️ Need: Formal incident response procedures

### HIPAA (Healthcare Use Cases)
- ⚠️ Additional requirements needed:
  - Business Associate Agreement (BAA)
  - Enhanced audit logging
  - Automatic session timeout
  - PHI handling procedures

---

## 9. Operational Considerations

### Monitoring & Alerting

**Production Mode:**
- Alert on any vetting service rejections
- Monitor sandbox escape attempts
- Track resource exhaustion
- Alert on authentication failures

**Self-Hosted-Production Mode:**
- Alert on unapproved resource access attempts
- Monitor egress proxy logs
- Track admin configuration changes

**Developer Mode:**
- Log all warnings
- Track workflow sources
- No alerts (non-production)

### Performance Impact

**Expected Overhead:**
- Sandboxing: ~5-10% performance overhead
- Network proxy: ~2-5% latency increase
- Workflow vetting: <100ms per submission
- IAM checks: <10ms per request

**Mitigation Strategies:**
- Cache vetting decisions
- Optimize sandbox startup time
- Use connection pooling for IAM
- Implement CDN for static assets

---

## 10. Developer Experience

### Getting Started (Developer Mode)

```bash
# Clone repo
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco

# Set developer mode
export JYNCO_EXECUTION_MODE=developer

# Start services (no vault or cloud storage needed!)
make up

# See security warnings in logs
make logs
```

### Migrating to Production

```bash
# Set production mode
export JYNCO_EXECUTION_MODE=production

# Configure required services
export VAULT_ADDR=https://vault.example.com
export S3_BUCKET=my-video-foundry-bucket

# Set up IAM
export OIDC_PROVIDER=https://auth.example.com

# Deployment will fail if any required config is missing
make deploy-prod
```

---

## 11. Documentation Requirements

### For Users
- [ ] Security overview for each mode
- [ ] Workflow safety guidelines
- [ ] Data handling policies
- [ ] Incident reporting procedures

### For Administrators
- [ ] Self-hosted installation guide
- [ ] Security hardening checklist
- [ ] Backup and recovery procedures
- [ ] Monitoring setup guide

### For Developers
- [ ] Security architecture overview
- [ ] Contribution security guidelines
- [ ] Testing security controls
- [ ] Vulnerability disclosure policy

---

## 12. Success Criteria

The implementation will be considered successful when:

1. ✅ All three execution modes are fully functional
2. ✅ Production mode passes penetration testing
3. ✅ Zero RCE vulnerabilities in production mode
4. ✅ Developer mode enables fast onboarding (<5 min to first video)
5. ✅ Self-hosted mode satisfies enterprise customers
6. ✅ Documentation is complete and clear
7. ✅ Performance overhead is <10%
8. ✅ Team is trained on security practices

---

## 13. Conclusion

This three-tier security architecture provides:

- **Uncompromising security** for multi-tenant SaaS deployments
- **Practical flexibility** for self-hosted enterprise users
- **Rapid iteration** for researchers and developers

By making security mode-aware and configuration-driven, we achieve both our security imperatives and our usability goals. The system is secure by default, but can be explicitly configured for different trust models based on deployment context.

### Next Steps

1. **Review & Approval**: Stakeholder review of this proposal
2. **Implementation Planning**: Detailed technical design documents
3. **Prototype**: Build proof-of-concept for each mode
4. **Testing**: Security audit and penetration testing
5. **Documentation**: Complete user and admin guides
6. **Rollout**: Phased deployment starting with developer mode

---

**Document Version:** 3.0
**Last Updated:** January 2025
**Next Review:** Q2 2025

---

## Appendix A: Configuration Examples

### Production Mode (.env)
```bash
JYNCO_EXECUTION_MODE=production
VAULT_ADDR=https://vault.company.com
VAULT_TOKEN=hvs.xxx
S3_BUCKET=video-foundry-prod
OIDC_PROVIDER=https://auth.company.com
ENABLE_RLS=true
SANDBOX_TYPE=gvisor
NETWORK_EGRESS=blocked
```

### Self-Hosted Production Mode (.env)
```bash
JYNCO_EXECUTION_MODE=self-hosted-production
VAULT_ADDR=https://vault.internal
VAULT_TOKEN=hvs.yyy
STORAGE_TYPE=local  # or s3
APPROVED_GIT_REPOS=github.com/myorg/*,gitlab.internal/*
EGRESS_PROXY=http://proxy.internal:3128
SANDBOX_TYPE=firecracker
```

### Developer Mode (.env)
```bash
JYNCO_EXECUTION_MODE=developer
# Minimal config needed!
DATABASE_URL=postgresql://localhost/videofoundry
REDIS_URL=redis://localhost:6379
# No vault, no cloud storage, no IAM required
```

---

## Appendix B: Security Checklist

### Pre-Deployment Security Checklist

**For Production Deployments:**
- [ ] Execution mode set to `production`
- [ ] Vault configured and accessible
- [ ] S3 bucket created with encryption
- [ ] IAM/OIDC provider integrated
- [ ] Database RLS policies enabled
- [ ] Network egress blocked in workers
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring and alerting enabled
- [ ] Incident response plan documented
- [ ] Security audit completed
- [ ] Compliance review passed

**For Self-Hosted Deployments:**
- [ ] Execution mode set to `self-hosted-production`
- [ ] Vault configured
- [ ] Approved resource list created
- [ ] Egress proxy configured
- [ ] Backup procedures tested
- [ ] Admin accounts secured with MFA
- [ ] Network isolation verified
- [ ] Audit logging enabled

**For Developer Setups:**
- [ ] Execution mode set to `developer`
- [ ] Running on trusted local network
- [ ] Not using production credentials
- [ ] Security warnings acknowledged
- [ ] Local firewall enabled

---

**END OF DOCUMENT**
