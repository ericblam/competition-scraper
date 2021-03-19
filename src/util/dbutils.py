from pg import DB

def createConnFromConfig(config):
    if 'db' not in config:
        raise RuntimeError('db config missing from configuration')

    dbconfig = config['db']

    return DB(dbname = dbconfig['dbname'],
              host   = dbconfig['host'],
              port   = dbconfig['port'],
              user   = dbconfig['user'],
              passwd = dbconfig['password'])
