from pg import DB

def createConn(config):
    return DB(dbname = config['dbname'],
              host   = config['host'],
              port   = config['port'],
              user   = config['user'],
              passwd = config['password'])
