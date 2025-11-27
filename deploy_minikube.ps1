# Script de despliegue en Minikube para Windows (PowerShell)

# Agregar Minikube al PATH temporalmente para este script
$env:Path += ";C:\Program Files\Kubernetes\Minikube"

Write-Host "🚀 Iniciando despliegue en Minikube..." -ForegroundColor Cyan

# 1. Verificar si Minikube está corriendo
$minikubeStatus = minikube status --format='{{.Host}}'
if ($minikubeStatus -ne "Running") {
    Write-Host "⚠️ Minikube no está corriendo. Iniciando..." -ForegroundColor Yellow
    minikube start
} else {
    Write-Host "✅ Minikube está corriendo." -ForegroundColor Green
}

# 2. Configurar entorno Docker para usar el daemon de Minikube
Write-Host "🐳 Configurando entorno Docker de Minikube..." -ForegroundColor Cyan
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 3. Construir imagen del middleware
Write-Host "🔨 Construyendo imagen del middleware (esto puede tardar unos minutos)..." -ForegroundColor Cyan
docker build -t middleware-citus:1.0 ./middleware

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Imagen construida exitosamente." -ForegroundColor Green
} else {
    Write-Host "❌ Error al construir la imagen." -ForegroundColor Red
    exit 1
}

# 4. Aplicar manifiestos de Kubernetes
Write-Host "📦 Aplicando manifiestos de Kubernetes..." -ForegroundColor Cyan

# Configuración y Secretos
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/schema-configmap.yaml

# Base de Datos
Write-Host "   - Desplegando PostgreSQL..."
kubectl apply -f k8s/postgres-deployment.yaml

# HAPI FHIR
Write-Host "   - Desplegando HAPI FHIR..."
kubectl apply -f k8s/hapi-fhir-deployment.yaml

# Middleware
Write-Host "   - Desplegando Middleware..."
kubectl apply -f k8s/middleware-deployment.yaml

# 5. Esperar a que los pods estén listos (opcional, solo informativo)
Write-Host "⏳ Esperando a que los pods se inicien..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
kubectl get pods

# 6. Mostrar URL de acceso
Write-Host "`n🎉 Despliegue completado!" -ForegroundColor Green
Write-Host "Para acceder al sistema:" -ForegroundColor Yellow

$serviceUrl = minikube service hce-middleware --url
Write-Host "👉 URL del Middleware: $serviceUrl" -ForegroundColor White
Write-Host "   (Usa esta URL en tu navegador)"

Write-Host "`nComandos útiles:" -ForegroundColor Gray
Write-Host "   kubectl get pods          # Ver estado de los pods"
Write-Host "   kubectl logs <pod-name>   # Ver logs de un pod"
Write-Host "   minikube dashboard        # Abrir dashboard visual"
