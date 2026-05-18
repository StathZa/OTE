#!/usr/bin/env python3

import vertica_python
import pandas as pd
import numpy as np
import multiprocessing as mp
from vertica_python.errors import QueryError
from datetime import datetime
from utils.logger import logger
from utils.table_reader import read_vertica_table, read_vertica_table_with_multiprocessing
from static.queries import pollaploi_query, parohes_cosmote_query
from static.type_mapping import type_mapping
from dotenv import dotenv_values


# Configuration
env_path = os.path.expanduser("~/.env")

if os.path.exists(env_path):
    try:
        os.chmod(env_path, 0o600)
        print(f"Set permissions on {env_path}")
        report.add(f"Set permissions on {env_path}")
    except PermissionError:
        print(f"Warning: Could not set permissions on {env_path}")
        report.warn(f"Warning: Could not set permissions on {env_path}")
else:
    print(f"ERROR: {env_path} not found!")
    report.err(f"ERROR: {env_path} not found!")

# Load environment variables
load_dotenv(env_path)

# Validate required variables are present
required = ['VERTICA_HOST', 'VERTICA_PORT', 'VERTICA_USER', 
            'VERTICA_PASSWORD', 'VERTICA_DATABASE']
missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f"ERROR: Missing environment variables: {missing}")
    report.err(f"ERROR: Missing environment variables: {missing}")

print("Loaded credentials from .env")

# Configure connection
conn_info = {
    'host': os.getenv('VERTICA_HOST'),
    'port': int(os.getenv('VERTICA_PORT', 5433)),
    'user': os.getenv('VERTICA_USER'),
    'password': os.getenv('VERTICA_PASSWORD'),
    'database': os.getenv('VERTICA_DATABASE'),
    'tlsmode': 'disable'
}

# Establish a connection to Vertica
connection = vertica_python.connect(**conn_info)
cursor = connection.cursor()

logger.info(f"Logging started at {datetime.now()}")

# Read tables
logger.info("Reading table:  energy_efficiency.pollaploi")
df = read_vertica_table_with_multiprocessing(conn_info, pollaploi_query)

logger.info("Reading table: energy_efficiency.parohes_cosmote")
sites = read_vertica_table(conn_info, parohes_cosmote_query)

# Apply basic data processing
logger.info("Processing data: filling N/A values, applying type casting, and creating required columns.")

# Convert "paroxi" to string
df["paroxi"] = pd.to_numeric(df["paroxi"], errors="coerce") # changed
df["paroxi"] = df["paroxi"].fillna(0).astype(int).astype(str)

df["kodikos_pollaplou_logariasmou_xxxxxxx"]=df["kodikos_pollaplou_logariasmou_xxxxxxx"].astype(str)
df["kodikos_pollaplou_logariasmou_xxxxxxx"]=df["kodikos_pollaplou_logariasmou_xxxxxxx"].str.replace('.0', '')

df["arithmos_paroxis"]=df["arithmos_paroxis"].astype(str)
df["arithmos_paroxis"]=df["arithmos_paroxis"].str.replace('.0', '', regex=False)

