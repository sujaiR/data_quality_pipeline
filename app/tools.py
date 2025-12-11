import csv, io
from typing import Dict, Any
from collections import Counter

# Tools registry: small set of functions used by nodes
# Each function accepts and mutates the 'state' dict (or returns updates)

def profile_data(state: Dict[str, Any]) -> Dict[str, Any]:
    # expect 'data_csv' in state (string)
    data_csv = state.get('data_csv')
    if not data_csv:
        return {'profile': {}, 'row_count': 0}
    f = io.StringIO(data_csv)
    reader = csv.DictReader(f)
    rows = list(reader)
    profile = {}
    if not rows:
        return {'profile': {}, 'row_count': 0}
    columns = rows[0].keys()
    profile['columns'] = list(columns)
    profile['row_count'] = len(rows)
    col_stats = {}
    for col in columns:
        values = [r[col] for r in rows]
        missing = sum(1 for v in values if v == '' or v is None)
        unique = len(set(values))
        sample_vals = values[:5]
        col_stats[col] = {'missing': missing, 'unique': unique, 'sample': sample_vals}
    profile['col_stats'] = col_stats
    state['_internal_rows'] = rows  # keep for downstream tools (in-memory)
    return {'profile': profile, 'row_count': len(rows)}

def detect_anomalies(state: Dict[str, Any]) -> Dict[str, Any]:
    rows = state.get('_internal_rows', [])
    anomalies = []
    # very simple rule-based anomalies:
    # - numeric columns with negative values or impossible ages > 120
    # - salary containing non-digit chars
    for i, r in enumerate(rows):
        if 'age' in r:
            try:
                if r['age'] == '':
                    anomalies.append({'row': i, 'col': 'age', 'issue': 'missing'})
                else:
                    age = float(r['age'])
                    if age < 0 or age > 120:
                        anomalies.append({'row': i, 'col': 'age', 'issue': f'unrealistic_age={age}'})
            except Exception:
                anomalies.append({'row': i, 'col': 'age', 'issue': f'not_numeric:{r.get("age")}'})
        if 'salary' in r:
            s = r['salary']
            if s == '' or s is None:
                anomalies.append({'row': i, 'col': 'salary', 'issue': 'missing'})
            else:
                # check numeric
                try:
                    float(s)
                except Exception:
                    anomalies.append({'row': i, 'col': 'salary', 'issue': f'not_numeric:{s}'})
    state['anomalies'] = anomalies
    return {'anomaly_count': len(anomalies)}

def generate_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    # From anomalies, produce simple rules to fix or flag rows
    anomalies = state.get('anomalies', [])
    rules = []
    for a in anomalies:
        if a['col'] == 'age':
            rules.append({'action': 'fill_median', 'col': 'age'})
        if a['col'] == 'salary':
            rules.append({'action': 'set_null_to_0', 'col': 'salary'})
    # dedupe
    seen = set()
    final = []
    for r in rules:
        key = (r['action'], r['col'])
        if key not in seen:
            final.append(r)
            seen.add(key)
    state['rules'] = final
    return {'rules_generated': len(final)}

def apply_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    rows = state.get('_internal_rows', [])
    rules = state.get('rules', [])
    # implement two simple rule types
    for rule in rules:
        if rule['action'] == 'fill_median' and rule['col'] == 'age':
            # compute median of numeric ages
            ages = []
            for r in rows:
                try:
                    if r['age'] != '':
                        ages.append(float(r['age']))
                except Exception:
                    pass
            median = sorted(ages)[len(ages)//2] if ages else 30
            for r in rows:
                if r['age'] == '' or r['age'] is None:
                    r['age'] = str(median)
        if rule['action'] == 'set_null_to_0' and rule['col'] == 'salary':
            for r in rows:
                try:
                    if r['salary'] == '' or r['salary'] is None or not r['salary'].strip().replace('.','',1).isdigit():
                        r['salary'] = '0'
                except Exception:
                    r['salary'] = '0'
    state['_internal_rows'] = rows
    return {'applied_rules': len(rules)}

# registry
TOOLS = {
    'profile_data': profile_data,
    'detect_anomalies': detect_anomalies,
    'generate_rules': generate_rules,
    'apply_rules': apply_rules
}
