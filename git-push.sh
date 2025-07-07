#!/bin/bash

# MLB Analytics Git Push Script
# This script helps you commit and push changes to GitHub with a custom message

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MLB Analytics - Git Push Script${NC}"
echo "======================================"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check if there are any changes to commit
if git diff --quiet && git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  No changes detected to commit${NC}"
    echo "Current git status:"
    git status --short
    exit 0
fi

# Show current status
echo -e "${YELLOW}📋 Current git status:${NC}"
git status --short
echo ""

# Check if there are unstaged changes
if ! git diff --quiet; then
    echo -e "${YELLOW}⚠️  You have unstaged changes. Do you want to add all changes? (y/n)${NC}"
    read -p "> " -r add_all
    if [[ $add_all =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}📦 Adding all changes...${NC}"
        git add .
        echo -e "${GREEN}✅ All changes staged${NC}"
    else
        echo -e "${YELLOW}ℹ️  Only staged changes will be committed${NC}"
    fi
fi

# Get commit message from user
echo ""
echo -e "${BLUE}💬 Enter your commit message:${NC}"
read -p "> " -r commit_message

# Validate commit message
if [ -z "$commit_message" ]; then
    echo -e "${RED}❌ Error: Commit message cannot be empty${NC}"
    exit 1
fi

# Get current branch
current_branch=$(git branch --show-current)
echo -e "${YELLOW}📍 Current branch: ${current_branch}${NC}"

# Get remote origin URL
remote_url=$(git remote get-url origin 2>/dev/null || echo "No remote origin configured")
echo -e "${YELLOW}🌐 Remote origin: ${remote_url}${NC}"

# Show what will be committed
echo ""
echo -e "${YELLOW}📝 Changes to be committed:${NC}"
git diff --staged --name-status
echo ""

# Confirm before committing
echo -e "${BLUE}🤔 Do you want to commit and push these changes? (y/n)${NC}"
read -p "> " -r confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏹️  Operation cancelled${NC}"
    exit 0
fi

# Commit changes
echo -e "${BLUE}📝 Committing changes...${NC}"
if git commit -m "$commit_message"; then
    echo -e "${GREEN}✅ Changes committed successfully${NC}"
else
    echo -e "${RED}❌ Failed to commit changes${NC}"
    exit 1
fi

# Push to remote
echo -e "${BLUE}🚀 Pushing to origin/${current_branch}...${NC}"
if git push origin "$current_branch"; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
    echo ""
    echo -e "${GREEN}🎉 All done! Your changes are now on GitHub.${NC}"
    
    # Show the commit hash
    commit_hash=$(git rev-parse --short HEAD)
    echo -e "${BLUE}📌 Commit hash: ${commit_hash}${NC}"
    echo -e "${BLUE}💬 Commit message: \"${commit_message}\"${NC}"
    
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    echo -e "${YELLOW}ℹ️  Your changes are committed locally but not pushed to remote${NC}"
    echo -e "${YELLOW}ℹ️  You may need to set up the remote origin or check your internet connection${NC}"
    exit 1
fi

# Optional: Show git log
echo ""
echo -e "${BLUE}📜 Recent commits:${NC}"
git log --oneline -5