df["axia_energeias_ekdothentos_logariasmou"]=df["axia_energeias_ekdothentos_logariasmou"].fillna(0).astype(float)
df["fpa_energeias_ekdothentos_logariasmou"]=df["fpa_energeias_ekdothentos_logariasmou"].fillna(0).astype(float)
df["ert_ekdothentos_logariasmou"]=df["ert_ekdothentos_logariasmou"].fillna(0).astype(float)
df["logariasmos_kat_ektimisi_enanti_meion"]=df["logariasmos_kat_ektimisi_enanti_meion"].fillna(0).astype(float)
df["axia_energeias_logariasmou_enanti_meion"]=df["axia_energeias_logariasmou_enanti_meion"].fillna(0).astype(float)
df["fpa_logariasmou_enanti_meion"]=df["fpa_logariasmou_enanti_meion"].fillna(0).astype(float)
df["ert_logariasmou_enanti_meion"]=df["ert_logariasmou_enanti_meion"].fillna(0).astype(float)
df["diafores_xrewseis_pistwseis"]=df["diafores_xrewseis_pistwseis"].fillna(0).astype(float)
df["xrewsh_telous_ape"]=df["xrewsh_telous_ape"].fillna(0).astype(float)
df["fpa_telous_ape"]=df["fpa_telous_ape"].fillna(0).astype(float)
df["eidikos_foros_katanalwshs"]=df["eidikos_foros_katanalwshs"].fillna(0).astype(float)
df["poso_dik_ektel_telwn_ergasiwn"]=df["poso_dik_ektel_telwn_ergasiwn"].fillna(0).astype(float)
df["synolo_xamhlou_fpa"]=df["synolo_xamhlou_fpa"].fillna(0).astype(float)
df["synolo_ypshlou_fpa"]=df["synolo_ypshlou_fpa"].fillna(0).astype(float)
df["axia_endiamesou"]=df["axia_endiamesou"].fillna(0).astype(float)
df["synolo_energeias"]=df["synolo_energeias"].fillna(0).astype(float)
df["synolo_fpa_reumatos"]=df["synolo_fpa_reumatos"].fillna(0).astype(float)
df["synolo_fpa_yphresiwn"]=df["synolo_fpa_yphresiwn"].fillna(0).astype(float)
df["synoliko_fpa"]=df["synoliko_fpa"].fillna(0).astype(float)
df["synolo_ert"]=df["synolo_ert"].fillna(0).astype(float)
df["dhm_telh_dhm_foros"]=df["dhm_telh_dhm_foros"].fillna(0).astype(float)
df["telos_akinhths_periousias"]=df["telos_akinhths_periousias"].fillna(0).astype(float)
df["dosh_eeta"]=df["dosh_eeta"].fillna(0).astype(float)
df["plhrwteo_poso"]=df["plhrwteo_poso"].fillna(0).astype(float)
df["synolo_trexontos_mhnos"]=df["synolo_trexontos_mhnos"].fillna(0).astype(float)
df["energy_cost"]=df["energy_cost"].fillna(0).astype(float)

df["imera_teleutaias_katametrisis"]=df["imera_teleutaias_katametrisis"].fillna(0).astype(int)
df["minas_teleutaias_katametrisis"]=df["minas_teleutaias_katametrisis"].fillna(0).astype(int)
df["etos_teleutaias_katametrisis"]=df["etos_teleutaias_katametrisis"].fillna(0).astype(int)
df["imera_prohgoumenis_katametrisis"]=df["imera_prohgoumenis_katametrisis"].fillna(0).astype(int)
df["minas_prohgoumenis_katametrisis"]=df["minas_prohgoumenis_katametrisis"].fillna(0).astype(int)
df["etos_prohgoumenis_katametrisis"]=df["etos_prohgoumenis_katametrisis"].fillna(0).astype(int)

df["energy_consumption_kwh"]=df["energy_consumption_kwh"].fillna(0).astype(float)
df["number_of_days"]=df["number_of_days"].fillna(0).astype(float)

# Convert "paroxi" to string
df["kwdikos_eett"]=df["kwdikos_eett"].astype(str)
df["kwdikos_eett"]=df["kwdikos_eett"].str.replace('.00', '',regex=False)
df["etos"]=df["etos"].fillna(0).astype(int) # changed
df["logistikos_minas"]=df["logistikos_minas"].fillna(0).astype(int) # changed
df["perifereia"]=df["perifereia"].fillna(0).astype(int)
df["perifereia"]=df["perifereia"].astype(str)
df["grafeio"]=df["grafeio"].fillna(0).astype(int)
df["grafeio"]=df["grafeio"].astype(str)
df["arithmos_paroxis"]=df["arithmos_paroxis"].astype(str)
df["arithmos_paroxis"]=df["arithmos_paroxis"].str.replace('.0', '',regex=False)

df["a_a_ekdosis_logariasmou"]=df["a_a_ekdosis_logariasmou"].astype(str)
df["a_a_ekdosis_logariasmou"]=df["a_a_ekdosis_logariasmou"].str.replace('.00', '',regex=False)


# Extract date from 'hmeromhnia_teleutaias_katametrhshs'
df['hmeromhnia_teleutaias_katametrhshs']=df['hmeromhnia_teleutaias_katametrhshs'].str.split(" ", expand=True)[0]
df['hmeromhnia_teleutaias_katametrhshs']=pd.to_datetime(df['hmeromhnia_teleutaias_katametrhshs'],
                                                        dayfirst=True, errors='coerce')

# Extract date from 'hmeromhnia_prohgoumenis_katametrhshs'
df['hmeromhnia_prohgoumenis_katametrhshs']=df['hmeromhnia_prohgoumenis_katametrhshs'].str.split(" ", expand=True)[0]
df['hmeromhnia_prohgoumenis_katametrhshs']=pd.to_datetime(df['hmeromhnia_prohgoumenis_katametrhshs'],
                                                          dayfirst=True, errors='coerce')

