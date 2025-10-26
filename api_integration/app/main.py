from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import score_routes, fraude_routes
from app.auth.auth_handler import require_roles, verify_token
from app.logging.elk_logger import logger

app = FastAPI(
    title="API Scoring & Détection Fraude",
    description="Endpoints pour calcul de score et détection de fraude avec auth RBAC et logs ELK",
    version="1.0.0"
)

# --- Middleware CORS (exemple)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adapter selon l'environnement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes
app.include_router(
    score_routes.router,
    prefix="/score",
    tags=["Score"],
    dependencies=[Depends(require_roles("analyst", "admin"))]
)

app.include_router(
    fraude_routes.router,
    prefix="/fraude",
    tags=["Fraude"],
    dependencies=[Depends(require_roles("analyst", "admin"))]
)

# --- Endpoint Admin exemple
@app.get("/admin/status", tags=["Admin"], dependencies=[Depends(require_roles("admin"))])
def admin_status():
    """
    Endpoint admin pour vérifier le statut de l'API.
    """
    return {"status": "API opérationnelle", "message": "Bienvenue admin!"}

# --- Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"message": "Bienvenue sur l'API Scoring & Fraude. Consultez /docs pour Swagger UI."}

# --- Event handlers pour démarrage et shutdown
@app.on_event("startup")
async def startup_event():
    logger.info("Démarrage de l'API Scoring & Fraude...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Arrêt de l'API Scoring & Fraude...")
