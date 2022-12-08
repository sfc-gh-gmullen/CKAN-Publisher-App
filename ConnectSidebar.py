import streamlit as st
import json
from snowflake.snowpark import Session
from snowflake.snowpark import DataFrame as sdf
import pandas as pd

try:
    #attempt file based credentials
    with open('creds.json') as f:
        data = json.load(f)
        username = data['username']
        password = data['password']
        account = data["account"]
except:
    print('nothing to do.')

def getContext():
    if 'connection_parameters' in st.session_state:
        CONNECTION_PARAMETERS = st.session_state.connection_parameters
    else:
        CONNECTION_PARAMETERS = {
        'account': txtAccountLocator,
        'user': txtUserName,
        'password': txtPassword,
        'loginTimeout': 10
        }
    session = Session.builder.configs(CONNECTION_PARAMETERS).create()
    currentwh = session.sql('select current_warehouse()').collect()
    if currentwh[0][0] is None: #need a warehouse to check for roles assigned to the user
        fullroles = session.sql('SHOW ROLES').collect()
        roles = list()
        for row in fullroles:
            roles.append(row[1])
    else: #get all the roles in Snowflake
        roles = session.sql('select value::STRING ROLE from table(flatten(input => parse_json(current_available_roles())))').to_pandas()
        
    whs = session.sql('SHOW WAREHOUSES').collect()
    fulldbs = session.sql('SHOW DATABASES').collect()
    dbs = list()
    for db in fulldbs:
        dbs.append(db[1])
    
    schemas = session.sql('SHOW SCHEMAS').collect()
    st.session_state.roles = roles
    st.session_state.whs = whs
    st.session_state.dbs = dbs
    st.session_state.schemas = schemas
    st.session_state.filteredSchemas = schemas
    
    session.close()

def getListValues(key):
    if key not in st.session_state:
        return []
    else:
        return st.session_state[key]

def filterSchema():
    if txtDatabase:
        lstSchemas= getListValues('schemas')
        ret = list()
        for row in lstSchemas:
            if row[4] == txtDatabase:
                ret.append(row[1])
        return ret
    else:
        return []
def setContext():
    CONNECTION_PARAMETERS = {
    'account': txtAccountLocator,
    'user': txtUserName,
    'password': txtPassword,
    'schema': txtSchema,
    'database': txtDatabase,
    'warehouse': txtWarehouse,
    'role': ddlRoles
    }
    st.session_state.connection_parameters = CONNECTION_PARAMETERS
    
txtAccountLocator = st.sidebar.text_input('Account Locator',key='txtAccountLocator', value=account)
txtUserName = st.sidebar.text_input('User Name', value=username)
txtPassword = st.sidebar.text_input('Password', type="password", value=password)
btnConnect = st.sidebar.button('Get Context', on_click=getContext,type='secondary')
st.sidebar.info('Roles displayed will depend on whether a warehouse was selected. Select a WH and Get Context again for a filtered list of roles.')
ddlRoles = st.sidebar.selectbox('Roles', options=getListValues('roles'))
txtWarehouse = st.sidebar.selectbox('Warehouse', options=getListValues('whs'))
txtDatabase = st.sidebar.selectbox('Database', options=getListValues('dbs'))
txtSchema = st.sidebar.selectbox('Schema', options=filterSchema())
btnSet = st.sidebar.button('Set Context', on_click=setContext, type='primary')