# Qdrant Local Server Setup Guide

This guide will help you set up a local Qdrant vector database server on http://localhost:6333.

---

## Option 1: Docker Installation (Recommended)

### Step 1: Install Docker on WSL2

```bash
# Update package list
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list again
sudo apt-get update

# Install Docker Engine
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

# Verify installation
docker --version
```

**Important**: After adding yourself to the docker group, you need to log out and log back in (or restart WSL) for the changes to take effect.

### Step 2: Start Qdrant Container

```bash
# Pull and run Qdrant
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Verify it's running
docker ps | grep qdrant

# Check logs
docker logs qdrant
```

### Step 3: Verify Qdrant is Accessible

```bash
# Test the REST API
curl http://localhost:6333/

# Expected response: JSON with Qdrant version info
```

### Step 4: Stop/Start/Remove Qdrant

```bash
# Stop container
docker stop qdrant

# Start container
docker start qdrant

# Remove container (if you want to start fresh)
docker rm -f qdrant
```

---

## Option 2: Qdrant Binary (No Docker Required)

If you can't or don't want to use Docker, you can download the Qdrant binary directly.

### Step 1: Download Qdrant Binary

```bash
# Create a directory for Qdrant
mkdir -p ~/qdrant
cd ~/qdrant

# Download the latest Qdrant binary (replace version as needed)
wget https://github.com/qdrant/qdrant/releases/download/v1.11.3/qdrant-x86_64-unknown-linux-musl.tar.gz

# Extract
tar -xzf qdrant-x86_64-unknown-linux-musl.tar.gz

# Make executable
chmod +x qdrant
```

### Step 2: Run Qdrant

```bash
# Run Qdrant (foreground)
./qdrant

# Or run in background with nohup
nohup ./qdrant > qdrant.log 2>&1 &

# Check if it's running
curl http://localhost:6333/
```

### Step 3: Stop Qdrant

```bash
# Find the process
ps aux | grep qdrant

# Kill it
pkill qdrant

# Or if using nohup, find PID and kill
kill $(pgrep qdrant)
```

---

## Option 3: Docker Compose (Best for Development)

Create a `docker-compose.yml` file in your project:

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
```

Then run:

```bash
# Start Qdrant
docker compose up -d

# View logs
docker compose logs -f qdrant

# Stop Qdrant
docker compose down

# Stop and remove data
docker compose down -v
```

---

## Configure MCP Server for Qdrant

After Qdrant is running, add it to your `.kilocode/mcp.json`:

```json
{
  "mcpServers": {
    "redis": {
      "command": "uvx",
      "args": [
        "mcp-server-redis",
        "--url",
        "redis://default:gjWuRAlGXbBvnWGoVwSUIUwWyBvkRCMv@switchback.proxy.rlwy.net:51029"
      ]
    },
    "sqlite": {
      "command": "uvx",
      "args": [
        "mcp-server-sqlite",
        "--db-path",
        "backend/"
      ]
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://postgres:FOxNYviCCzWKNNJCVswOqoCYZtQwDfkC@shortline.proxy.rlwy.net:56297/railway"
      ]
    },
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

**Note**: If there's no official MCP server for Qdrant, you can use the Qdrant Python client or REST API directly in your code.

---

## Testing Qdrant

### Using cURL

```bash
# Get Qdrant version
curl http://localhost:6333/

# Create a collection
curl -X PUT http://localhost:6333/collections/test \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'

# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/test
```

### Using Python

```bash
# Install Qdrant client
pip install qdrant-client
```

```python
from qdrant_client import QdrantClient

# Connect to local Qdrant
client = QdrantClient(url="http://localhost:6333")

# Check connection
print(client.get_collections())

# Create a collection
from qdrant_client.models import Distance, VectorParams

client.create_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Insert vectors
from qdrant_client.models import PointStruct

client.upsert(
    collection_name="test_collection",
    points=[
        PointStruct(
            id=1,
            vector=[0.1] * 384,
            payload={"text": "Hello world"}
        )
    ]
)

# Search
results = client.search(
    collection_name="test_collection",
    query_vector=[0.1] * 384,
    limit=5
)
print(results)
```

---

## Troubleshooting

### Docker not starting on WSL2

```bash
# Check if Docker service is running
sudo service docker status

# Start Docker service
sudo service docker start

# Enable Docker to start on WSL boot (add to ~/.bashrc)
echo 'sudo service docker start' >> ~/.bashrc
```

### Port 6333 already in use

```bash
# Find what's using the port
sudo lsof -i :6333

# Or
sudo netstat -tulpn | grep 6333

# Kill the process
sudo kill -9 <PID>
```

### Qdrant container won't start

```bash
# Check logs
docker logs qdrant

# Remove old container and start fresh
docker rm -f qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

### Permission denied for qdrant_storage directory

```bash
# Fix permissions
sudo chown -R $USER:$USER ./qdrant_storage
chmod -R 755 ./qdrant_storage
```

---

## Qdrant Web UI

Qdrant comes with a built-in web UI accessible at:

**http://localhost:6333/dashboard**

This provides a visual interface to:
- View collections
- Browse points/vectors
- Search and filter
- Monitor performance
- Manage snapshots

---

## Production Considerations

For production use, consider:

1. **Persistent Storage**: Always mount a volume for data persistence
2. **Authentication**: Enable API key authentication
3. **Backups**: Set up automated snapshots
4. **Monitoring**: Use Prometheus metrics endpoint at `/metrics`
5. **Resource Limits**: Configure memory and CPU limits
6. **TLS/SSL**: Use HTTPS for external access

Example production Docker Compose:

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## Quick Start Commands

```bash
# Install Docker (run these commands manually)
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
sudo service docker start

# Start Qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# Test it
curl http://localhost:6333/

# Open web UI
# Navigate to http://localhost:6333/dashboard in your browser
```

---

## Resources

- **Official Docs**: https://qdrant.tech/documentation/
- **GitHub**: https://github.com/qdrant/qdrant
- **Docker Hub**: https://hub.docker.com/r/qdrant/qdrant
- **Python Client**: https://github.com/qdrant/qdrant-client
- **REST API Docs**: https://qdrant.tech/documentation/interfaces/rest/
