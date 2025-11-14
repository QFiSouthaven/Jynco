# Sandboxing Setup Guide for Video Foundry

## Overview

This guide explains how to set up kernel-level sandboxing for Video Foundry AI workers using gVisor. Sandboxing is **mandatory** for all execution modes to prevent untrusted workflows from compromising the host system.

## Why Sandboxing is Critical

ComfyUI workflows can execute arbitrary Python code through custom nodes. Without proper sandboxing:
- Malicious workflows could access the host file system
- Attackers could steal secrets or sensitive data
- Host system could be compromised via privilege escalation

**Sandboxing provides defense-in-depth**, even when workflow vetting is in place.

---

## Sandboxing Technologies

Video Foundry supports two sandboxing technologies:

### 1. gVisor (Recommended for most deployments)

**Pros:**
- User-space kernel providing strong syscall filtering
- Works on any Linux system (no KVM required)
- Lower overhead than full VMs
- Excellent for Kubernetes deployments

**Cons:**
- ~10-20% performance overhead
- Some syscalls not implemented (rare edge cases)

**Use cases:**
- Kubernetes/container orchestration
- Cloud deployments (AWS, GCP, Azure)
- Systems without KVM support

### 2. Firecracker (Alternative for bare-metal)

**Pros:**
- Micro-VM isolation using KVM
- Sub-second startup time
- Strong isolation guarantees

**Cons:**
- Requires KVM support (bare-metal or nested virtualization)
- More complex setup
- Higher resource overhead

**Use cases:**
- Bare-metal servers with KVM
- AWS EC2 (powers AWS Lambda)
- Maximum isolation requirements

---

## gVisor Installation

### Step 1: Install gVisor Runtime

#### On Ubuntu/Debian:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg

# Add gVisor repository
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list > /dev/null

# Install runsc
sudo apt-get update
sudo apt-get install -y runsc

# Verify installation
runsc --version
```

#### On RHEL/CentOS/Fedora:

```bash
# Download latest runsc
ARCH=$(uname -m)
URL=https://storage.googleapis.com/gvisor/releases/release/latest/${ARCH}

sudo wget ${URL}/runsc -O /usr/local/bin/runsc
sudo wget ${URL}/runsc.sha512 -O /tmp/runsc.sha512

# Verify checksum
sha512sum -c /tmp/runsc.sha512

# Make executable
sudo chmod a+rx /usr/local/bin/runsc

# Verify installation
runsc --version
```

### Step 2: Configure Docker Daemon

Copy the gVisor daemon configuration:

```bash
# Backup existing Docker daemon config
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup

# Copy gVisor configuration
sudo cp config/docker-daemon-gvisor.json /etc/docker/daemon.json

# Create log directory for runsc
sudo mkdir -p /var/log/runsc
sudo chmod 755 /var/log/runsc

# Restart Docker
sudo systemctl restart docker

# Verify gVisor runtime is available
docker info | grep -i runtime
```

Expected output:
```
Runtimes: io.containerd.runc.v2 runc runsc runsc-kvm
Default Runtime: runc
```

### Step 3: Test gVisor

Test that gVisor is working correctly:

```bash
# Run test container with gVisor
docker run --rm --runtime=runsc hello-world

# Test with more complex container
docker run --rm --runtime=runsc ubuntu:22.04 uname -a
```

Expected output:
```
Linux <hostname> 4.4.0 #1 SMP ... x86_64 x86_64 x86_64 GNU/Linux
```

Note: The kernel version will show 4.4.0 (gVisor's emulated kernel) regardless of your host kernel.

### Step 4: Verify Isolation

Test that gVisor actually provides isolation:

```bash
# Try to access host /etc (should fail or show different content)
docker run --rm --runtime=runsc ubuntu:22.04 cat /etc/hostname

# Try to mount (should fail)
docker run --rm --runtime=runsc --privileged ubuntu:22.04 mount -t tmpfs tmpfs /mnt
# Should output: mount: /mnt: permission denied
```

---

## Kubernetes Deployment

For Kubernetes deployments, use RuntimeClass:

### Step 1: Install gVisor on Nodes

Follow the installation steps above on all Kubernetes worker nodes.

### Step 2: Create RuntimeClass

```yaml
# k8s/runtimeclass-gvisor.yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
```

Apply the RuntimeClass:

```bash
kubectl apply -f k8s/runtimeclass-gvisor.yaml
```

### Step 3: Use RuntimeClass in Deployments

Update AI worker deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-worker
spec:
  template:
    spec:
      runtimeClassName: gvisor  # Use gVisor runtime
      containers:
      - name: ai-worker
        image: videofoundry/ai-worker:latest
        # ... rest of container spec
```

---

