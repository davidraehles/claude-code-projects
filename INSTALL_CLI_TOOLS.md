# CLI Tools Installation Guide

Quick guide to install Railway and Vercel CLI tools on Windows.

## 🚀 Quick Start (Easiest Method)

**Simply double-click** [run-install.cmd](./run-install.cmd) and follow the prompts!

The script will:
- ✅ Automatically detect and use PowerShell 7 (or fall back to PowerShell 5.1)
- ✅ Find Node.js even if not in PATH
- ✅ Install Railway CLI
- ✅ Install Vercel CLI
- ✅ Verify installations

---

## 📋 Prerequisites

### 1. Install Node.js (Required)

If you don't have Node.js installed:

1. **Download**: [nodejs.org](https://nodejs.org/)
   - Choose **LTS version** (Long Term Support)
   - Version 20.x or 22.x recommended

2. **Install**:
   - Run the installer
   - ✅ **IMPORTANT**: Check "Add to PATH" during installation
   - Keep all other default settings

3. **Verify**:
   ```cmd
   node --version
   npm --version
   ```

### 2. Install PowerShell 7+ (Recommended)

PowerShell 7+ is faster and more feature-rich than Windows PowerShell 5.1.

1. **Download**: [GitHub Releases](https://github.com/PowerShell/PowerShell/releases)
   - Look for: `PowerShell-7.x.x-win-x64.msi`

2. **Install**:
   - Run the MSI installer
   - Use default settings

3. **Verify**:
   ```cmd
   pwsh --version
   ```

---

## 🎯 Installation Methods

### Method 1: Use the Launcher Script (Recommended)

1. **Double-click** [run-install.cmd](./run-install.cmd)
2. The script will automatically:
   - Detect the best PowerShell version
   - Find Node.js installation
   - Install both CLI tools
   - Verify installations

### Method 2: Run PowerShell Script Directly

**Using PowerShell 7:**
```powershell
pwsh -ExecutionPolicy Bypass -File install-cli-tools.ps1
```

**Using Windows PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File install-cli-tools.ps1
```

### Method 3: Manual Installation

```cmd
# Install Railway CLI
npm install -g @railway/cli

# Install Vercel CLI
npm install -g vercel

# Verify
railway --version
vercel --version
```

---

## 🔧 Troubleshooting

### Node.js Not Found

**Symptom**: Script says "Node.js not found"

**Solutions**:

1. **Check if Node.js is installed**:
   ```cmd
   where node
   ```

2. **If installed but not in PATH**, the script will try to find it automatically in:
   - `C:\Program Files\nodejs`
   - `C:\Program Files (x86)\nodejs`
   - `%LOCALAPPDATA%\Programs\nodejs`

3. **Manual PATH fix**:
   ```cmd
   # Find Node.js location
   dir /s /b C:\node.exe

   # Add to PATH (replace with your actual path)
   setx PATH "%PATH%;C:\Program Files\nodejs"

   # Restart PowerShell
   ```

4. **Still not working?** Reinstall Node.js with "Add to PATH" checked

### Execution Policy Error

**Symptom**: "cannot be loaded because running scripts is disabled"

**Solution**: The launcher script handles this, but if running manually:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### npm ERR! EACCES

**Symptom**: Permission denied when installing globally

**Solutions**:

1. **Run PowerShell as Administrator**:
   - Right-click PowerShell → "Run as Administrator"
   - Run the script again

2. **Or configure npm to use a different directory**:
   ```cmd
   npm config set prefix "%APPDATA%\npm"
   ```

### Railway/Vercel Command Not Found After Installation

**Symptom**: CLI tools installed but commands not recognized

**Solution**:
1. **Restart PowerShell/Terminal** (npm global bin path needs to be loaded)
2. **Check npm global bin location**:
   ```cmd
   npm config get prefix
   # Should be in your PATH
   ```

---

## ✅ Post-Installation

After successful installation, authenticate with both services:

### Railway Authentication
```cmd
# Login (opens browser)
railway login

# Navigate to project directory
cd c:\Users\david\workspaces\claude-code-projects

# Link to your Railway project
railway link
```

### Vercel Authentication
```cmd
# Login (opens browser)
vercel login

# Navigate to frontend directory
cd c:\Users\david\workspaces\claude-code-projects\meal-planner-ui

# Link to your Vercel project
vercel link
```

---

## 🎯 Next Steps

Once installed and authenticated, you can use debugging commands:

### Railway Commands
```cmd
railway logs              # View deployment logs
railway status            # Check service status
railway variables         # List environment variables
railway open              # Open project in browser
```

### Vercel Commands
```cmd
vercel logs <url>         # View deployment logs
vercel ls                 # List deployments
vercel env ls             # List environment variables
vercel open               # Open project in browser
```

For more debugging commands, see [CLI_INSTALLATION.md](./CLI_INSTALLATION.md)

---

## 📚 Related Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - General deployment guide
- [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) - Detailed Railway setup
- [CLI_INSTALLATION.md](./CLI_INSTALLATION.md) - Full CLI reference

---

## 🆘 Still Having Issues?

1. Check Node.js version: `node --version` (should be 18.x, 20.x, or 22.x)
2. Check npm version: `npm --version` (should be 9.x or 10.x)
3. Try running as Administrator
4. Check Windows PATH environment variable includes Node.js
5. Restart your computer (sometimes Windows PATH updates need a full restart)
