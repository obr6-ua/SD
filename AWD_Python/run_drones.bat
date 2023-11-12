@echo off
setlocal EnableDelayedExpansion

REM Inicializar ID y puerto
set /a ID=1
set /a PORT=4001

REM Ejecutar el comando 8 veces en ventanas separadas
FOR /L %%i IN (1,1,8) DO (
    start cmd /k "echo Ejecutando docker-compose para ID=!ID! y puerto !PORT!:4000 && docker-compose run -e ID=!ID! -p !PORT!:4000 drone && exit"
    set /a ID=!ID!+1
    set /a PORT=!PORT!+1
)
endlocal
