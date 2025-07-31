#!/bin/bash
# Environment switcher script

case "$1" in
    "local")
        echo "🏠 Switching to LOCAL environment..."
        if [ -f .prod ]; then
            mv .prod .prod.disabled
            echo "Disabled .prod file"
        fi
        if [ -f .env.production ]; then
            mv .env.production .env.production.disabled
            echo "Disabled .env.production file"
        fi
        echo "✅ Now using .env for local development"
        echo "Database will use local credentials from .env file"
        ;;
    "production")
        echo "🌐 Switching to PRODUCTION environment..."
        if [ -f .prod.disabled ]; then
            mv .prod.disabled .prod
            echo "Enabled .prod file"
        elif [ -f .env.production.disabled ]; then
            mv .env.production.disabled .env.production
            echo "Enabled .env.production file"
        elif [ -f .env.production ]; then
            cp .env.production .prod
            echo "Created .prod from .env.production"
        fi
        echo "✅ Now using .prod or .env.production for production"
        echo "Database will use production credentials"
        ;;
    *)
        echo "Usage: $0 {local|production}"
        echo ""
        echo "Current environment files:"
        ls -la .env* .prod* 2>/dev/null | grep -E '\.(env|prod)'
        echo ""
        echo "Environment detection logic:"
        if [ -f .prod ] || [ -f .env.production ]; then
            echo "📍 Currently configured for PRODUCTION"
        elif [ -f .env ]; then
            echo "📍 Currently configured for LOCAL"
        else
            echo "⚠️  No environment files found"
        fi
        ;;
esac