## Docker Compose Configuration

Video Foundry's docker-compose.yml already includes security configurations. The runtime is specified via environment variable or docker-compose override.

### Production Mode (with gVisor)

Create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  ai_worker:
    runtime: runsc
    security_opt:
      - no-new-privileges:true
      - seccomp:unconfined  # gVisor provides syscall filtering
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if needed
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp
    networks:
      isolated_workers:
        aliases:
          - ai-worker

  comfyui:
    runtime: runsc
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp

networks:
  isolated_workers:
    driver: bridge
    internal: true  # No internet access
```

Start with override:

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Self-Hosted Production Mode (with controlled egress)

```yaml
version: '3.8'

services:
  ai_worker:
    runtime: runsc
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    environment:
      - HTTP_PROXY=http://proxy.internal:8080
      - HTTPS_PROXY=http://proxy.internal:8080
    networks:
      - default

  # Egress proxy (optional, for controlled internet access)
  egress_proxy:
    image: sameersbn/squid:latest
    container_name: vf_egress_proxy
    volumes:
      - ./config/squid.conf:/etc/squid/squid.conf:ro
    ports:
      - "3128:3128"
    networks:
      - default
```

### Developer Mode (sandboxed but with internet)

```yaml
version: '3.8'

services:
  ai_worker:
    runtime: runsc  # Still use gVisor for host protection
    security_opt:
      - no-new-privileges:true
    # Internet access allowed
    networks:
      - default
```

---

## Security Profiles

### AppArmor Profile (Additional Layer)

For Ubuntu/Debian systems, add AppArmor profile:

```bash
# /etc/apparmor.d/docker-videofoundry-worker

#include <tunables/global>

profile docker-videofoundry-worker flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Deny access to sensitive files
  deny /etc/shadow r,
  deny /etc/passwd w,
  deny /root/** rw,
  deny /home/** rw,

  # Allow only worker directories
  /videos/** rw,
  /tmp/worker/** rw,

  # Deny network raw sockets
  deny network raw,
  deny network packet,

  # Allow internet only if configured
  network inet stream,
  network inet6 stream,
}
```

Load the profile:

```bash
sudo apparmor_parser -r /etc/apparmor.d/docker-videofoundry-worker
```

Apply to container:

```yaml
services:
  ai_worker:
    security_opt:
      - apparmor=docker-videofoundry-worker
```

---

## Seccomp Profile (Syscall Filtering)

Create a restrictive seccomp profile:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_AARCH64"
  ],
  "syscalls": [
    {
      "names": [
        "read",
        "write",
        "open",
        "close",
        "stat",
        "fstat",
        "lseek",
        "mmap",
        "mprotect",
        "munmap",
        "brk",
        "rt_sigaction",
        "rt_sigprocmask",
        "ioctl",
        "access",
        "socket",
        "connect",
        "sendto",
        "recvfrom",
        "bind",
        "listen",
        "accept",
        "execve",
        "exit",
        "wait4",
        "kill",
        "fcntl",
        "getcwd",
        "chdir",
        "mkdir",
        "rmdir",
        "unlink",
        "readlink",
        "getdents",
        "select",
        "poll",
        "epoll_create",
        "epoll_ctl",
        "epoll_wait",
        "clone",
        "fork",
        "vfork",
        "getpid",
        "getppid",
        "getuid",
        "geteuid",
        "getgid",
        "getegid"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

Apply to container:

```yaml
services:
  ai_worker:
    security_opt:
      - seccomp=./config/seccomp-worker.json
```

**Note:** When using gVisor, seccomp is less critical as gVisor already filters syscalls.

---

## Network Isolation

### Production Mode: Zero Internet Access

Use internal network with no default gateway:

```yaml
networks:
  isolated_workers:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

Workers can only communicate with internal services (artifact repository, RabbitMQ, etc.).

### Self-Hosted Mode: Proxy-Based Egress Control

Use Squid proxy with allowlist:

```conf
# config/squid.conf

# Allowed domains (admin-configured)
acl allowed_domains dstdomain .github.com
acl allowed_domains dstdomain .githubusercontent.com
acl allowed_domains dstdomain .huggingface.co

# SSL bump for HTTPS inspection
acl SSL_ports port 443
acl CONNECT method CONNECT

# Allow only approved domains
http_access allow allowed_domains
http_access deny all

# Logging
access_log /var/log/squid/access.log
```

### Developer Mode: Logged Egress

Use transparent proxy for logging:

```yaml
services:
  egress_logger:
    image: mitmproxy/mitmproxy
    command: mitmdump -w /logs/egress.log
    volumes:
      - ./logs:/logs
```

---

## Testing Sandboxing Effectiveness

### Test 1: File System Isolation

```bash
# Try to access host files (should fail)
docker exec vf_ai_worker cat /etc/shadow
# Should fail with permission denied

# Try to write to root (should fail)
docker exec vf_ai_worker touch /test.txt
# Should fail (read-only root)
```

### Test 2: Network Isolation (Production)

```bash
# Try to access internet (should fail in production mode)
docker exec vf_ai_worker curl https://google.com
# Should timeout or fail with network error

# Verify no DNS resolution
docker exec vf_ai_worker nslookup google.com
# Should fail
```

### Test 3: Syscall Filtering

```bash
# Try to execute privileged syscall (should fail)
docker exec vf_ai_worker python3 -c "import os; os.setuid(0)"
# Should fail with permission error
```

### Test 4: Container Breakout Attempt

```bash
# Try to access host namespace (should fail)
docker exec vf_ai_worker cat /proc/1/environ
# Should show worker's init, not host's
```

---

## Performance Considerations

### gVisor Overhead

- **CPU:** ~10-20% overhead for most workloads
- **Memory:** Minimal additional memory (~50MB per container)
- **I/O:** Slightly higher latency for file operations

### Optimization Tips

1. **Use KVM platform if available:**
   ```json
   "runtimeArgs": ["--platform=kvm"]
   ```
   Lower overhead than ptrace platform.

2. **Shared memory for AI models:**
   ```yaml
   volumes:
     - type: tmpfs
       target: /dev/shm
       tmpfs:
         size: 2G
   ```

3. **Direct I/O for large files:**
   ```yaml
   volumes:
     - ./models:/models:ro,z
   ```

---

## Monitoring and Alerts

### Log Analysis

Monitor gVisor logs for security events:

```bash
# View gVisor debug logs
sudo tail -f /var/log/runsc/*/log

