@echo off
setlocal EnableDelayedExpansion

REM Inicializar ID, puerto y API
set /a ID=1
set /a PORT=4001
set API=N

REM Ejecutar el comando 8 veces en ventanas separadas
FOR /L %%i IN (1,1,8) DO (
    REM Cambiar API a S después de las primeras 4 iteraciones
    if %%i GTR 4 (
        set API=S
    )

    start cmd /k "echo Ejecutando docker-compose para ID=!ID!, puerto !PORT!:4000 y API=!API! && docker-compose run -e ID=!ID! -e API=!API! -p !PORT!:4000 drone && exit"
    set /a ID=!ID!+1
    set /a PORT=!PORT!+1
)
endlocal