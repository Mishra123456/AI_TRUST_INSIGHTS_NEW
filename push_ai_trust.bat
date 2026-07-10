@echo off
echo Pushing AI Trust Insights to GitHub...
cd "c:\Users\user\Downloads\ai-trust-insights-main (2)\ai-trust-insights-main"
git add .
git commit -m "chore: push latest YAML configs"
git push origin main
echo.
echo Done! Press any key to exit.
pause
