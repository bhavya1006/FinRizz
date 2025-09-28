#!/bin/bash

# 🚀 FinRizz Quick Deployment Script
# Usage: ./deploy.sh [platform]
# Platforms: vercel, netlify, firebase, github, local

set -e

PLATFORM=${1:-"local"}
PROJECT_NAME="finrizz-landing"

echo "🚀 Deploying FinRizz Landing Page to: $PLATFORM"

# Prepare build
echo "📦 Preparing build..."

case $PLATFORM in
  "vercel")
    echo "🔵 Deploying to Vercel..."
    if ! command -v vercel &> /dev/null; then
        echo "Installing Vercel CLI..."
        npm install -g vercel
    fi
    vercel --prod
    ;;
    
  "netlify")
    echo "🟢 Deploying to Netlify..."
    if ! command -v netlify &> /dev/null; then
        echo "Installing Netlify CLI..."
        npm install -g netlify-cli
    fi
    netlify deploy --prod --dir src
    ;;
    
  "firebase")
    echo "🔥 Deploying to Firebase..."
    if ! command -v firebase &> /dev/null; then
        echo "Installing Firebase CLI..."
        npm install -g firebase-tools
    fi
    firebase login
    firebase deploy
    ;;
    
  "github")
    echo "🐙 Setting up GitHub Pages..."
    git add .
    git commit -m "Deploy: FinRizz landing page"
    git push origin main
    echo "✅ Pushed to GitHub! Enable GitHub Pages in repository settings."
    ;;
    
  "local")
    echo "🏠 Starting local server..."
    echo "🌐 Opening http://localhost:3000"
    cd src && python3 -m http.server 3000
    ;;
    
  *)
    echo "❌ Unknown platform: $PLATFORM"
    echo "Available platforms: vercel, netlify, firebase, github, local"
    exit 1
    ;;
esac

echo "✅ Deployment complete!"