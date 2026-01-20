from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from config import UPLOAD_DIR
from api.routes import router as user_router
from api.admin_routes import router as admin_router

# Create FastAPI app
app = FastAPI(
    title="ZarbdorUn E-commerce API",
    description="REST API for ZarbdorUn e-commerce platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files for uploads
app.mount(f"/{UPLOAD_DIR}", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(user_router, tags=["User API"])
app.include_router(admin_router, tags=["Admin API"])

# Health check endpoint
@app.get("/")
async def root():
    """API Health Check"""
    return {
        "message": "ZarbdorUn E-commerce API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    from database import init_db
    
    # Initialize database
    init_db()
    
    # Run server
    uvicorn.run(app, host=API_HOST, port=API_PORT)
