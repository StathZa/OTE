import multiprocessing as mp

pollaploi_query = f"""
    SELECT
        *
    FROM  energy_efficiency.pollaploi
    WHERE MOD(HASH(paroxos, paroxi, etos), {min(25, mp.cpu_count())}) = 
"""

parohes_cosmote_query = """
    SELECT
        paroxi, 
        site_code, 
        site_name 
    FROM energy_efficiency.parohes_cosmote
"""