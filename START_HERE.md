# 🚀 START HERE - Video Foundry Quick Setup

**One-click automated setup. No manual configuration needed.**

---

## Step 1: Run the Automated Setup (ONE COMMAND)

### Windows PowerShell:
```powershell
.\setup.ps1
```

### Mac/Linux:
```bash
chmod +x setup.sh && ./setup.sh
```

**That's it!** The script will:
- ✅ Check Docker is running
- ✅ Auto-detect and fix port conflicts
- ✅ Create optimized `.env` configuration
- ✅ Start all services
- ✅ Validate everything is working
- ✅ Open the UI in your browser

**Time: ~2-3 minutes**

---

## If Something Goes Wrong

### Run the Auto-Troubleshooter:
```powershell
.\fix-common-issues.ps1 -AutoFix
```

This automatically detects and fixes:
- Port 8000 blocked (common on Windows)
- Docker not running
- Containers stuck/not starting
- Missing configuration files
- Service connectivity issues

---

## Access Your Platform

After setup completes, access these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend UI** | http://localhost:5173 | Main application |
| **API Docs** | http://localhost:8000/docs | Interactive API |
| **ComfyUI** | http://localhost:8188 | AI workflow editor |
| **RabbitMQ** | http://localhost:15672 | Queue management |
| **Portainer** | http://localhost:9000 | Docker management |

**Note:** Ports may differ if auto-adjusted for conflicts. Check terminal output.

---

## Common Commands

```powershell
# Stop all services
.\dev.ps1 down

# View logs
.\dev.ps1 logs

# Restart everything
.\dev.ps1 restart

# Check service status
.\dev.ps1 status

# Run troubleshooter
.\fix-common-issues.ps1
```

---

## Next Steps

1. **Explore the Platform** → Open http://localhost:5173
2. **Read the User Guide** → `docs/USER_GUIDE.md`
3. **Learn the Architecture** → `CLAUDE.md`
4. **Set Up ArchViz Features** → `docs/ARCHVIZ_ANIMATION_STRATEGY.md`

---

## Still Having Issues?

1. **Check Docker Desktop is running** (green icon in system tray)
2. **Run:** `.\fix-common-issues.ps1 -AutoFix`
3. **View detailed logs:** `docker-compose logs -f`
4. **Check:** `docs/TROUBLESHOOTING.md`

---

**Need help?** Check the documentation:
- **Quick Start:** `QUICKSTART.md`
- **Full Setup Guide:** `docs/SETUP.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Windows-Specific:** `docs/WINDOWS_SETUP.md`
