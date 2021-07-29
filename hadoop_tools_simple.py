from impala.dbapi import connect
from impala.util import as_pandas

def connect_to_impala(host='mgmt0.hadoop.trivago.com', port=21050,
                      auth_mechanism='GSSAPI', user=None, password=None):
    """ Connect to the Impala cluster """
    return connect(host=host, port=port, auth_mechanism=auth_mechanism,
                   user=user, password=password)


def connect_to_hive(host='mgmt1.hadoop.trivago.com', port=10000,
                    auth_mechanism='GSSAPI', kerberos_service_name='hive'):
    """ Connect to Hive with kerberos authentification """
    return connect(host=host, port=port,
                   auth_mechanism=auth_mechanism,
                   kerberos_service_name=kerberos_service_name)


def exec_query(conn, query, verbose=True):
    query = [string for string in query.split(';')
             if string != '\n']

    with conn.cursor() as cursor:
        for subquery in query:
            if verbose:
                print(subquery)
            cursor.execute(subquery)
            try:
                df = clean_col_headers(as_pandas(cursor))
            except:
                df = None
    return df


def read_query(path_to_file):
    with open(path_to_file) as fd:
        query = fd.read()
    return query


def clean_col_headers(df):
    df.columns = [col.split('.')[-1] for col in df.columns]
    return df


def query_hive(query, verbose=False):
    conn = connect_to_hive()
    df_result = exec_query(conn, query, verbose)
    conn.close()
    return  df_result


def query_impala(query, verbose=False):    
    conn = connect_to_impala()
    df_result = exec_query(conn, query, verbose)
    conn.close()
    return  df_result
