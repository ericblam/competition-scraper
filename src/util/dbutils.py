import psycopg2

def createConnFromConfig(config):
    if 'db' not in config:
        raise RuntimeError('db config missing from configuration')

    dbconfig = config['db']
    conn = psycopg2.connect(
        dbname = dbconfig['dbname'],
        host   = dbconfig['host'],
        port   = dbconfig['port'],
        user   = dbconfig['user'],
        password = dbconfig['password'])

    return conn


