from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import insert


def upsert_dataframe(engine, df, unique_key_columns, table_name, schema="public"):
    """
    Performs a bulk INSERT OR UPDATE of a pandas DataFrame to a Postgresql table.
    This function inserts rows from the DataFrame. If a row violates a unique
    constraint (specified by `unique_key_columns`), it updates the
    existing row with the new values from the DataFrame instead.
    """
    metadata = MetaData()
    metadata.reflect(bind=engine, schema=schema)
    table = metadata.tables[f"{schema}.{table_name}"]
    if df.empty: return
    # Convert DataFrame to a list of dictionaries for SQLAlchemy
    data_to_insert = df.to_dict(orient='records')
    # The initial INSERT statement
    stmt = insert(table).values(data_to_insert)
    # Dynamically create the 'set_' dictionary for the ON CONFLICT clause.
    # This dictionary maps columns to be updated to the new values from
    # the incoming data (referred to by 'stmt.excluded').
    # We update all columns that are NOT part of the unique key.
    update_cols = {
        col.name: col
        for col in stmt.excluded
        if col.name not in unique_key_columns
    }
    # Construct the final UPSERT statement with the ON CONFLICT clause
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=unique_key_columns,
        set_=update_cols
    )
    # Execute the statement within a transaction
    with engine.begin() as conn:
        conn.execute(upsert_stmt)


def insert_if_not_exists(engine, df, unique_key_columns, table_name, schema="public"):
    """
    Performs a bulk INSERT IGNORE of a pandas DataFrame to a PostgreSQL table.

    This function attempts to insert rows from the DataFrame. If a row violates
    a unique constraint (specified by `unique_key_columns`), the database
    ignores the new row and keeps the existing one (ON CONFLICT DO NOTHING).

    Args:
        engine: SQLAlchemy engine object.
        df (pd.DataFrame): The data to insert.
        unique_key_columns (list): List of column names constituting the unique constraint.
        table_name (str): Target table name.
        schema (str): Target schema name.
    """
    if df.empty:
        return

    metadata = MetaData()
    # Reflect the table structure from the database
    metadata.reflect(bind=engine, schema=schema)

    # Handle potential key errors if schema/table string formatting varies
    full_table_name = f"{schema}.{table_name}"
    if full_table_name not in metadata.tables:
        raise ValueError(f"Table {full_table_name} not found in database metadata.")

    table = metadata.tables[full_table_name]

    # Convert DataFrame to a list of dictionaries for SQLAlchemy
    data_to_insert = df.to_dict(orient='records')

    # The initial INSERT statement
    stmt = insert(table).values(data_to_insert)

    # Construct the INSERT IGNORE statement with ON CONFLICT DO NOTHING
    # index_elements specifies the columns that trigger the conflict check
    do_nothing_stmt = stmt.on_conflict_do_nothing(
        index_elements=unique_key_columns
    )

    # Execute the statement within a transaction
    with engine.begin() as conn:
        conn.execute(do_nothing_stmt)
