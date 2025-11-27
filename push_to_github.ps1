# Script para subir el proyecto al repositorio de GitHub

Write-Host "Preparando proyecto para GitHub..." -ForegroundColor Cyan

# 1. Crear .gitignore
$gitignoreContent = @'
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
*.env

# Database
*.db
*.sqlite3

# Docker
*.log

# OS
.DS_Store
Thumbs.db

# Credentials
credenciales_*.txt

# Minikube
.minikube/
'@

if (-not (Test-Path ".gitignore")) {
    Write-Host "Creando .gitignore..." -ForegroundColor Yellow
    $gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
}

# 2. Inicializar Git
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
}

# 3. Configurar remote
Write-Host "Configurando repositorio remoto..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/Marck04Mc/Historia-Clinica-Unificada-y-Alta-Disponibilidad-por-Sedes-HCE-.git"

$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}

# 4. Agregar archivos
Write-Host "Agregando archivos..." -ForegroundColor Yellow
git add .

# 5. Commit
Write-Host "Creando commit..." -ForegroundColor Yellow
git commit -m "feat: Sistema HCE completo con roles, Kubernetes y FHIR"

# 6. Push
Write-Host "Subiendo al repositorio..." -ForegroundColor Cyan
git branch -M main
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "Proyecto subido exitosamente!" -ForegroundColor Green
    Write-Host "Repositorio: $remoteUrl" -ForegroundColor White
} else {
    Write-Host "Error al subir el proyecto." -ForegroundColor Red
    Write-Host "Verifica tu autenticacion de GitHub" -ForegroundColor Yellow
}
