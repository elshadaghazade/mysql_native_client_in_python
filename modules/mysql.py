from socket import AF_INET, SOCK_STREAM, socket, gethostbyname
from modules.packages import *

class MySQL: 
    def __init__(self, host="", port="", user="", password=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
    
    def connect(self):
        resp = self.client.recv(65536)
        return HANDSHAKE_PACKAGE(resp)

    def login(self, handshake_package, package_number):
        """Sending Authentication package"""
        login_package = LOGIN_PACKAGE(handshake_package)
        package = login_package.create_package(user=self.user, password=self.password, package_number=package_number)
        self.client.sendall(package)
        resp = self.client.recv(65536)
        package = self.detect_package(resp)
        if isinstance(package, ERR_PACKAGE):
            info = package.parse()
            raise Exception(f"MySQL Server Error: {info['error_code']} - {info['error_message']}")
        elif isinstance(package, OK_PACKAGE):
            return package.parse()['package_number']
        elif isinstance(package, EOF_PACKAGE):
            return False
    
    def init_db(self, db):
        """changing schema"""
        package = INIT_DB_PACKAGE(db).create_package()
        self.client.sendall(package)
        resp = self.client.recv(65536)
        package = self.detect_package(resp)
        
        if isinstance(package, ERR_PACKAGE):
            info = package.parse()
            raise Exception(f"MySQL Server Error: {info['error_code']} - {info['error_message']}")
        elif isinstance(package, OK_PACKAGE):
            return True
        elif isinstance(package, EOF_PACKAGE):
            return False

    def show_databases(self):
        """selecting databases from server"""
        show_databases = SHOW_DATABASES_PACKAGE()
        package = show_databases.create_package()
        self.client.sendall(package)
        resp = self.client.recv(65536)
        resp = show_databases.parse(resp)
        return resp

    def query(self, sql):
        """sending sql query to the server"""
        query_package = QUERY_PACKAGE(sql)
        package = query_package.create_package()
        self.client.sendall(package)
        resp = self.client.recv(65536)
        try:
            package = self.detect_package(resp)
        except Exception as err:
            return {"package_name": "unknown"}
        return package.parse()


    def detect_package(self, resp):
        if resp[4] == 0x00:
            return OK_PACKAGE(resp)
        elif resp[4] == 0xff:
            return ERR_PACKAGE(resp)
        elif resp[4] == 0xfe:
            return EOF_PACKAGE(resp)
        else:
            return QUERY_RESPONSE_PACKAGE(resp)

    def __enter__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        ip = gethostbyname(self.host)
        address=(ip,int(self.port))
        self.client.connect(address)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Good Bye!")
        self.close()

    def close(self):
        self.client.close()
        

