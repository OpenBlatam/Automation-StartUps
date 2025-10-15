#!/usr/bin/env python3
"""
ClickUp Brain Database ORM
=========================

Object-Relational Mapping system with connection pooling, migrations,
query builder, and multi-database support.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from enum import Enum
import threading
from contextlib import asynccontextmanager

ROOT = Path(__file__).parent

T = TypeVar('T')

class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_type: DatabaseType
    host: str = "localhost"
    port: int = 5432
    database: str = "clickup_brain"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_mode: str = "prefer"

@dataclass
class Migration:
    """Database migration."""
    version: str
    name: str
    up_sql: str
    down_sql: str
    created_at: datetime = field(default_factory=datetime.now)

class Field:
    """Database field definition."""
    
    def __init__(self, field_type: str, nullable: bool = True, default: Any = None, 
                 primary_key: bool = False, unique: bool = False, index: bool = False):
        self.field_type = field_type
        self.nullable = nullable
        self.default = default
        self.primary_key = primary_key
        self.unique = unique
        self.index = index

class Model(ABC):
    """Base model class."""
    
    _table_name: str = ""
    _fields: Dict[str, Field] = {}
    _db: Optional['Database'] = None
    
    def __init__(self, **kwargs):
        for field_name, field_def in self._fields.items():
            value = kwargs.get(field_name, field_def.default)
            setattr(self, field_name, value)
    
    @classmethod
    def set_database(cls, db: 'Database') -> None:
        """Set database instance for model."""
        cls._db = db
    
    @classmethod
    async def create_table(cls) -> None:
        """Create table for model."""
        if not cls._db:
            raise RuntimeError("Database not set for model")
        
        await cls._db.create_table(cls)
    
    @classmethod
    async def drop_table(cls) -> None:
        """Drop table for model."""
        if not cls._db:
            raise RuntimeError("Database not set for model")
        
        await cls._db.drop_table(cls)
    
    async def save(self) -> 'Model':
        """Save model to database."""
        if not self._db:
            raise RuntimeError("Database not set for model")
        
        return await self._db.save(self)
    
    async def delete(self) -> bool:
        """Delete model from database."""
        if not self._db:
            raise RuntimeError("Database not set for model")
        
        return await self._db.delete(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for field_name in self._fields.keys():
            value = getattr(self, field_name, None)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[field_name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """Create model from dictionary."""
        return cls(**data)

class QueryBuilder:
    """Query builder for database operations."""
    
    def __init__(self, model_class: Type[Model], db: 'Database'):
        self.model_class = model_class
        self.db = db
        self._select_fields: List[str] = []
        self._where_conditions: List[str] = []
        self._where_params: List[Any] = []
        self._order_by: List[str] = []
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None
        self._joins: List[str] = []
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """Select specific fields."""
        self._select_fields = list(fields) if fields else []
        return self
    
    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """Add WHERE condition."""
        self._where_conditions.append(condition)
        self._where_params.extend(params)
        return self
    
    def where_eq(self, field: str, value: Any) -> 'QueryBuilder':
        """Add equality WHERE condition."""
        return self.where(f"{field} = %s", value)
    
    def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """Add IN WHERE condition."""
        placeholders = ", ".join(["%s"] * len(values))
        return self.where(f"{field} IN ({placeholders})", *values)
    
    def order_by(self, field: str, direction: str = "ASC") -> 'QueryBuilder':
        """Add ORDER BY clause."""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self._offset_value = count
        return self
    
    def join(self, table: str, condition: str) -> 'QueryBuilder':
        """Add JOIN clause."""
        self._joins.append(f"JOIN {table} ON {condition}")
        return self
    
    async def all(self) -> List[Model]:
        """Execute query and return all results."""
        return await self.db.execute_query(self)
    
    async def first(self) -> Optional[Model]:
        """Execute query and return first result."""
        results = await self.limit(1).all()
        return results[0] if results else None
    
    async def count(self) -> int:
        """Execute query and return count."""
        return await self.db.execute_count(self)
    
    def _build_sql(self) -> tuple[str, List[Any]]:
        """Build SQL query."""
        table_name = self.model_class._table_name
        
        # SELECT clause
        if self._select_fields:
            select_clause = ", ".join(self._select_fields)
        else:
            select_clause = "*"
        
        sql = f"SELECT {select_clause} FROM {table_name}"
        params = []
        
        # JOIN clauses
        for join in self._joins:
            sql += f" {join}"
        
        # WHERE clause
        if self._where_conditions:
            sql += " WHERE " + " AND ".join(self._where_conditions)
            params.extend(self._where_params)
        
        # ORDER BY clause
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        
        # LIMIT clause
        if self._limit_value is not None:
            sql += f" LIMIT {self._limit_value}"
        
        # OFFSET clause
        if self._offset_value is not None:
            sql += f" OFFSET {self._offset_value}"
        
        return sql, params

class ConnectionPool:
    """Database connection pool."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
        self.logger = logging.getLogger("connection_pool")
        self._lock = threading.RLock()
    
    async def initialize(self) -> None:
        """Initialize connection pool."""
        if self.config.db_type == DatabaseType.POSTGRESQL:
            await self._init_postgresql()
        elif self.config.db_type == DatabaseType.MYSQL:
            await self._init_mysql()
        elif self.config.db_type == DatabaseType.SQLITE:
            await self._init_sqlite()
        else:
            raise ValueError(f"Unsupported database type: {self.config.db_type}")
    
    async def _init_postgresql(self) -> None:
        """Initialize PostgreSQL connection pool."""
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=1,
                max_size=self.config.pool_size,
                command_timeout=self.config.pool_timeout
            )
            self.logger.info("PostgreSQL connection pool initialized")
        except ImportError:
            raise ImportError("asyncpg package is required for PostgreSQL")
    
    async def _init_mysql(self) -> None:
        """Initialize MySQL connection pool."""
        try:
            import aiomysql
            self.pool = await aiomysql.create_pool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.database,
                user=self.config.username,
                password=self.config.password,
                minsize=1,
                maxsize=self.config.pool_size,
                autocommit=True
            )
            self.logger.info("MySQL connection pool initialized")
        except ImportError:
            raise ImportError("aiomysql package is required for MySQL")
    
    async def _init_sqlite(self) -> None:
        """Initialize SQLite connection pool."""
        try:
            import aiosqlite
            # SQLite doesn't need a pool, but we'll create a simple wrapper
            self.pool = aiosqlite.connect(self.config.database)
            self.logger.info("SQLite connection initialized")
        except ImportError:
            raise ImportError("aiosqlite package is required for SQLite")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool."""
        if self.config.db_type == DatabaseType.SQLITE:
            async with self.pool as conn:
                yield conn
        else:
            async with self.pool.acquire() as conn:
                yield conn
    
    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            if self.config.db_type == DatabaseType.SQLITE:
                await self.pool.close()
            else:
                await self.pool.close()
            self.logger.info("Connection pool closed")

class MigrationManager:
    """Database migration manager."""
    
    def __init__(self, db: 'Database'):
        self.db = db
        self.migrations: List[Migration] = []
        self.logger = logging.getLogger("migration_manager")
    
    def add_migration(self, migration: Migration) -> None:
        """Add migration to manager."""
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    async def create_migrations_table(self) -> None:
        """Create migrations tracking table."""
        sql = """
        CREATE TABLE IF NOT EXISTS migrations (
            version VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await self.db.execute_sql(sql)
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        await self.create_migrations_table()
        result = await self.db.execute_sql("SELECT version FROM migrations ORDER BY version")
        return [row[0] for row in result] if result else []
    
    async def apply_migrations(self) -> None:
        """Apply pending migrations."""
        applied = await self.get_applied_migrations()
        
        for migration in self.migrations:
            if migration.version not in applied:
                self.logger.info(f"Applying migration {migration.version}: {migration.name}")
                
                try:
                    await self.db.execute_sql(migration.up_sql)
                    await self.db.execute_sql(
                        "INSERT INTO migrations (version, name) VALUES (%s, %s)",
                        migration.version, migration.name
                    )
                    self.logger.info(f"Migration {migration.version} applied successfully")
                except Exception as e:
                    self.logger.error(f"Failed to apply migration {migration.version}: {e}")
                    raise
    
    async def rollback_migration(self, version: str) -> None:
        """Rollback a specific migration."""
        migration = next((m for m in self.migrations if m.version == version), None)
        if not migration:
            raise ValueError(f"Migration {version} not found")
        
        self.logger.info(f"Rolling back migration {version}: {migration.name}")
        
        try:
            await self.db.execute_sql(migration.down_sql)
            await self.db.execute_sql("DELETE FROM migrations WHERE version = %s", version)
            self.logger.info(f"Migration {version} rolled back successfully")
        except Exception as e:
            self.logger.error(f"Failed to rollback migration {version}: {e}")
            raise

class Database:
    """Main database class."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = ConnectionPool(config)
        self.migration_manager = MigrationManager(self)
        self.logger = logging.getLogger("database")
        self._models: Dict[str, Type[Model]] = {}
    
    async def initialize(self) -> None:
        """Initialize database connection."""
        await self.pool.initialize()
        self.logger.info("Database initialized")
    
    async def close(self) -> None:
        """Close database connection."""
        await self.pool.close()
        self.logger.info("Database closed")
    
    def register_model(self, model_class: Type[Model]) -> None:
        """Register a model with the database."""
        model_class.set_database(self)
        self._models[model_class._table_name] = model_class
        self.logger.info(f"Registered model {model_class.__name__}")
    
    async def create_table(self, model_class: Type[Model]) -> None:
        """Create table for model."""
        table_name = model_class._table_name
        fields = model_class._fields
        
        # Build CREATE TABLE SQL
        field_definitions = []
        for field_name, field_def in fields.items():
            field_sql = f"{field_name} {field_def.field_type}"
            
            if field_def.primary_key:
                field_sql += " PRIMARY KEY"
            elif not field_def.nullable:
                field_sql += " NOT NULL"
            
            if field_def.unique:
                field_sql += " UNIQUE"
            
            if field_def.default is not None:
                if isinstance(field_def.default, str):
                    field_sql += f" DEFAULT '{field_def.default}'"
                else:
                    field_sql += f" DEFAULT {field_def.default}"
            
            field_definitions.append(field_sql)
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(field_definitions)})"
        await self.execute_sql(sql)
        
        # Create indexes
        for field_name, field_def in fields.items():
            if field_def.index:
                index_sql = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{field_name} ON {table_name} ({field_name})"
                await self.execute_sql(index_sql)
    
    async def drop_table(self, model_class: Type[Model]) -> None:
        """Drop table for model."""
        table_name = model_class._table_name
        sql = f"DROP TABLE IF EXISTS {table_name}"
        await self.execute_sql(sql)
    
    async def save(self, model: Model) -> Model:
        """Save model to database."""
        table_name = model.__class__._table_name
        fields = model.__class__._fields
        
        # Check if model has primary key
        pk_field = next((name for name, field in fields.items() if field.primary_key), None)
        pk_value = getattr(model, pk_field, None) if pk_field else None
        
        if pk_value is None:
            # Insert new record
            field_names = [name for name in fields.keys() if name != pk_field]
            field_values = [getattr(model, name) for name in field_names]
            
            placeholders = ", ".join(["%s"] * len(field_values))
            sql = f"INSERT INTO {table_name} ({', '.join(field_names)}) VALUES ({placeholders})"
            
            if self.config.db_type == DatabaseType.POSTGRESQL:
                sql += " RETURNING *"
                result = await self.execute_sql(sql, *field_values)
                if result:
                    return model.__class__.from_dict(dict(result[0]))
            else:
                await self.execute_sql(sql, *field_values)
                # For non-PostgreSQL, we'd need to get the last insert ID
                return model
        else:
            # Update existing record
            field_names = [name for name in fields.keys() if name != pk_field]
            field_values = [getattr(model, name) for name in field_names]
            
            set_clause = ", ".join([f"{name} = %s" for name in field_names])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {pk_field} = %s"
            
            await self.execute_sql(sql, *field_values, pk_value)
            return model
    
    async def delete(self, model: Model) -> bool:
        """Delete model from database."""
        table_name = model.__class__._table_name
        fields = model.__class__._fields
        
        pk_field = next((name for name, field in fields.items() if field.primary_key), None)
        if not pk_field:
            raise ValueError("Model must have a primary key for deletion")
        
        pk_value = getattr(model, pk_field)
        sql = f"DELETE FROM {table_name} WHERE {pk_field} = %s"
        
        result = await self.execute_sql(sql, pk_value)
        return result is not None
    
    def query(self, model_class: Type[Model]) -> QueryBuilder:
        """Create query builder for model."""
        return QueryBuilder(model_class, self)
    
    async def execute_query(self, query_builder: QueryBuilder) -> List[Model]:
        """Execute query and return results."""
        sql, params = query_builder._build_sql()
        results = await self.execute_sql(sql, *params)
        
        if not results:
            return []
        
        # Convert results to model instances
        models = []
        for row in results:
            if isinstance(row, dict):
                model_data = row
            else:
                # Convert tuple to dict
                field_names = list(query_builder.model_class._fields.keys())
                model_data = dict(zip(field_names, row))
            
            model = query_builder.model_class.from_dict(model_data)
            models.append(model)
        
        return models
    
    async def execute_count(self, query_builder: QueryBuilder) -> int:
        """Execute count query."""
        sql, params = query_builder._build_sql()
        count_sql = f"SELECT COUNT(*) FROM ({sql}) AS count_query"
        result = await self.execute_sql(count_sql, *params)
        return result[0][0] if result else 0
    
    async def execute_sql(self, sql: str, *params: Any) -> List[Any]:
        """Execute raw SQL query."""
        async with self.pool.get_connection() as conn:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                return await conn.fetch(sql, *params)
            elif self.config.db_type == DatabaseType.MYSQL:
                cursor = await conn.execute(sql, params)
                return await cursor.fetchall()
            elif self.config.db_type == DatabaseType.SQLITE:
                cursor = await conn.execute(sql, params)
                return await cursor.fetchall()

# Example model
class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field("SERIAL", primary_key=True),
        "username": Field("VARCHAR(50)", unique=True, nullable=False),
        "email": Field("VARCHAR(100)", unique=True, nullable=False),
        "created_at": Field("TIMESTAMP", default="CURRENT_TIMESTAMP"),
        "is_active": Field("BOOLEAN", default=True)
    }

class Task(Model):
    _table_name = "tasks"
    _fields = {
        "id": Field("SERIAL", primary_key=True),
        "title": Field("VARCHAR(255)", nullable=False),
        "description": Field("TEXT"),
        "user_id": Field("INTEGER", nullable=False, index=True),
        "status": Field("VARCHAR(20)", default="pending"),
        "created_at": Field("TIMESTAMP", default="CURRENT_TIMESTAMP"),
        "updated_at": Field("TIMESTAMP", default="CURRENT_TIMESTAMP")
    }

# Global database instance
db_instance: Optional[Database] = None

def initialize_database(config: DatabaseConfig) -> Database:
    """Initialize global database instance."""
    global db_instance
    db_instance = Database(config)
    return db_instance

async def get_database() -> Database:
    """Get global database instance."""
    global db_instance
    if db_instance is None:
        raise RuntimeError("Database not initialized")
    return db_instance

if __name__ == "__main__":
    # Demo database ORM
    print("ClickUp Brain Database ORM Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Initialize database
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            database="demo.db"
        )
        db = initialize_database(config)
        await db.initialize()
        
        # Register models
        db.register_model(User)
        db.register_model(Task)
        
        # Create tables
        await db.create_table(User)
        await db.create_table(Task)
        
        # Create and save user
        user = User(username="john_doe", email="john@example.com")
        saved_user = await user.save()
        print(f"Created user: {saved_user.to_dict()}")
        
        # Create and save task
        task = Task(title="Demo Task", description="This is a demo task", user_id=1)
        saved_task = await task.save()
        print(f"Created task: {saved_task.to_dict()}")
        
        # Query users
        users = await db.query(User).where_eq("username", "john_doe").all()
        print(f"Found users: {[u.to_dict() for u in users]}")
        
        # Query tasks for user
        user_tasks = await db.query(Task).where_eq("user_id", 1).all()
        print(f"User tasks: {[t.to_dict() for t in user_tasks]}")
        
        # Update task
        saved_task.status = "completed"
        await saved_task.save()
        print(f"Updated task: {saved_task.to_dict()}")
        
        # Count tasks
        task_count = await db.query(Task).count()
        print(f"Total tasks: {task_count}")
        
        # Close database
        await db.close()
        
        print("\nDatabase ORM demo completed!")
    
    asyncio.run(demo())