df["imera_teleutaiou_logariasmou"]=df["imera_teleutaiou_logariasmou"].fillna(0).astype(int) # changed
df["minas_teleutaiou_logariasmou"]=df["minas_teleutaiou_logariasmou"].fillna(0).astype(int) # changed
df["etos_teleutaiou_logariasmou"]=df["etos_teleutaiou_logariasmou"].fillna(0).astype(int) # changed

# Create field 'Date_Bill'
cols=["imera_teleutaiou_logariasmou", "minas_teleutaiou_logariasmou", "etos_teleutaiou_logariasmou"]
df['Date_Bill']=df[cols].apply(lambda x: '/'.join(x.values.astype(str)), axis="columns")
df['Date_Bill']=pd.to_datetime(df['Date_Bill'], dayfirst=True, errors="coerce")

df = df.sort_values(by=["paroxi", "Date_Bill"], ascending=[True, True]).reset_index(drop=True)

# Extract date from 'Λογιστικό Date'
df['logistiko_date']=df['logistiko_date'].str.split(" ",expand=True)[0]
df['logistiko_date'] = pd.to_datetime(df['logistiko_date'], dayfirst=True, errors='coerce')
df['actual_date']=df['actual_date'].str.split(" ",expand=True)[0]
df['actual_date']=pd.to_datetime(df['actual_date'], dayfirst=True, errors='coerce')
df['power_off_date']=df['power_off_date'].str.split(" ",expand=True)[0]
df['power_off_date']=pd.to_datetime(df['power_off_date'], dayfirst=True, errors='coerce')

# Create last_date & previous_date Fields
df["last_date"]=df["hmeromhnia_teleutaias_katametrhshs"]
df["previous_date"]=df["hmeromhnia_prohgoumenis_katametrhshs"]

logger.info("Filling last_date & previouis_date N/A values for final invoice and special bill type")
ektaktoi=df[df["bill_type"] == 'Έκτακτος']

enanti=df[df["bill_type"] == 'Έναντι']

df = df.loc[(df["bill_type"] == 'Εκκαθαριστικός') | (df["bill_type"] == 'Τελικός')]

# Change 'previous_date' for Εκκαθαριστικούς & Τελικούς
df.loc[(df['previous_date'].isnull()) & (df['paroxi']==(df['paroxi'].shift(1))), "previous_date"] = df['last_date'].shift(1)
df.loc[(df['last_date'].isnull())
       & (df['previous_date'].isnull()), "previous_date"] = df["Date_Bill"] - pd.to_timedelta(30, unit='d')


logger.info("Filling last_date & previous_date N/A values for account_payment bill type")
df = pd.concat([df, enanti], ignore_index=True)


df = df.sort_values(by=["paroxi", "Date_Bill"], ascending=[True, True]).reset_index(drop=True)


df.loc[(df['last_date'].isnull()) & ((df["bill_type"] == 'Εκκαθαριστικός')
                                     | (df["bill_type"] == 'Τελικός')), "last_date"] = df["previous_date"].shift(-1)
df.loc[(df['last_date'].isnull()) & ((df["bill_type"] == 'Εκκαθαριστικός')
                                     | (df["bill_type"] == 'Τελικός')), "last_date"] = df["Date_Bill"]

df.loc[
    (df['last_date'].isnull()) &
    (df['previous_date'].notnull()) &
    ((df["bill_type"] == 'Εκκαθαριστικός') | (df["bill_type"] == 'Τελικός')),
    "last_date"
] = df['previous_date'] + pd.to_timedelta(30, unit='d')


df.loc[(df['last_date'].isnull()) & (df["bill_type"] == "Έναντι"), "last_date"] = df["Date_Bill"]

df.loc[(df['hmeromhnia_teleutaias_katametrhshs'].isnull())
       & (df['hmeromhnia_prohgoumenis_katametrhshs'].isnull())
       & (df["bill_type"] == "Έναντι")
       & (df['paroxi'].eq(df['paroxi'].shift(1))), "previous_date"] = df["last_date"].shift(1)

df.loc[(df['hmeromhnia_teleutaias_katametrhshs'].isnull())
       & (df['hmeromhnia_prohgoumenis_katametrhshs'].isnull())
       & (df["bill_type"] == "Έναντι")
       & (df['paroxi'].ne(df['paroxi'].shift(1))), "previous_date"] = df["Date_Bill"] - pd.to_timedelta(30, unit='d')

