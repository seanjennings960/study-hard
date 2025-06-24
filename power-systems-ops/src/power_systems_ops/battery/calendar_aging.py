from typing import Optional
from pathlib import Path
import re
import numpy as np
import pandas as pd

import power_systems_ops.battery.feature_extraction as ext
from power_systems_ops.battery.data_import import import_datafile, find_files


T_calendar = [10, 23, 35, 45]


def filt_common_temp(cap, atol=5):
    filt = [np.isclose(cap[:, 1], T, atol=atol) for T in T_calendar]
    i = np.argmax([np.sum(f) for f in filt])
    return cap[filt[i]]



def extract_two_digits(s: str) -> Optional[int]:
    """
    If `s` ends with 'T' followed by any two digits, return that number as an int.
    Otherwise return None.
    """
    m = re.search(r'T(\d{2})$', s)
    return int(m.group(1)) if m else None


def default_temperature(files, T_amb):
    # Some of the ambient temperatures measurements are missing, so we'll replace them with 
    # default values: the start-up and end checkups have their filenames ending in T10, T23, T45
    # For all the other checkups, we'll just assume it's the ambient temperature. 
    T_file = [extract_two_digits(f.stem) for f in files]
    return np.array(
        [T_f if T_f is not None else T_amb
         for T_f in T_file]
    )


def extract_calendar(df):
    c = ext.capacity(ext.df_capacity(df))['Q_mean']
    T = df['amb_temp'].mean()
    return (c, T)


def capacity_vs_time(files, T_amb):
    cap = np.array([extract_calendar(import_datafile(f)) for f in files])
    
    T_default = default_temperature(files, T_amb)
    T_ext = cap[:, 1]
    mask = np.isnan(T_ext) 
    T_ext[mask] = T_default[mask]
    
    f_cap = filt_common_temp(cap)
    print(f"Found {len(f_cap)} at same temp")
    if len(f_cap) < 2:
        raise KnownIssue()
    # The logic here is a bit fragile and dependent on which values are filtered...
    # Should really read the meta file for the dates!
    t = np.cumsum([0, 5, 4] + [8] * (len(f_cap) - 3))
    t = t[:len(f_cap)]
    # (t, capacity, T_amb)
    return (t, f_cap[:, 0], f_cap[:, 1])
    

def calendar_degradation(files, T_amb):
    t, cap, _ = capacity_vs_time(files, T_amb)
    
    A = np.c_[np.ones_like(t), t]
    b = cap
    x, error, _, _ = np.linalg.lstsq(A, b)
    c0, beta = x
    print(f"Found (c0, beta, error): ({c0}, {beta}, {error})")
    return -beta


class KnownIssue(Exception):
    pass


def extract_results(study_dir: Path):
    meta_df = pd.read_csv(study_dir / "experiments_meta.csv")
    results = []
    for i, row in meta_df.iterrows():
        print(f"experiment {i}")
        if row.type != 'k':
            print("Skipping cycle aging")
            continue
        experiment_files = find_files(study_dir, row.stage, row.type, row.tp, row.cell)
        try:
            results.append((row, calendar_degradation(experiment_files, row.amb_temp_tp)))
        except KnownIssue:
            print(f"Warning: failed on {row.serial}")
    return results