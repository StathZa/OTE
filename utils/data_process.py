from utils.dependencies import re, os, pd, logging, glob, Path, load_dotenv, dotenv_values

def load_creds(ON_CONNECT: bool = os.getenv("POSIT_PRODUCT") == "CONNECT", logger: logging.Logger = None)-> dict:
    """Custom creds loader from env with environment detection capability"""
    
    if ON_CONNECT:
        logger.info(f"Running on {os.getenv('POSIT_PRODUCT')}")
        conn_info = {
                    'host': os.getenv('VERTICA_HOST'),
                    'port': int(os.getenv('VERTICA_PORT', 5433)),
                    'user': os.getenv('VERTICA_USER'),
                    'password': os.getenv('VERTICA_PASSWORD'),
                    'database': os.getenv('VERTICA_DATABASE'),
                    'tlsmode': os.getenv('VERTICA_TLSMODE', 'disable'),}
    else:
        if load_dotenv(dotenv_path=f"{Path(os.getenv('HOME'))}/dev.env",  override=True):
            conn_info = dict(dotenv_values(f"{Path(os.getenv('HOME'))}/dev.env"))
            logger.info("Loaded credentials from environment file")
        else:
            logger.warning("Failed to get credentials from environment file. Reverting to default [if exist]")
            logger.info("Available .env files:\n"+'\n'.join([f for f in os.listdir(os.getenv('HOME')) if '.env' in f]))
            load_dotenv()
            conn_info = dict(dotenv_values())

    # sanity check
    required = ['host', 'port', 'user', 'password', 'database']
    conn_info = {str(re.sub("VERTICA_", "", k)).lower(): v for k, v in conn_info.items()}

    missing = [str(re.sub(pattern="VERTICA_", repl="", string=key)) for key in required if key not in conn_info.keys()]
    if missing:
        logger.error(f"Missing env variables:\n"+'\n'.join(missing))

        conn_info['tlsmode'] = 'disable'
        logger.info("Reverting to default")
    
    return conn_info


def _dtypes_convert(df: pd.DataFrame, logger: logging.Logger = None):
    """A dtype manipulation utility"""
    
    logger.info("Filling last_date & previous_date N/A values for final invoice and special bill type")

    float_cols=[
        "axia_energeias_ekdothentos_logariasmou", "fpa_energeias_ekdothentos_logariasmou",
        "ert_ekdothentos_logariasmou", "logariasmos_kat_ektimisi_enanti_meion",
        "axia_energeias_logariasmou_enanti_meion", "fpa_logariasmou_enanti_meion",
        "ert_logariasmou_enanti_meion", "diafores_xrewseis_pistwseis",
        "xrewsh_telous_ape", "fpa_telous_ape", "eidikos_foros_katanalwshs",
        "poso_dik_ektel_telwn_ergasiwn", "synolo_xamhlou_fpa", "synolo_ypshlou_fpa",
        "axia_endiamesou", "synolo_energeias", "synolo_fpa_reumatos",
        "synolo_fpa_yphresiwn", "synoliko_fpa", "synolo_ert", "dhm_telh_dhm_foros",
        "telos_akinhths_periousias", "dosh_eeta", "plhrwteo_poso",
        "synolo_trexontos_mhnos", "energy_cost", "energy_consumption_kwh",
        "number_of_days",]

    int_cols = [
        "imera_teleutaias_katametrisis", "minas_teleutaias_katametrisis",
        "etos_teleutaias_katametrisis", "imera_prohgoumenis_katametrisis",
        "minas_prohgoumenis_katametrisis", "etos_prohgoumenis_katametrisis",
        "imera_teleutaiou_logariasmou", "minas_teleutaiou_logariasmou",
        "etos_teleutaiou_logariasmou", "etos", "logistikos_minas",]

    int_to_str_cols=["perifereia", "grafeio"]           
    str_strip_dot0=["arithmos_paroxis",              
                    "kodikos_pollaplou_logariasmou_xxxxxxx"]
    str_strip_dot00=["kwdikos_eett", "a_a_ekdosis_logariasmou"]  

    date_cols = [
        "hmeromhnia_teleutaias_katametrhshs", "hmeromhnia_prohgoumenis_katametrhshs",
        "logistiko_date", "actual_date", "power_off_date",]

    df[float_cols]=df[float_cols].fillna(0).astype(float)
    df[int_cols]=df[int_cols].fillna(0).astype(int)

    df["paroxi"]=pd.to_numeric(df["paroxi"], errors="coerce").fillna(0).astype(int).astype(str)

    for col in int_to_str_cols:
        df[col]=df[col].fillna(0).astype(int).astype(str)

    for col in str_strip_dot0:
        df[col]=df[col].astype(str).str.replace(".0", "", regex=False)

    for col in str_strip_dot00:
        df[col]=df[col].astype(str).str.replace(".00", "", regex=False)

    for col in date_cols:
        df[col]=pd.to_datetime(df[col].astype(str).str.split().str[0],
                                       dayfirst=True, errors="coerce")

    bill_date_parts=["imera_teleutaiou_logariasmou",
                         "minas_teleutaiou_logariasmou",
                         "etos_teleutaiou_logariasmou"]
    df["Date_Bill"]=pd.to_datetime(
                            df[bill_date_parts].astype(str).agg("/".join, axis=1),
                            dayfirst=True, errors="coerce")

    df["last_date"]=df["hmeromhnia_teleutaias_katametrhshs"]
    df["previous_date"]=df["hmeromhnia_prohgoumenis_katametrhshs"]

    df = df.sort_values(["paroxi", "Date_Bill"]).reset_index(drop=True)

    ektaktoi = df[df["bill_type"] == "Έκτακτος"]
    enanti = df[df["bill_type"] == "Έναντι"]
    df = df[df["bill_type"].isin(["Εκκαθαριστικός", "Τελικός"])]
    logger.info(f"Fetching {len(ektaktoi)} ektaktoi, {len(enanti)} enanti and {len(df)} Ekk or Tel")

    return df, enanti, ektaktoi