df.loc[(df['hmeromhnia_teleutaias_katametrhshs'].isnull())
       & (df['hmeromhnia_prohgoumenis_katametrhshs'] >= df['hmeromhnia_prohgoumenis_katametrhshs'].shift(1))
       & (df["bill_type"] == "Έναντι") & (df['paroxi'] == (df['paroxi'].shift(1)))
       & (df['paroxos'] == (df['paroxos'].shift(1))), "previous_date"] = df["hmeromhnia_teleutaias_katametrhshs"].shift(1)

df.loc[(df['hmeromhnia_teleutaias_katametrhshs'].isnull())
       & (df['hmeromhnia_prohgoumenis_katametrhshs'] < df['hmeromhnia_prohgoumenis_katametrhshs'].shift(1))
       & (df["bill_type"] == "Έναντι")&(df['paroxi'] == (df['paroxi'].shift(1)))
       & (df['paroxos'] == (df['paroxos'].shift(1))), "previous_date"] = df["hmeromhnia_teleutaias_katametrhshs"]

df.loc[(df['hmeromhnia_teleutaias_katametrhshs'].isnull())
       & (df['hmeromhnia_prohgoumenis_katametrhshs']>df['hmeromhnia_prohgoumenis_katametrhshs'].shift(1))
       & (df["bill_type"] == "Έναντι")
       & (df['paroxi'] == (df['paroxi'].shift(1))), "previous_date"] = df["hmeromhnia_teleutaias_katametrhshs"].shift(1)

df.loc[(df['hmeromhnia_prohgoumenis_katametrhshs'] == df['hmeromhnia_prohgoumenis_katametrhshs'].shift(1))
       & (df['hmeromhnia_teleutaias_katametrhshs'] >df ['hmeromhnia_teleutaias_katametrhshs'].shift(1))
       & (df["bill_type"] == "Έναντι") & (df['paroxi'] == (df['paroxi'].shift(1)))
       & (df['paroxos'] == df['paroxos'].shift(1))
       & (df['bill_type'] == df['bill_type'].shift(1)), "previous_date"] = df["hmeromhnia_teleutaias_katametrhshs"].shift(1)

df.loc[(df['last_date'].notnull())
        & (df['previous_date'].isnull())
        & (df["bill_type"]== "Έναντι")
        & (df['paroxi'].ne(df['paroxi'].shift(1)))
        & (df['paroxi'].ne(df['paroxi'].shift(-1))), "previous_date"] = df["last_date"] - pd.to_timedelta(30, unit='d')

df.loc[(df['last_date'].notnull())
        & (df['previous_date'].isnull())
        & (df["bill_type"]== "Έναντι")
        &(df['paroxi'].eq(df['paroxi'].shift(1))), "previous_date"] = df["last_date"].shift(1)

df.loc[(df['last_date'].notnull())
        & (df['previous_date'].isnull())
        & (df["bill_type"]== "Έναντι")
        &(df['paroxi']!=(df['paroxi'].shift(1)))
        &(df['paroxi']==(df['paroxi'].shift(-1))), "previous_date"] = df['last_date'] - pd.to_timedelta(30, unit='d')

df.loc[(df['last_date'].notnull())
        & (df['previous_date'].isnull())
        & (df["bill_type"]== "Έναντι")
        &(df['paroxi']==(df['paroxi'].shift(1)))
        &(df['paroxi']!=(df['paroxi'].shift(-1))), "previous_date"] = df['last_date'].shift(1)

df.loc[(df['last_date'].notnull())
        & (df['previous_date'].isnull())
        & (df["bill_type"]== "Έναντι")
        &(df['paroxi']==(df['paroxi'].shift(1)))
        &(df['paroxi']==(df['paroxi'].shift(-1))), "previous_date"] = df['last_date'].shift(1)


# Επαναφέρουμε τους Έκτακτους στο df


df = pd.concat([df, ektaktoi])

df = df.sort_values(by=["paroxi", "Date_Bill"], ascending=[True, True]).reset_index(drop=True)

df.loc[(df['last_date'].isnull())
       & (df['previous_date'].isnull())
       & (df["bill_type"] == "Έκτακτος"), "previous_date"] = df["logistiko_date"]

df.loc[(df['last_date'].isnull())
       & (df['previous_date'].isnull())
       & (df["bill_type"] == "Έκτακτος"), "last_date"] = df["logistiko_date"]

df.loc[(df['last_date'].isnull())
       & (df['previous_date'].notnull())
       & (df["bill_type"] == "Έκτακτος"), "last_date"] = df['previous_date']

