from dotenv import load_dotenv
import os

load_dotenv()

ddb_host = os.getenv('DDB_HOST')
ddb_port = os.getenv('DDB_PORT')

try:
    ddb_port = int(ddb_port)
except ValueError:
    print('.env文件中DDB_PORT配置错误！必须是数字！例如8848')

ddb_user = os.getenv('DDB_USER')
ddb_password = os.getenv('DDB_PASSWORD')

proxy_key = os.getenv('PROXY_KEY')
proxy_url = os.getenv('PROXY_API_URL')
proxy_number_param = os.getenv('PROXY_API_NUM_PARAM')
