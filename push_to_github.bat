@echo off
echo Initializing Git...
git init
git add .
git commit -m "feat: setup Render backend and Vercel frontend deployment"
git remote remove origin 2>nul
git remote add origin https://github.com/Mishra123456/degradix-health-hub-main.git
git branch -M main
echo Pushing to GitHub...
git push -u origin main --force
echo.
echo Push complete! Press any key to exit.
pause