#Change

df["days"]=(df["last_date"]-df["previous_date"]).dt.days
df.loc[(df['days']<=0), "days"] = 1

df["parousa_endeiksi"]=df["parousa_endeiksi"].astype(float) # changed
df["prohgoumeni_endeiksi"]=df["prohgoumeni_endeiksi"].fillna(0).astype(float)

df["katanalwsh_kwh"]=df["katanalwsh_kwh"].astype(float)

df["synt_wxv"]=df["synt_wxv"].astype(float)

df["energy_consumption_kwh"]=df["energy_consumption_kwh"].astype(float)

df["energy_cost"]=df["energy_cost"].astype(float)

df["number_of_days"]=df["number_of_days"].astype(float)

#fixed
df['min_metrisi'] = np.nanmin(df[['parousa_endeiksi', 'prohgoumeni_endeiksi']].values, axis=1)

df['max_metrisi'] = df[['parousa_endeiksi', 'prohgoumeni_endeiksi']].max(axis=1, skipna=True)

# correct_proigoumeni_metrisi field
df.loc[(df['parousa_endeiksi'] > df['prohgoumeni_endeiksi']), 'correct_proigoumeni_metrisi'] = df['min_metrisi']
df.loc[(df['parousa_endeiksi'] <= df['prohgoumeni_endeiksi']), 'correct_proigoumeni_metrisi'] = df['max_metrisi']

# correct_parousa_metrisi field
df['correct_parousa_metrisi']=df['max_metrisi']

df.loc[(df['parousa_endeiksi'] < df['prohgoumeni_endeiksi'])
       & (df['max_metrisi']<100000), 'correct_parousa_metrisi'] = 100000 + df['min_metrisi']

df.loc[(df['parousa_endeiksi'] < df['prohgoumeni_endeiksi'])
       & (df['max_metrisi']>100000), 'correct_parousa_metrisi'] = 1000000 + df['min_metrisi']


df['last_date']=pd.to_datetime(df['last_date'], dayfirst=True, errors='coerce')
df['previous_date']=pd.to_datetime(df['previous_date'], dayfirst=True, errors='coerce')

df["delta_days"]= df["days"]

df["delta_days"].isnull().sum(axis = 0)


df["delta_days"].isnull().sum(axis = 0)

# Daily Consumption Field
df.loc[(df['bill_type'] == 'Εκκαθαριστικός')
       | (df['bill_type'] == 'Τελικός'), 'daily_consumption'] = df['katanalwsh_kwh'] / df["delta_days"]
df.loc[(df['bill_type'] == 'Έναντι'), 'daily_consumption'] = df['energy_consumption_kwh'] / df["delta_days"]

# Κωδικός Τιμολογίου
df["new_bill_code"] = "Γ21"
df.loc[(df['mv_lv'] == 'MV'), 'new_bill_code'] = df['mv_lv']
df.loc[((df['neos_kodikos_timologiou'] == '22')
        | (df['neos_kodikos_timologiou'] == 'Γ22-3Φ')
        | (df['neos_kodikos_timologiou'] == 'Γ22α-3Φ')
        | (df['neos_kodikos_timologiou'] == 'Γ22α')
        | (df['neos_kodikos_timologiou'] == 'Γ22')
        | (df['neos_kodikos_timologiou'] == 'Ε22')), 'new_bill_code'] = "Γ22"

ek = df[(df["bill_type"] == "Εκκαθαριστικός") | (df["bill_type"] == "Τελικός")]

df['paroxi'] = pd.to_numeric(df['paroxi'], errors='coerce')
sites['paroxi'] = pd.to_numeric(sites['paroxi'], errors='coerce')

# checkpoint
df = pd.merge(df, sites,
              how='left',
              left_on=['paroxi'],
              right_on=['paroxi'])

df.loc[(df["category"] == "Cosmote BTS"), 'site_code_cosmote'] = df['site_code']
df.loc[(df["category"] == "Cosmote BTS"), 'onomasia'] = df['site_name']

df = df.drop(['site_code', 'site_name'], axis=1)

df.loc[(df["category"] == "Cosmote BTS"), 'siteid'] = df['site_code_cosmote']
df.loc[((df["category"] == "BUILDING") | (df["category"] == "CABIN")), 'siteid'] = df['kwdikos_eett']

# Coordinates
coordinates=pd.read_excel("./excel_files/coordinates.xlsx", engine='openpyxl')

