# """
# Database Configuration and Connection Management
# """

# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.pool import QueuePool
# from contextlib import contextmanager
# import logging

# from .models import Base

# log = logging.getLogger(__name__)


# class DatabaseConfig:
#     """Database configuration from environment variables"""
    
#     def __init__(self):
#         self.DB_HOST = os.getenv("DB_HOST", "localhost")
#         self.DB_PORT = os.getenv("DB_PORT", "543")
#         self.DB_NAME = os.getenv("DB_NAME", "sales_explorer")
#         self.DB_USER = os.getenv("DB_USER", "postgres")
#         self.DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        
#         # Connection pool settings
#         self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
#         self.MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
#         self.POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        
#     @property
#     def database_url(self) -> str:
#         """Construct PostgreSQL database URL"""
#         return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
#     def get_engine_kwargs(self) -> dict:
#         """Get SQLAlchemy engine configuration"""
#         return {
#             "poolclass": QueuePool,
#             "pool_size": self.POOL_SIZE,
#             "max_overflow": self.MAX_OVERFLOW,
#             "pool_timeout": self.POOL_TIMEOUT,
#             "pool_pre_ping": True,  # Verify connections before using
#             "echo": os.getenv("DB_ECHO", "false").lower() == "true"  # SQL logging
#         }


# class DatabaseManager:
#     """Manages database connections and sessions"""
    
#     def __init__(self, config: DatabaseConfig = None):
#         self.config = config or DatabaseConfig()
#         self.engine = None
#         self.SessionLocal = None
#         self._initialized = False
    
#     def initialize(self):
#         """Initialize database engine and session factory"""
#         if self._initialized:
#             log.info("Database already initialized")
#             return
        
#         try:
#             log.info(f"Connecting to database: {self.config.DB_HOST}:{self.config.DB_PORT}/{self.config.DB_NAME}")
            
#             self.engine = create_engine(
#                 self.config.database_url,
#                 **self.config.get_engine_kwargs()
#             )
            
#             self.SessionLocal = sessionmaker(
#                 autocommit=False,
#                 autoflush=False,
#                 bind=self.engine
#             )
            
#             self._initialized = True
#             log.info("✅ Database engine initialized successfully")
            
#         except Exception as e:
#             log.error(f"❌ Failed to initialize database: {e}")
#             raise
    
#     def create_tables(self):
#         """Create all database tables"""
#         if not self._initialized:
#             self.initialize()
        
#         try:
#             log.info("Creating database tables...")
#             Base.metadata.create_all(bind=self.engine)
#             log.info("✅ Database tables created successfully")
#         except Exception as e:
#             log.error(f"❌ Failed to create tables: {e}")
#             raise
    
#     def drop_tables(self):
#         """Drop all database tables (use with caution!)"""
#         if not self._initialized:
#             self.initialize()
        
#         try:
#             log.warning("⚠️  Dropping all database tables...")
#             Base.metadata.drop_all(bind=self.engine)
#             log.info("✅ Database tables dropped")
#         except Exception as e:
#             log.error(f"❌ Failed to drop tables: {e}")
#             raise
    
#     def get_session(self) -> Session:
#         """Get a new database session"""
#         if not self._initialized:
#             self.initialize()
#         return self.SessionLocal()
    
#     @contextmanager
#     def session_scope(self):
#         """
#         Provide a transactional scope for database operations.
        
#         Usage:
#             with db_manager.session_scope() as session:
#                 session.add(obj)
#         """
#         session = self.get_session()
#         try:
#             yield session
#             session.commit()
#         except Exception as e:
#             session.rollback()
#             log.error(f"Database transaction failed: {e}")
#             raise
#         finally:
#             session.close()
    
#     def close(self):
#         """Close database connections"""
#         if self.engine:
#             self.engine.dispose()
#             log.info("Database connections closed")


# # Global database manager instance
# db_manager = DatabaseManager()


# def get_db() -> Session:
#     """
#     Dependency for FastAPI endpoints.
    
#     Usage in FastAPI:
#         @app.get("/api/endpoint")
#         async def endpoint(db: Session = Depends(get_db)):
#             ...
#     """
#     db = db_manager.get_session()
#     try:
#         yield db
#     finally:
#         db.close()


# def init_database():
#     """Initialize database (call at startup)"""
#     db_manager.initialize()
#     db_manager.create_tables()









"""
Database Configuration and Connection Management
"""

import os
import logging
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from psycopg2 import sql
from .base import Base 

log = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration from environment variables"""
    
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "sales_explorer")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "adj2272")
        
        # Connection pool settings
        self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
        self.MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def admin_url(self) -> str:
        """Connection URL to default postgres DB for admin operations"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/postgres"
    
    def get_engine_kwargs(self) -> dict:
        """Get SQLAlchemy engine configuration"""
        return {
            "poolclass": QueuePool,
            "pool_size": self.POOL_SIZE,
            "max_overflow": self.MAX_OVERFLOW,
            "pool_timeout": self.POOL_TIMEOUT,
            "pool_pre_ping": True,
            "echo": os.getenv("DB_ECHO", "false").lower() == "true"
        }


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def _create_database_if_missing(self):
        """Create the database if it does not exist"""
        try:
            log.info(f"Checking if database '{self.config.DB_NAME}' exists...")
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                host=self.config.DB_HOST,
                port=self.config.DB_PORT
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s;"),
                [self.config.DB_NAME]
            )
            exists = cur.fetchone()
            if not exists:
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.config.DB_NAME)
                    )
                )
                log.info(f"✅ Database '{self.config.DB_NAME}' created successfully.")
            else:
                log.info(f"Database '{self.config.DB_NAME}' already exists.")
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"❌ Failed to check/create database: {e}")
            raise
    
    def initialize(self):
        """Initialize database engine and session factory"""
        if self._initialized:
            log.info("Database already initialized")
            return
        
        try:
            # Ensure the DB exists before connecting via SQLAlchemy
            self._create_database_if_missing()

            log.info(f"Connecting to database: {self.config.DB_HOST}:{self.config.DB_PORT}/{self.config.DB_NAME}")
            self.engine = create_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs()
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self._initialized = True
            log.info("✅ Database engine initialized successfully")
        except Exception as e:
            log.error(f"❌ Failed to initialize database: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            self.initialize()
        try:
            log.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            log.info("✅ Database tables created successfully")
        except Exception as e:
            log.error(f"❌ Failed to create tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self._initialized:
            self.initialize()
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            log.error(f"Database transaction failed: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            log.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Session:
    """Dependency for FastAPI endpoints."""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database (call at startup)"""
    db_manager.initialize()
    db_manager.create_tables()




