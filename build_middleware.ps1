# Script para reconstruir la imagen del middleware en Minikube

# Agregar Minikube al PATH
$env:Path += ";C:\Program Files\Kubernetes\Minikube"

Write-Host "🔧 Configurando entorno Docker de Minikube..." -ForegroundColor Cyan
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

Write-Host "🔨 Construyendo imagen middleware-citus:1.0..." -ForegroundColor Cyan
docker build -t middleware-citus:1.0 ./middleware

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Imagen construida exitosamente." -ForegroundColor Green
    
    Write-Host "🔄 Reiniciando pod de middleware..." -ForegroundColor Yellow
    kubectl delete pod -l app=middleware
    
    Write-Host "⏳ Esperando a que el nuevo pod inicie..."
    Start-Sleep -Seconds 10
    kubectl get pods
} else {
    Write-Host "❌ Error al construir la imagen." -ForegroundColor Red
    exit 1
}
