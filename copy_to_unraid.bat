@echo off

SET TEMPLATE_PATH=%1

if "%TEMPLATE_PATH%"=="" (
    echo "Usage: copy_to_unraid.bat <path_to_template>"
    exit /b
)

scp "-r" "%TEMPLATE_PATH%" "bigbox:/boot/config/plugins/dockerMan/templates/nwithan8/"