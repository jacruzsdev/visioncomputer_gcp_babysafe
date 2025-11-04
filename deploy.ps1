# ==============================================================================
# SCRIPT DE DESPLIEGUE EN GCP (PowerShell)
# ------------------------------------------------------------------------------
# Este script automatiza la configuración, el build de Docker y el despliegue
# de la aplicación Django en Google Cloud Run.
# Requisitos: gcloud CLI, Docker y la Cuenta de Servicio configurada.
# ==============================================================================

# --- 1. Definición de Variables (AJUSTAR SEGÚN TU PROYECTO) ---
$REGION = "us-east1"                                # Región de GCP
$SERVICE_NAME = "safety-detector-app"                 # Nombre del Servicio en Cloud Run
$GCP_PROJECT_ID = (gcloud config get-value project)   # Obtener el ID del proyecto actual
$REPO_NAME = "visioncomputador"                            # Nombre del Repositorio de Artifact Registry
$IMAGE_TAG = "$REGION-docker.pkg.dev/$GCP_PROJECT_ID/$REPO_NAME/$SERVICE_NAME`:latest"
$SERVICE_ACCOUNT = "safetyappserviceaccount@snappy-storm-475817-t1.iam.gserviceaccount.com"
$MY_DJANGO_SECRET = '$3-oa20*t%&ai=vxiq)bq3y_5js_9l%pb&p#u)6o!&0$pu4)=d' 
$VERTEX_ENDPOINT_ID = "tu-endpoint-id-de-vertex-ai" # Endpoint de tu modelo
Write-Host "Iniciando Despliegue para el Proyecto: $GCP_PROJECT_ID en la Región: $REGION" -ForegroundColor Green

# --- 2. Habilitar APIs y Configurar Artifact Registry ---
Write-Host "`n--- Habilitando APIs y Configurando Artifact Registry ---" -ForegroundColor Yellow

# Habilita los servicios requeridos
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com # Nueva: Necesaria para gcloud builds submit

# Crea el repositorio de Docker si no existe
Write-Host "Verificando/Creando repositorio $REPO_NAME..."
gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="Docker Repo for Django App" `
    --allow-project-ids="" 2>$null | Out-Null

# --- 3. Construir y Subir la Imagen (Usando Cloud Build) ---
Write-Host "`n--- 🚀 Construyendo y subiendo la imagen usando CLOUD BUILD ---" -ForegroundColor Yellow
Write-Host "Esto evita problemas de red local." -ForegroundColor Cyan

# El build se ejecuta en GCP y el push se hace internamente.
gcloud builds submit . --tag $IMAGE_TAG

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error en el Cloud Build o al subir la imagen. Abortando." -ForegroundColor Red
    exit 1
}

# --- 4. Desplegar en Google Cloud Run (Optimizado) ---
Write-Host "`n--- Desplegando en Google Cloud Run (Memoria y Timeout ajustados) ---" -ForegroundColor Yellow
Write-Host "Usando Service Account: $SERVICE_ACCOUNT" -ForegroundColor Cyan

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --region $REGION `
    --allow-unauthenticated `
    --service-account $SERVICE_ACCOUNT `
    --platform managed `
    --port 8080 `
    --memory 1Gi `
    --max-instances 3 `
    --timeout 600 `
    --set-env-vars SECRET_KEY=$MY_DJANGO_SECRET,GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$REGION,VERTEX_ENDPOINT_ID=$VERTEX_ENDPOINT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error en el despliegue de Cloud Run. Revisar los logs." -ForegroundColor Red
    exit 1
}


Write-Host "`n✅ ¡Despliegue de Django completado exitosamente en Cloud Run! ✅" -ForegroundColor Green
# Mostrar la URL final
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)'

# Pregunta de continuación (IAM)
Write-Host "`nSi el acceso falla con 'Permission Denied', recuerda ejecutar el comando para hacerlo público:" -ForegroundColor Yellow
Write-Host "gcloud run services add-iam-policy-binding $SERVICE_NAME --region=$REGION --member=allUsers --role=roles/run.invoker" -ForegroundColor Yellow