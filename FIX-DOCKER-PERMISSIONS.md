# Fix Docker Permissions Issue

You're getting a "permission denied" error because you need to log out and back in for the docker group changes to take effect.

---

## Solution Options

### Option 1: Restart WSL (Recommended - Easiest)

**In Windows PowerShell or Command Prompt**, run:

```powershell
wsl --shutdown
```

Then **open WSL again** and verify:

```bash
groups
# You should now see 'docker' in the list

# Test Docker
docker ps
```

---

### Option 2: Use `newgrp` Command (Temporary for Current Session)

This creates a new shell session with the docker group active:

```bash
newgrp docker
```

Then try running the setup script again:

```bash
./setup-qdrant.sh
```

**Note**: This only works for the current terminal session.

---

### Option 3: Use `sudo` (Quick Workaround)

If you just want to get Qdrant running quickly without restarting:

```bash
# Start Docker service
sudo service docker start

# Run Qdrant with sudo
sudo docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Test it
curl http://localhost:6333/
```

**Note**: You'll need to use `sudo docker` for all docker commands until you restart WSL.

---

### Option 4: Re-add User to Docker Group (If Previous Command Failed)

If for some reason the user wasn't added properly:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

# Then choose Option 1 or Option 2 above
```

---

## Verification Steps

After using any of the options above, verify Docker works without sudo:

```bash
# Check groups (should include 'docker')
groups

# Test Docker (should work without sudo)
docker ps

# Check Docker version
docker --version

# Run hello-world test
docker run hello-world
```

---

## Recommended Steps (In Order)

1. **Restart WSL** (Option 1 - run `wsl --shutdown` in Windows PowerShell)
2. **Open WSL again**
3. **Verify groups**: `groups` (should show 'docker')
4. **Test Docker**: `docker ps`
5. **Run setup**: `./setup-qdrant.sh`

---

## If You're in a Hurry

Just run this now with sudo:

```bash
sudo service docker start && \
sudo docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest && \
sleep 3 && \
curl http://localhost:6333/
```

Then restart WSL later to fix the permissions permanently.

---

## Common Issues

### "docker: Got permission denied"
- **Cause**: User not in docker group or haven't logged out/in
- **Fix**: Use Option 1 (restart WSL)

### "Cannot connect to the Docker daemon"
- **Cause**: Docker service not running
- **Fix**: `sudo service docker start`

### "groups" command doesn't show 'docker'
- **Cause**: User not added to group or need to re-login
- **Fix**: Run `sudo usermod -aG docker $USER` then restart WSL
