#!/bin/bash
# Railway CLI Setup Script

echo "=========================================="
echo "Railway CLI Setup"
echo "=========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not installed"
    echo ""
    echo "Install with:"
    echo "  curl -fsSL https://railway.com/install.sh | sudo sh"
    echo ""
    exit 1
fi

echo "✅ Railway CLI installed: $(railway --version)"
echo ""

# Check if logged in
echo "Checking Railway login status..."
if railway whoami &> /dev/null; then
    echo "✅ Already logged in to Railway"
    railway whoami
    echo ""
else
    echo "⚠️  Not logged in to Railway"
    echo ""
    echo "Please run:"
    echo "  railway login"
    echo ""
    echo "This will open your browser to authenticate."
    echo "After login, run this script again."
    echo ""
    exit 1
fi

# Link to project
echo "Linking to Railway project..."
echo "Project ID: 786b11ae-cdbd-461b-9b96-01050878c6c4"
echo ""

if railway link -p 786b11ae-cdbd-461b-9b96-01050878c6c4; then
    echo "✅ Successfully linked to Railway project"
    echo ""

    # Show project info
    echo "Project information:"
    railway status
    echo ""

    echo "=========================================="
    echo "✅ Railway CLI Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Useful commands:"
    echo "  railway status          - Show project status"
    echo "  railway logs            - View service logs"
    echo "  railway run <command>   - Run command with Railway env"
    echo "  railway up              - Deploy to Railway"
    echo "  railway variables       - Manage environment variables"
    echo ""
else
    echo "❌ Failed to link Railway project"
    echo ""
    echo "Make sure:"
    echo "1. You're logged in (railway login)"
    echo "2. You have access to project ID: 786b11ae-cdbd-461b-9b96-01050878c6c4"
    echo ""
    exit 1
fi
