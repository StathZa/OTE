########################################## Read data from DB ##############################33
from utils.dependencies import pd, mp, re, logging, vertica_python, partial

def _fetch_chunk(
    conn_info:dict, 
    query: str = "",
    bucket_id: int = -1
) -> pd.DataFrame:
    """Fetch a single chunk from Vertica and return it as a DataFrame."""
    # NOTICE: using the str.format() function breaks it
    query += f" {bucket_id}"
    with vertica_python.connect(**conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        return df

def read_vertica_table_with_multiprocessing(
    conn_info: dict,
    query: str = "",
    num_workers: int = min(25, mp.cpu_count()),
    logger: logging.Logger = None
) -> pd.DataFrame:
    """Fetch a Vertica DB table by reading in chunks"""
    
    # Sanity check the number of system permissible concurrent workers and available cores
    if num_workers > mp.cpu_count():
        logger.warning("Invalid number of workers passed. Reverting to permissible range.")
        num_workers=min(25, mp.cpu_count())
    query = re.sub(pattern="\d{2}", repl=f"{num_workers}", string=query)
    logger.info(query)

    # Calculate bucket ids
#     bucket_ids = [i for i in range(num_workers)]

    # fill out the signature of function
    worker = partial(
        _fetch_chunk,
        conn_info,
        query
    )

    # Get table chunks
    with mp.Pool(processes=num_workers) as pool:
        chunks = pool.map(worker, range(num_workers))
    return pd.concat(chunks, ignore_index=True)

def read_vertica_table(
    conn_info: dict,
    query: str = ""
) -> pd.DataFrame:
    """Retrieve an entire table from a Vertica database in a single operation."""
    with vertica_python.connect(**conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        return df