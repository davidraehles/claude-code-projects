# Qdrant Quick Start - Manual Installation

Since automated installation requires sudo access, please run these commands manually in your WSL terminal.

## Step 1: Install Docker (Run these commands one by one)

```bash
# Update package list
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io

# Add your user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start
```

**Important**: After running the above commands, you need to **log out and log back in** (or restart WSL) for the docker group changes to take effect.

To restart WSL, run this in Windows PowerShell:
```powershell
wsl --shutdown
```

Then open WSL again.

---

## Step 2: Verify Docker Installation

```bash
# Check Docker version (should work without sudo now)
docker --version

# Test Docker
docker run hello-world
```

---

## Step 3: Start Qdrant Server

```bash
# Navigate to project directory
cd /home/darae/meal-planner

# Run the automated setup script
./setup-qdrant.sh
```

**OR** run manually:

```bash
# Create storage directory
mkdir -p ./qdrant_storage

# Pull and run Qdrant container
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Wait a few seconds for startup
sleep 5

# Test connection
curl http://localhost:6333/
```

---

## Step 4: Verify Qdrant is Running

```bash
# Check container status
docker ps | grep qdrant

# Check logs
docker logs qdrant

# Test REST API
curl http://localhost:6333/

# Open Web UI in browser
# http://localhost:6333/dashboard
```

---

## Step 5: Configure MCP Server (Optional)

If you want to use Qdrant through MCP, check if there's an official MCP server:

```bash
# Search for Qdrant MCP server
npm search mcp-server-qdrant
```

If available, add to `.kilocode/mcp.json`:

```json
{
  "mcpServers": {
    "qdrant": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-server-qdrant",
        "--url",
        "http://localhost:6333"
      ]
    }
  }
}
```

---

## Common Issues & Solutions

### Issue: "permission denied while trying to connect to the Docker daemon"

**Solution**: You haven't logged out and back in after adding user to docker group.

```bash
# Check if you're in docker group
groups

# If 'docker' is not in the list, log out and log back in
# Or run: newgrp docker
```

### Issue: "Cannot connect to the Docker daemon"

**Solution**: Docker service isn't running.

```bash
# Start Docker service
sudo service docker start

# Check status
sudo service docker status
```

### Issue: Port 6333 already in use

**Solution**: Something else is using the port.

```bash
# Find what's using the port
sudo lsof -i :6333

# Kill the process (replace <PID> with actual PID)
sudo kill -9 <PID>

# Or use a different port
docker run -d --name qdrant -p 6335:6333 qdrant/qdrant:latest
# Then access at http://localhost:6335
```

---

## Quick Commands Reference

```bash
# Start Qdrant
docker start qdrant

# Stop Qdrant
docker stop qdrant

# Restart Qdrant
docker restart qdrant

# View logs
docker logs qdrant
docker logs -f qdrant  # Follow logs

# Remove container (data is preserved in ./qdrant_storage)
docker rm -f qdrant

# Remove container and data
docker rm -f qdrant
sudo rm -rf ./qdrant_storage

# Check Qdrant status
docker ps | grep qdrant

# Execute commands inside container
docker exec -it qdrant /bin/sh
```

---

## Testing Qdrant with Python

```bash
# Install Qdrant client
pip install qdrant-client

# Create test script
cat > test_qdrant.py << 'EOF'
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Connect to Qdrant
client = QdrantClient(url="http://localhost:6333")

# Create a collection
client.create_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Insert a vector
client.upsert(
    collection_name="test_collection",
    points=[
        PointStruct(
            id=1,
            vector=[0.1] * 384,
            payload={"text": "Hello Qdrant!"}
        )
    ]
)

# Search
results = client.search(
    collection_name="test_collection",
    query_vector=[0.1] * 384,
    limit=5
)

print("Search results:", results)
print("\n✓ Qdrant is working!")
EOF

# Run test
python3 test_qdrant.py
```

---

## Next Steps

1. **Open Web UI**: http://localhost:6333/dashboard
2. **Read Full Guide**: See `QDRANT-SETUP-GUIDE.md` for advanced configuration
3. **Install Python Client**: `pip install qdrant-client`
4. **Check Documentation**: https://qdrant.tech/documentation/

---

## One-Line Install (Copy and Paste)

```bash
sudo apt-get update && sudo apt-get install -y docker.io && sudo usermod -aG docker $USER && sudo service docker start && echo "Docker installed! Log out and log back in, then run: ./setup-qdrant.sh"
```

After logging out and back in:

```bash
cd /home/darae/meal-planner && ./setup-qdrant.sh
```
