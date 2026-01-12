@echo off
echo ========================================
echo Running Screenshot Generated Tests
echo Test: ScreenshotTest
echo Generated: 2026-01-12 15:31:22
echo ========================================
echo.

REM Run tests with Maven
mvn clean test -Dtest=ScreenshotTestTest

echo.
echo ========================================
echo Test execution completed!
echo Check target/surefire-reports for results
echo ========================================
pause
