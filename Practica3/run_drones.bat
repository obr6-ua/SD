@echo off
setlocal EnableDelayedExpansion

REM Inicializar ID y puerto
set ID=1
set PORT=4001
set API=N

REM Ejecutar el comando 8 veces en ventanas separadas
FOR /L %%i IN (1,1,8) DO (
    REM Cambiar API a S después de las primeras 4 iteraciones
    @REM if %%i GEQ 5 (
    @REM     set API=S
    @REM )

    start cmd /k "echo Ejecutando docker-compose para ID=!ID! y puerto !PORT!:4000 && docker-compose run -e ID=!ID! -e API=!API! -p !PORT!:4000 drone && exit"
    set /a ID+=1
    set /a PORT+=1
)
endlocal
