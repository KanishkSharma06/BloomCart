import typesense

def get_typesense_client():
    return typesense.Client({
        'nodes': [{
            'host': 'fas0pie5tckr6g2hp-1.a2.typesense.net', # Yahan direct paste karein
            'port': '443',
            'protocol': 'https'
        }],
        'api_key': 'dtOFl3ANkvNJr7DUrOAmIWTZO2AQSVNR',
        'connection_timeout_seconds': 15,
    })

client = get_typesense_client()