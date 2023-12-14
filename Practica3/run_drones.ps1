# Inicializar ID y puerto
$ID = 1
$PORT = 4001

# Ejecutar el comando 8 veces en ventanas separadas
1..8 | ForEach-Object {
    Start-Process powershell -ArgumentList "-NoExit", "-Command `"`& { docker-compose run -e ID=$ID -p $PORT:4000 drone }`""
    $ID++
    $PORT++
}
