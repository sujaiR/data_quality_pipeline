# Simple graph definition for the data quality pipeline
# nodes: profile -> detect -> generate -> apply -> check -> loop or end

data_quality_graph = {
    'start': 'profile',
    'nodes': {
        'profile': {
            'fn': 'profile_data',
            'next': 'detect'
        },
        'detect': {
            'fn': 'detect_anomalies',
            'next': 'generate'
        },
        'generate': {
            'fn': 'generate_rules',
            'next': 'apply'
        },
        'apply': {
            'fn': 'apply_rules',
            'next': {
                'cond_key': 'anomaly_count',
                'op': 'gt',
                'value': 0,
                'true': 'detect',   # re-run detect after applying
                'false': None
            }
        }
    }
}
