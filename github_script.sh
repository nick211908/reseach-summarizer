#!/bin/bash



# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
fi

# Add remote (force update if already exists)
git remote remove origin 2>/dev/null
git remote add origin https://github.com/nick211908/reseach-summarizer.git

# Stage all changes
git add .

# Commit changes
git commit -m "Initial commit" || echo "Nothing to commit"

# Push to main branch
git branch -M main
git push -u origin main