from fastapi import FastAPI
from Stores.llm.Templates.template_parser import TemplateParser
from Routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from Stores.llm.LLMProviderFactory import LLMProviderFactory
from Stores.VectorDB.VectorDbProviderFactory import VectorDbProviderFactory

app = FastAPI()

async def startup_span():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DB_NAME]

    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDbProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    # vector db client
    app.vector_db_client = vector_db_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND,
        db_path=settings.VECTOR_DB_PATH,
        distance_method=settings.VECTOR_DB_DISTANCE_METHOD
    )
    app.vector_db_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )
    

async def shutdown_span():
    app.mongodb_conn.close() 
    app.vector_db_client.disconnect()
    
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)       

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)