coordinates["eett"]=coordinates["eett"].astype(int)
coordinates["eett"]=coordinates["eett"].astype(str)

coordinates=coordinates.drop_duplicates(subset=['eett'], keep='first')
coordinates=coordinates.drop_duplicates(subset=['latitude','longitude'], keep='first')

coordinates2=pd.read_excel("./excel_files/coordinates_missing.xlsx",
                           engine='openpyxl')

coordinates2["siteid"]=coordinates2["siteid"].astype(int)
coordinates2["siteid"]=coordinates2["siteid"].astype(str)
coordinates2=coordinates2.drop_duplicates(subset=['siteid'], keep='first')
coordinates2=coordinates2.drop_duplicates(subset=['latitude', 'longitude'], keep='first')

coordinates3=pd.read_excel("./excel_files/coordinates_BTS.xlsx",
                           engine='openpyxl')

coordinates3["siteid"]=coordinates3["siteid"].astype(int)
coordinates3["siteid"]=coordinates3["siteid"].astype(str)


coordinates3=coordinates3.drop_duplicates(subset=['siteid'], keep='first')

coordinates3=coordinates3.drop_duplicates(subset=['latitude','longitude'], keep='first')

coordinates = coordinates.rename(columns={'eett': 'siteid'})

coordinates = pd.concat([coordinates, coordinates2], ignore_index=True)

coordinates = pd.concat([coordinates, coordinates3], ignore_index=True)

coordinates=coordinates.drop_duplicates(subset=['siteid'], keep='first')

# Convert siteid to numeric safely, while keeping NaN values
df["siteid"] = pd.to_numeric(df["siteid"], errors="coerce").astype("Int64")  # Keeps NaN as <NA>, avoids conversion error
coordinates["siteid"] = pd.to_numeric(coordinates["siteid"], errors="coerce").astype("Int64")

# Convert back to string, keeping NaNs
df["siteid"] = df["siteid"].astype(str).replace("<NA>", "")
coordinates["siteid"] = coordinates["siteid"].astype(str).replace("<NA>", "")

# Trim spaces (if any)
df["siteid"] = df["siteid"].str.strip()
coordinates["siteid"] = coordinates["siteid"].str.strip()


# Check how many matching siteid values exist now
common_siteids = set(df["siteid"].unique()) & set(coordinates["siteid"].unique())

df = pd.merge(df, coordinates,
              how='left',
              on=['siteid'])


############################################## Create Alerts ##########################################################

# ##### Alert 1 - Μεγάλη Καθυστέρηση του τελευταίου Εκκαθαριστικού

logger.info("Creating alert 1")
df = df.sort_values(by=["paroxi", "Date_Bill"], ascending=[True, True]).reset_index(drop=True)

max_date=ek[["paroxi", "last_date"]]

max_date = max_date.groupby("paroxi").max().reset_index()

max_date = max_date.rename(columns={"last_date": "last_date_ek"})

max_date['paroxi'] = max_date['paroxi'].astype(int).astype(str)
df['paroxi'] = df['paroxi'].astype(int).astype(str)

df = pd.merge(df, max_date,  how='left', left_on=['paroxi'], right_on=['paroxi'])

df.loc[(df['paroxi'] != df['paroxi'].shift(-1)) & (df["bill_type"] == "Έναντι"), 'last_enanti'] = "1"

df.loc[(df["last_enanti"] == "1")
       & (df['last_date'] != df['last_date_ek']), 'days_from_last_ek'] = (df['last_date']-df['last_date_ek']).dt.days

df.loc[(df["days_from_last_ek"] > 200), 'alert_kathisterisis'] = "1"


# ##### Alert 2 - Υψηλός Εκκαθαριστικός
logger.info("Creating alert 2")
median_consumption=ek[["paroxi","daily_consumption"]]

median_consumption=median_consumption.groupby("paroxi").median().reset_index()

median_consumption = median_consumption.rename(columns={"daily_consumption": "median_daily_consumption"})
median_consumption['paroxi'] = median_consumption['paroxi'].astype(int).astype(str)

df = pd.merge(df, median_consumption,
              how='left',
              left_on=['paroxi'],
              right_on=['paroxi'])

df["perc_consumption"]= np.abs(df["daily_consumption"] / df["median_daily_consumption"])
df["perc_consumption"]=df["perc_consumption"].astype(float)

