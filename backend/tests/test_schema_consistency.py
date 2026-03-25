"""
Schema consistency tests to verify all model columns exist in the database.

This test ensures that SQLAlchemy models are in sync with the actual database schema,
preventing runtime errors from missing or extra columns.
"""
import pytest
from sqlalchemy import inspect, create_engine
from app.db.database import get_async_engine
from app.db.models import User, Project, Dataset, OperationHistory, Agent


def get_table_columns(engine, table_name):
    """Get columns from a table using synchronous inspection."""
    # Convert async URL to sync URL for inspection
    sync_url = str(engine.url).replace('sqlite+aiosqlite', 'sqlite')
    sync_engine = create_engine(sync_url)
    inspector = inspect(sync_engine)
    columns = {col['name'] for col in inspector.get_columns(table_name)}
    sync_engine.dispose()
    return columns


@pytest.mark.asyncio
async def test_all_model_columns_exist():
    """Verify all model columns exist in the database."""
    engine = get_async_engine()
    
    models = {
        'users': User,
        'projects': Project,
        'datasets': Dataset,
        'operation_history': OperationHistory,
        'agents': Agent
    }
    
    discrepancies = []
    
    for table_name, model in models.items():
        # Get database columns using synchronous inspection
        db_columns = get_table_columns(engine, table_name)
        
        # Get model columns
        model_columns = {col.name for col in model.__table__.columns}
        
        # Find missing columns (in model but not in database)
        missing_in_db = model_columns - db_columns
        
        # Find extra columns (in database but not in model)
        extra_in_db = db_columns - model_columns
        
        if missing_in_db:
            discrepancies.append(f"Table '{table_name}': Missing in DB: {missing_in_db}")
        if extra_in_db:
            discrepancies.append(f"Table '{table_name}': Extra in DB: {extra_in_db}")
    
    if discrepancies:
        pytest.fail(
            "Schema inconsistencies found:\n" + "\n".join(discrepancies)
        )


@pytest.mark.asyncio
async def test_users_table_schema():
    """Verify users table has all required columns."""
    engine = get_async_engine()
    
    db_columns = get_table_columns(engine, 'users')
    model_columns = {col.name for col in User.__table__.columns}
    
    missing = model_columns - db_columns
    assert not missing, f"Users table missing columns: {missing}"


@pytest.mark.asyncio
async def test_projects_table_schema():
    """Verify projects table has all required columns."""
    engine = get_async_engine()
    
    db_columns = get_table_columns(engine, 'projects')
    model_columns = {col.name for col in Project.__table__.columns}
    
    missing = model_columns - db_columns
    assert not missing, f"Projects table missing columns: {missing}"


@pytest.mark.asyncio
async def test_datasets_table_schema():
    """Verify datasets table has all required columns."""
    engine = get_async_engine()
    
    db_columns = get_table_columns(engine, 'datasets')
    model_columns = {col.name for col in Dataset.__table__.columns}
    
    missing = model_columns - db_columns
    assert not missing, f"Datasets table missing columns: {missing}"


@pytest.mark.asyncio
async def test_operation_history_table_schema():
    """Verify operation_history table has all required columns."""
    engine = get_async_engine()
    
    db_columns = get_table_columns(engine, 'operation_history')
    model_columns = {col.name for col in OperationHistory.__table__.columns}
    
    missing = model_columns - db_columns
    assert not missing, f"OperationHistory table missing columns: {missing}"


@pytest.mark.asyncio
async def test_agents_table_schema():
    """Verify agents table has all required columns."""
    engine = get_async_engine()
    
    db_columns = get_table_columns(engine, 'agents')
    model_columns = {col.name for col in Agent.__table__.columns}
    
    missing = model_columns - db_columns
    assert not missing, f"Agents table missing columns: {missing}"


def get_table_columns_with_types(engine, table_name):
    """Get columns with types from a table using synchronous inspection."""
    # Convert async URL to sync URL for inspection
    sync_url = str(engine.url).replace('sqlite+aiosqlite', 'sqlite')
    sync_engine = create_engine(sync_url)
    inspector = inspect(sync_engine)
    columns = {col['name']: col for col in inspector.get_columns(table_name)}
    sync_engine.dispose()
    return columns


