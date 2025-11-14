# Video Foundry - Security Best Practices

This document provides security best practices for Video Foundry deployments across all three execution modes.

---

## Table of Contents

1. [General Security Principles](#general-security-principles)
2. [Production Mode Best Practices](#production-mode-best-practices)
3. [Self-Hosted Production Best Practices](#self-hosted-production-best-practices)
4. [Developer Mode Best Practices](#developer-mode-best-practices)
5. [Common Security Checklist](#common-security-checklist)
6. [Incident Response](#incident-response)
7. [Compliance Guidelines](#compliance-guidelines)

---

## General Security Principles

### Defense in Depth

Never rely on a single security control. Layer multiple controls:
- Application-level authentication
- Database-level row security
- Network-level isolation
- Kernel-level sandboxing

### Principle of Least Privilege

Grant the minimum permissions necessary:
- Database users should have limited permissions
- API keys should be scoped to specific resources
- Workers should only access their assigned tasks
- Admin accounts should be used sparingly

### Secure by Default

- Default to the most secure configuration (production mode)
- Require explicit action to reduce security
- Show warnings when security is relaxed
- Make insecure options obvious

### Regular Security Reviews

- Weekly: Review audit logs
- Monthly: Check for dependency vulnerabilities
- Quarterly: Full security audit
- Annually: Penetration testing

---

## Production Mode Best Practices

### Configuration Management

**✅ DO:**
- Use HashiCorp Vault or AWS Secrets Manager for all secrets
- Enable database Row-Level Security (RLS)
- Use gVisor or Firecracker for sandboxing
- Block all internet egress from workers
- Enable strict workflow vetting
- Use S3 with bucket policies for storage
- Enable MFA for all admin accounts
- Set up comprehensive audit logging

**❌ DON'T:**
- Never store secrets in environment variables
- Never use docker-only sandboxing
- Never allow internet access from workers
- Never skip workflow vetting
- Never use local file storage
- Never disable audit logging

### Network Security

```yaml
# Required network configuration
NETWORK_EGRESS=blocked
SANDBOX_TYPE=gvisor  # or firecracker

# Ensure workers have no internet access
# Only internal artifact repository access
```

### Access Control

1. **Authentication:**
   - Use OIDC/SAML with a trusted provider
   - Enforce MFA for all accounts
   - Implement session timeouts (max 1 hour)
   - Use secure, httpOnly cookies

2. **Authorization:**
   - Implement RBAC with least privilege
   - Use database RLS for data isolation
   - Log all authorization decisions
   - Regular access reviews

3. **API Security:**
   - Rate limiting on all endpoints
   - Input validation on all requests
   - CSRF protection
   - Proper CORS configuration

### Data Protection

1. **Encryption:**
   - TLS 1.3 for all connections
   - Encryption at rest for S3
   - Encrypted database connections
   - Secure key management via vault

2. **Data Isolation:**
   - S3 bucket policies per tenant
   - Database RLS policies
   - No shared resources between tenants
   - Separate processing queues

### Monitoring & Alerting

**Critical Alerts:**
- Workflow vetting rejections
- Sandbox escape attempts
- Authentication failures (>5 in 5 min)
- Unauthorized access attempts
- Resource exhaustion
- Unexpected network connections

**Monitoring Metrics:**
- Request rate and latency
- Error rates
- Worker resource usage
- Queue depth
- Storage usage
- Authentication success/failure rates

---

## Self-Hosted Production Best Practices

### Configuration Management

**✅ DO:**
- Use secrets vault (Vault or AWS Secrets Manager)
- Enable database RLS for multi-user deployments
- Use gVisor or Firecracker sandboxing
- Configure approved resource lists
- Use S3 or ensure local storage backups
- Enable comprehensive audit logging
- Document approved resources
- Regular security reviews

**❌ DON'T:**
- Don't use .env files for production secrets
- Don't skip sandbox configuration
- Don't allow unapproved external resources
- Don't disable audit logging
- Don't skip backups if using local storage

### Administrator Responsibilities

1. **Resource Approval:**
   - Vet custom ComfyUI nodes before approval
   - Review model sources for safety
   - Maintain approved Git repository list
   - Document approval decisions

2. **Network Configuration:**
   - Configure egress proxy properly
   - Restrict approved sources
   - Monitor network traffic
   - Review logs regularly

3. **User Management:**
   - Follow least privilege for user roles
   - Regular access reviews
   - Disable inactive accounts
   - Monitor for unusual activity

### Backup & Recovery

**For Local Storage:**
```bash
# Daily backups
0 2 * * * /scripts/backup-videos.sh

# Test restores monthly
# Document recovery procedures
# Store backups off-site
```

**For S3 Storage:**
- Enable versioning
- Configure lifecycle policies
- Set up cross-region replication
- Test restore procedures

### Approved Resources Management

Create and maintain `/etc/videofoundry/approved_nodes.json`:

```json
{
  "approved_git_repos": [
    "github.com/your-org/custom-nodes",
    "gitlab.internal/ai-team/comfyui-nodes"
  ],
  "approved_models": [
    "huggingface.co/your-org/*",
    "models.internal/*"
  ],
  "blocked_nodes": [
    "known-vulnerable-node",
    "unsafe-file-access"
  ],
  "last_updated": "2025-01-13T00:00:00Z",
  "reviewed_by": "security-team"
}
```

---

## Developer Mode Best Practices

### Configuration Management

**✅ DO:**
- Use developer mode only on trusted networks
- Keep the mode clearly labeled in UI
- Use test/dummy credentials
- Enable sandboxing even in dev mode
- Review workflow sources
- Keep dependencies updated

**❌ DON'T:**
- Never use developer mode in production
- Never use real production credentials
- Never expose developer mode to internet
- Never skip security warnings
- Don't run untrusted workflows without review

### Development Environment Security

1. **Local Network:**
   - Use firewall to block external access
   - Use VPN if accessing remotely
   - Don't expose ports to internet

2. **Credentials:**
   - Use separate dev credentials
   - Never commit credentials to git
   - Use `.env` only for development
   - Rotate credentials regularly

3. **Testing Security Features:**
```bash
# Test with production-like config locally
JYNCO_EXECUTION_MODE=self-hosted-production
SANDBOX_TYPE=gvisor
NETWORK_EGRESS=restricted
```

### Transitioning to Production

Before deploying to production:

- [ ] Change execution mode
- [ ] Set up secrets vault
- [ ] Configure cloud storage
- [ ] Enable IAM/authentication
- [ ] Configure strict sandboxing
- [ ] Enable audit logging
- [ ] Review all configurations
- [ ] Run security tests
- [ ] Document deployment
- [ ] Train operations team

---

## Common Security Checklist

### Pre-Deployment

- [ ] Execution mode properly configured
- [ ] Secrets vault configured (production/self-hosted)
- [ ] Database RLS enabled (multi-user)
- [ ] Sandboxing configured (gvisor/firecracker)
- [ ] Network policies enforced
- [ ] Workflow vetting configured
- [ ] Storage properly secured
- [ ] Audit logging enabled
- [ ] Monitoring configured
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Backups configured and tested
- [ ] Incident response plan documented
- [ ] Security audit completed

### Post-Deployment

- [ ] Monitor audit logs daily
- [ ] Review access logs weekly
- [ ] Check for security updates weekly
- [ ] Update dependencies monthly
- [ ] Review user access monthly
- [ ] Full security audit quarterly
- [ ] Penetration testing annually
- [ ] Disaster recovery drill annually

---

## Incident Response

### Security Incident Types

1. **Suspected Breach:**
   - Isolate affected systems
   - Review audit logs
   - Change credentials
   - Notify stakeholders
   - Document incident

2. **Sandbox Escape Attempt:**
   - Immediately stop affected worker
   - Review workflow that triggered escape
   - Check for system compromise
   - Update sandbox configuration
   - Report to security team

3. **Unauthorized Access:**
   - Lock affected account
   - Review access logs
   - Check for data exfiltration
   - Reset credentials
   - Document and report

4. **Data Leak:**
   - Identify scope of leak
   - Notify affected users
   - Review access controls
   - Implement additional controls
   - Document and report

### Incident Response Checklist

**Immediate (0-1 hour):**
- [ ] Identify and contain incident
- [ ] Stop active attacks
- [ ] Preserve evidence
- [ ] Notify incident response team
- [ ] Begin documentation

**Short-term (1-24 hours):**
- [ ] Assess damage
- [ ] Identify root cause
- [ ] Implement temporary fixes
- [ ] Notify stakeholders
- [ ] Continue documentation

**Long-term (1-7 days):**
- [ ] Implement permanent fixes
- [ ] Review and update policies
- [ ] Conduct post-mortem
- [ ] Update incident response plan
- [ ] Train team on lessons learned

### Contact Information

```
Security Team: security@videofoundry.dev
Incident Hotline: +1-xxx-xxx-xxxx
On-Call Rotation: oncall@videofoundry.dev
```

---

## Compliance Guidelines

### GDPR (EU Users)

**Requirements:**
- [ ] Data processing agreement
- [ ] User consent management
- [ ] Right to access (data export)
- [ ] Right to deletion
- [ ] Data breach notification (72 hours)
- [ ] Privacy policy
- [ ] Data retention policies

**Implementation:**
```python
# User data export
GET /api/v1/users/{user_id}/export

# User data deletion
DELETE /api/v1/users/{user_id}

# Audit all data access
LOG: User X accessed their data at T
```

### SOC 2

**Requirements:**
- [ ] Access controls (RBAC)
- [ ] Encryption at rest and in transit
- [ ] Audit logging
- [ ] Change management
- [ ] Incident response procedures
- [ ] Risk assessment
- [ ] Vendor management

### HIPAA (Healthcare Use Cases)

**Additional Requirements:**
- [ ] Business Associate Agreement (BAA)
- [ ] Enhanced audit logging
- [ ] Automatic session timeout
- [ ] PHI handling procedures
- [ ] Breach notification procedures
- [ ] Employee training

**Note:** HIPAA compliance requires additional controls beyond the base security architecture. Consult with a compliance expert before handling PHI.

---

## Security Tools & Scanning

### Regular Security Scans

```bash
# Dependency vulnerabilities
pip-audit
npm audit

# Python security issues
bandit -r backend/ workers/

# Container scanning
trivy image video-foundry:latest

# Secrets scanning
detect-secrets scan --all-files
```

### Automated Security Testing

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Dependency Check
        run: pip-audit

      - name: Bandit Scan
        run: bandit -r backend/ workers/

      - name: Secrets Scan
        run: detect-secrets scan
```

---

## Security Training

### For Developers

- Secure coding practices
- OWASP Top 10
- Authentication & authorization
- Input validation
- Secrets management
- Security testing

### For Administrators

- Access management
- Incident response
- Backup & recovery
- Security monitoring
- Compliance requirements
- Approved resource vetting

### For Users

- Strong password practices
- MFA usage
- Phishing awareness
- Incident reporting
- Data handling policies

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Security Proposal V3](./SECURITY_PROPOSAL_V3.md)
- [Implementation Roadmap](./SECURITY_IMPLEMENTATION_ROADMAP.md)

---

## Questions or Concerns?

Contact: security@videofoundry.dev

---

**Last Updated:** January 2025
**Next Review:** Q2 2025