df.loc[((df["daily_consumption"] > 0)
        & (df["median_daily_consumption"] > 0)
        & ((df["bill_type"] == "Εκκαθαριστικός")
           | (df["bill_type"] == "Τελικός"))
        & (df["perc_consumption"] > 2)
        & (df["energy_consumption_kwh"] > 0)
        & (df["correct_parousa_metrisi"]-df["correct_proigoumeni_metrisi"]>20)), 'alert_high_ekkatharistikos'] = "1"

# ##### Alert 3 - Υψηλός Έναντι
logger.info("Creating alert 3")
df.loc[((df["daily_consumption"] > 0)
        & (df["median_daily_consumption"] > 0)
        & (df["bill_type"] == "Έναντι")
        & (df["perc_consumption"] > 2)
        & (df["energy_consumption_kwh"] > 0)), 'alert_high_enanti'] = "1"


# ##### Alert 4 - Round Consumption
logger.info("Creating alert 4")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός")
         | (df["bill_type"] == "Τελικός"))
        & (((df["parousa_endeiksi"] > 0)
            & (df["parousa_endeiksi"] % 1000 == 0))
           | ((df["prohgoumeni_endeiksi"] > 0)
              & (df["prohgoumeni_endeiksi"] % 1000 == 0))
           | ((df["katanalwsh_kwh"] > 0)
              & (df["katanalwsh_kwh"] % 1000 == 0)))
        & (df["katanalwsh_kwh"] > 0)), 'alert_round_numbers'] = "1"


# ##### Alert 5 - Μηδενικές Μετρήσεις
logger.info("Creating alert 5")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός")
         | (df["bill_type"] == "Τελικός"))
        & ((df["parousa_endeiksi"] == 0)
           | (df["prohgoumeni_endeiksi"] == 0)
           | (df["katanalwsh_kwh"] == 0)
           | ((df["max_metrisi"] - df["min_metrisi"]) == 0))), 'alert_zero_figures'] = "1"



# ##### Alert 6 - Γύρισμα Μετρητή
logger.info("Creating alert 6")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός")
         | (df["bill_type"] == "Τελικός"))
        & (df["parousa_endeiksi"] < df["prohgoumeni_endeiksi"])), 'alert_girisma_metriti'] = "1"


# ##### Alert 7 - Αλλαγή Μετρητή
logger.info("Creating alert 7")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός")
         | (df["bill_type"] == "Τελικός"))
        & (df['paroxi']==df['paroxi'].shift(1))
        & (df['arithmos_metriti']!=df['arithmos_metriti'].shift(1))
        & df['arithmos_metriti'].notnull()
        & df['arithmos_metriti'].shift(1).notnull()
        & (df['arithmos_metriti']!="00")
        & (df['arithmos_metriti'].shift(1)!="00")), 'alert_allagi_metriti'] = "1"

# ##### Alert 8 - Λάθος Μέτρηση

logger.info("Creating alert 8")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός")
         | (df["bill_type"] == "Τελικός"))
        & (df["synt_wxv"]*(df["correct_parousa_metrisi"]-df["correct_proigoumeni_metrisi"])!=df["katanalwsh_kwh"])), 'alert_check_consumption'] = "1"



# ##### Alert 9 - Consumption before 2018
logger.info("Creating alert 9")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός")
         | (df["bill_type"] == "Τελικός")
         | (df["bill_type"] == "Έναντι") )
        & (df["last_date"].dt.year>=2000)
        & (df["last_date"].dt.year<=2017)
        & (df["previous_date"].dt.year>=2000)
        & (df["previous_date"].dt.year<=2017)), 'alert_old_consumption'] = "1"



# ##### Alert 10 - Zero Consumption

logger.info("Creating alert 10")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός") | (df["bill_type"] == "Τελικός"))
        & (df["katanalwsh_kwh"]==0)), 'alert_zero_consumption'] = "1"


# ##### Alert 11 - Low Consumption
logger.info("Creating alert 11")
df.loc[(((df["bill_type"] == "Εκκαθαριστικός") | (df["bill_type"] == "Τελικός"))
        & (df["perc_consumption"]<=0.4) & (df["perc_consumption"]>0)
        & (df["katanalwsh_kwh"]>0)), 'alert_low_consumption'] = "1"


# ##### Alert 12 - Αλλαγή Παρόχου
logger.info("Creating alert 12")
df.loc[((df["paroxi"]==df["paroxi"].shift(1))
        & (df["paroxi"].shift(2)==df["paroxi"].shift(1))
        & (df["paroxos"]!=df["paroxos"].shift(1))
        & (df["paroxos"].shift(2)==df["paroxos"].shift(1))
        & (df["bill_type"] != "Έκτακτος")
        & (df["bill_type"].shift(1) != "Έκτακτος")
        & (df["bill_type"].shift(2) != "Έκτακτος")), 'alert_change_provider'] = "1"

