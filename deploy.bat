@echo off
echo =====================
echo Git Deploy Starting...
echo =====================

git add .
git commit -m "update"
git push

echo.
echo =====================
echo Deploy Completed
echo =====================

pause