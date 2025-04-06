from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from app.app_sql.setup_database import Base, engine
from app.req_filters.AuthInterceptor import AuthInterceptor
from fastapi import FastAPI
from app.routes import AccountRoutes, DetectionRoutes


# Initialize data
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize models
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

authInterceptor = AuthInterceptor(app)
authInterceptor.turn_on()

# Include routers
app.include_router(AccountRoutes.router)
app.include_router(DetectionRoutes.router)