df.loc[((df["alert_change_provider"]== "1")
        & (df["paroxi"].shift(1)==df["paroxi"].shift(-1))
        & (df["paroxos"].shift(1)==df["paroxos"].shift(-1))), 'alert_change_provider'] = ""


# ##### Alarms

logger.info("Creating alarms")
df.loc[(df["alert_high_ekkatharistikos"] == "1")
       & (df["perc_consumption"] > 3), 'alarm_priority'] = 4

df.loc[(df["alert_high_ekkatharistikos"] == "1")
       & (df["alert_allagi_metriti"] == "1")
       & (df["perc_consumption"] > 3), 'alarm_priority'] = 3

df.loc[(df["alert_high_ekkatharistikos"] == "1")
       & (df["alert_girisma_metriti"] == "1")
       & (df["perc_consumption"] > 3), 'alarm_priority'] = 2

df.loc[(df["alert_high_ekkatharistikos"] == "1")
       & (df["alert_girisma_metriti"] == "1")
       & (df["alert_allagi_metriti"] == "1")
       & (df["perc_consumption"] > 3), 'alarm_priority'] = 1

df.head()

df.loc[(df["alert_high_enanti"] == "1") & (df["perc_consumption"] > 3), 'alarm_priority'] = 4

df = df.rename(columns={'Date_Bill': 'date_bill', 'days': 'number_of_days2',
                        'minas_teleutaias_katametrisis':'minas_teleutaias_katametrisi'}) # fixed

df['par_dt'] = df.logistiko_date.dt.strftime('%Y%m%d').astype(str) # fixed



# Adjust data types
for column, dtype in type_mapping.items():
    if column in df.columns:
        try:
            if dtype == 'datetime64[ns]':  # Handle datetime separately
                df[column] = pd.to_datetime(df[column], errors='coerce')
            else:
                df[column] = df[column].fillna(0).astype(dtype)
        except Exception as e:
            logger.error(f"Error converting column {column} to {dtype}: {e}")

try:
    cursor.execute("DELETE FROM energy_efficiency.plpl2;")
    connection.commit()
    logger.info("Table data deleted successfully.")
except QueryError as e:
    logger.error(f"Error deleting data from the table\n{e}")

# Check for data issues BEFORE insertion

null_counts = df.isnull().sum()
if null_counts.any():
    logger.warning(f"Null values: {null_counts[null_counts > 0].to_dict()}")

problematic_chars = []
for col in df.select_dtypes(include=['object']).columns:
    prob_rows = df[df[col].astype(str).str.contains(r'[\t\n\r]', na=False, regex=True)]
    if not prob_rows.empty:
        problematic_chars.append(f"{col}: {len(prob_rows)} rows with tabs/newlines")

if problematic_chars:
    logger.warning(f"Problematic characters: {problematic_chars}")

for col in df.select_dtypes(include=['object']).columns:
    max_len = df[col].astype(str).str.len().max()
    if max_len > 1000:
        logger.warning(f"Very long strings in {col}: max length {max_len}")

partitions_to_insert = df.par_dt.unique()


logger.info("Writing data to table: energy_efficiency.plpl2")
# Extract to csv
df.to_csv("/tmp/energy_efficiency_plpl2.csv", index=False, na_rep="NaT", date_format="%Y-%m-%d %H:%M:%S")

# Clear rejected & exceptions files
open("/tmp/rejected.txt", "w").close()
open("/tmp/exceptions.txt", "w").close()

# Copy csv to table
cursor.execute("""
    COPY 
        energy_efficiency.plpl2 
    FROM '/tmp/energy_efficiency_plpl2.csv' 
    PARSER fcsvparser(delimiter=',') 
    REJECTED DATA '/tmp/rejected.txt' 
    EXCEPTIONS '/tmp/exceptions.txt';
""")

# Check rejected lines and exceptions files
with open("/tmp/rejected.txt") as rejected, open("/tmp/exceptions.txt") as exceptions:
    rejected_lines = len(rejected.readlines())
    exception_lines = len(exceptions.readlines())
    if rejected_lines > 0 :
        logger.error("Copying csv failed. Please check rejected.txt file")
    if exception_lines > 0:
        logger.error("Copying csv failed. Please check exceptions.txt file")

# Close connection
cursor.close()
connection.close()