# Search for syscall violations
sudo grep -r "syscall violation" /var/log/runsc/
```

### Metrics

Track sandbox metrics:

```bash
# Container runtime stats
docker stats vf_ai_worker

# gVisor-specific metrics
runsc --root /var/run/docker/runtime-runsc/moby events
```

### Alerting

Set up alerts for:
- Sandbox escapes (should never happen)
- Unusual syscall patterns
- Network violations (unexpected egress in production)
- Resource exhaustion

---

## Troubleshooting

### Issue: gVisor not starting

**Symptoms:**
```
Error response from daemon: failed to create shim: OCI runtime create failed
```

**Solution:**
```bash
# Check runsc installation
which runsc
runsc --version

# Verify Docker daemon config
sudo cat /etc/docker/daemon.json

# Check Docker logs
sudo journalctl -u docker -n 50

# Test runsc directly
sudo runsc --rootless=false do echo "test"
```

### Issue: Permission denied in container

**Symptoms:**
```
Permission denied when accessing /videos
```

**Solution:**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 /path/to/videos

# Or use user namespace remapping
# Already configured in docker-daemon-gvisor.json
```

### Issue: Poor performance

**Symptoms:**
Slow workflow execution with gVisor

**Solution:**
```bash
# Switch to KVM platform (if supported)
# Edit /etc/docker/daemon.json:
"runtimeArgs": ["--platform=kvm", "--network=sandbox"]

# Restart Docker
sudo systemctl restart docker

# Verify KVM is available
lsmod | grep kvm
```

### Issue: Network not isolated

**Symptoms:**
Worker can access internet in production mode

**Solution:**
```bash
# Verify network is internal
docker network inspect video_foundry_isolated_workers

# Should show "Internal": true

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

---

## Production Checklist

Before deploying to production, verify:

- [ ] gVisor installed and tested
- [ ] Docker daemon configured with runsc runtime
- [ ] AI workers using gVisor runtime
- [ ] Network isolation enabled (internal network)
- [ ] DNS resolution disabled for workers
- [ ] Read-only root filesystem
- [ ] Dropped capabilities (CAP_DROP: ALL)
- [ ] No privileged mode
- [ ] AppArmor/SELinux profiles applied
- [ ] Logging and monitoring configured
- [ ] Tested sandbox escape prevention
- [ ] Documented incident response procedures

---

## References

- [gVisor Official Documentation](https://gvisor.dev/docs/)
- [gVisor Security Model](https://gvisor.dev/docs/architecture_guide/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Kubernetes RuntimeClass](https://kubernetes.io/docs/concepts/containers/runtime-class/)
- [Firecracker MicroVMs](https://firecracker-microvm.github.io/)

---

## Support

For issues with sandboxing setup:
1. Check gVisor documentation
2. Review Docker daemon logs
3. Test with simple containers first
4. Open issue at https://github.com/QFiSouthaven/Jynco/issues
