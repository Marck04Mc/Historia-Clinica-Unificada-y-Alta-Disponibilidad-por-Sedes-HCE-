# Script de inicio del sistema HCE
# Limpia contenedores y volúmenes anteriores y reinicia todo

Write-Host "🧹 Limpiando contenedores y volúmenes anteriores..." -ForegroundColor Yellow

# Detener y eliminar todos los contenedores del proyecto
docker-compose down 2>$null

# Eliminar contenedores específicos si existen
docker rm -f hce-postgres hce-hapi-fhir hce-middleware 2>$null

# Eliminar volúmenes específicos
docker volume rm ids-hce_postgres-data 2>$null

Write-Host "✅ Limpieza completada" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Iniciando servicios..." -ForegroundColor Cyan

# Iniciar servicios
docker-compose up -d

Write-Host ""
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Write-Host "   Esto puede tomar 1-2 minutos..."
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "📊 Estado de los servicios:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "📝 Para ver los logs:" -ForegroundColor White
Write-Host "   docker-compose logs -f" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Acceder a:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:8000" -ForegroundColor Green
Write-Host "   HAPI FHIR: http://localhost:8080/fhir" -ForegroundColor Green
Write-Host ""
Write-Host "👤 Credenciales de prueba:" -ForegroundColor White
Write-Host "   doctor1 / test123" -ForegroundColor Gray
Write-Host "   admisionista1 / test123" -ForegroundColor Gray
Write-Host "   paciente1 / test123" -ForegroundColor Gray
