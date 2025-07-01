"""
Database Configuration and Connection Management
Handles database connections and session management
"""

import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base

from ..core.exceptions import BackendError


logger = logging.getLogger(__name__)
Base = declarative_base()


class DatabaseConfig:
    """Database configuration settings"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "drclivi",
        username: str = "postgres",
        password: str = "",
        pool_size: int = 10,
        max_overflow: int = 20
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = pool_size
        self.max_overflow = max_overflow
    
    @property
    def url(self) -> str:
        """Get database URL for SQLAlchemy"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def asyncpg_url(self) -> str:
        """Get database URL for asyncpg"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseManager:
    """
    Database connection and session manager
    Handles SQLAlchemy async sessions and connection pooling
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self):
        """Initialize database engine and session factory"""
        try:
            self.engine = create_async_engine(
                self.config.url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                echo=False  # Set to True for SQL debugging
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise BackendError(f"Database initialization failed: {e}")
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database connections closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        if not self.session_factory:
            raise BackendError("Database not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False


class AsyncPGManager:
    """
    Alternative database manager using asyncpg directly
    For cases where SQLAlchemy ORM is not needed
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.config.asyncpg_url,
                min_size=5,
                max_size=self.config.pool_size
            )
            self.logger.info("AsyncPG pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AsyncPG pool: {e}")
            raise BackendError(f"AsyncPG initialization failed: {e}")
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.logger.info("AsyncPG pool closed")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection with automatic cleanup"""
        if not self.pool:
            raise BackendError("AsyncPG pool not initialized")
        
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                self.logger.error(f"AsyncPG connection error: {e}")
                raise
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"AsyncPG health check failed: {e}")
            return False