@pytest.mark.asyncio
async def test_column_types_match():
    """Verify column types match between models and database."""
    engine = get_async_engine()
    
    models = {
        'users': User,
        'projects': Project,
        'datasets': Dataset,
        'operation_history': OperationHistory,
        'agents': Agent
    }
    
    type_mismatches = []
    
    for table_name, model in models.items():
        # Get database column info using synchronous inspection
        db_columns = get_table_columns_with_types(engine, table_name)
        
        # Get model column info
        for model_col in model.__table__.columns:
            if model_col.name in db_columns:
                db_col = db_columns[model_col.name]
                # Basic type check (can be expanded)
                db_type = str(db_col['type']).lower()
                model_type = str(model_col.type).lower()
                
                # Check for common type mismatches
                if 'integer' in model_type and 'varchar' in db_type:
                    type_mismatches.append(
                        f"Table '{table_name}', column '{model_col.name}': "
                        f"Model expects {model_type}, DB has {db_type}"
                    )
                elif 'string' in model_type and 'integer' in db_type:
                    type_mismatches.append(
                        f"Table '{table_name}', column '{model_col.name}': "
                        f"Model expects {model_type}, DB has {db_type}"
                    )
    
    if type_mismatches:
        pytest.fail(
            "Column type mismatches found:\n" + "\n".join(type_mismatches)
        )


def get_table_foreign_keys(engine, table_name):
    """Get foreign keys from a table using synchronous inspection."""
    # Convert async URL to sync URL for inspection
    sync_url = str(engine.url).replace('sqlite+aiosqlite', 'sqlite')
    sync_engine = create_engine(sync_url)
    inspector = inspect(sync_engine)
    fks = inspector.get_foreign_keys(table_name)
    sync_engine.dispose()
    return fks


@pytest.mark.asyncio
async def test_foreign_keys_exist():
    """Verify all foreign key constraints exist."""
    engine = get_async_engine()
    
    expected_fks = {
        'projects': [('user_id', 'users', 'id')],
        'datasets': [('project_id', 'projects', 'id')],
        'operation_history': [
            ('project_id', 'projects', 'id'),
            ('dataset_id', 'datasets', 'id')
        ],
        'agents': [('user_id', 'users', 'id')]
    }
    
    missing_fks = []
    
    for table_name, fks in expected_fks.items():
        db_fks = get_table_foreign_keys(engine, table_name)
        db_fk_tuples = [
            (fk['constrained_columns'][0], fk['referred_table'], fk['referred_columns'][0])
            for fk in db_fks
        ]
        
        for expected_fk in fks:
            if expected_fk not in db_fk_tuples:
                missing_fks.append(
                    f"Table '{table_name}': Missing FK {expected_fk}"
                )
    
    if missing_fks:
        pytest.fail(
            "Missing foreign key constraints:\n" + "\n".join(missing_fks)
        )


def get_table_indexes(engine, table_name):
    """Get indexes from a table using synchronous inspection."""
    # Convert async URL to sync URL for inspection
    sync_url = str(engine.url).replace('sqlite+aiosqlite', 'sqlite')
    sync_engine = create_engine(sync_url)
    inspector = inspect(sync_engine)
    indexes = inspector.get_indexes(table_name)
    sync_engine.dispose()
    return indexes


@pytest.mark.asyncio
async def test_indexes_exist():
    """Verify all required indexes exist."""
    engine = get_async_engine()
    
    expected_indexes = {
        'users': ['ix_users_email'],
        'projects': ['ix_projects_user_id'],
        'datasets': ['ix_datasets_project_id'],
        'operation_history': [
            'ix_operation_history_created_at',
            'ix_operation_history_dataset_id',
            'ix_operation_history_project_id'
        ],
        'agents': ['ix_agents_user_id']
    }
    
    missing_indexes = []
    
    for table_name, indexes in expected_indexes.items():
        db_indexes = get_table_indexes(engine, table_name)
        db_index_names = [idx['name'] for idx in db_indexes]
        
        for expected_idx in indexes:
            if expected_idx not in db_index_names:
                missing_indexes.append(
                    f"Table '{table_name}': Missing index {expected_idx}"
                )
    
    if missing_indexes:
        pytest.fail(
            "Missing indexes:\n" + "\n".join(missing_indexes)
        )