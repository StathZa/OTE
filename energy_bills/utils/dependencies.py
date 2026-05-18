#------------------------ Main Script dependencies section and environment configuration ---------------------------

# Basic imports
import io, os, re, stat, sys, csv, gc, time, logging
from typing import Optional
from dataclasses import dataclass
from functools import partial

# Path utilities
from glob import glob
from pathlib import Path

# Date and dataframe manipulation
from datetime import datetime, date
import pandas as pd
import numpy as np

# progress bar
from tqdm import tqdm

# Resource management and monitoring
import tracemalloc
from contextlib import contextmanager

# load environment variables
from dotenv import dotenv_values, load_dotenv

# Vertica connector
import vertica_python
from vertica_python import connect,errors
from vertica_python.errors import QueryError

# Filter out warnings
if not sys.warnoptions:
    import warnings
    warnings.simplefilter('ignore')
    
pd.set_option('display.max_rows', None, 'display.max_columns', None)

# Concurrency
import multiprocessing as mp

# MIME 
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication