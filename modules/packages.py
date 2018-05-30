from hashlib import sha1
from modules.types import *

class MYSQL_PACKAGE:
    """Data between client and server is exchanged in packages of max 16MByte size."""  

    def __init__(self, resp = b''):
        self.resp = resp
        self.start = 0
        self.end = 0

        self.client_capabilities = {
            "Long Password": True,
            "Found Rows": False,
            "Long Column Flags": True,
            "Connect With Database": False,
            "Don't Allow database.table.column": False,
            "Can use compression protocol": False,
            "ODBC Client": False,
            "Can Use LOAD DATA LOCAL": False,
            "Ignore Spaces before '('": False,
            "Speaks 4.1 protocol (new flag)": True,
            "Interactive Client": True,
            "Switch to SSL after handshake": False,
            "Ignore sigpipes": False,
            "Knows about transactions": True,
            "Speaks 4.1 protocol (old flag)": False,
            "Can do 4.1 authentication": True
        }

        self.extended_client_capabilities = {
            "Multiple statements": True,
            "Multiple results": True,
            "PS Multiple results": True,
            "Plugin Auth": True,
            "Connect attrs": False,
            "Plugin Auth LENENC Client Data": False,
            "Client can handle expired passwords": False,
            "Session variable tracking": False,
            "Deprecate EOF": False,
            "unused1": False,
            "unused2": False,
            "unused3": False,
            "unused4": False,
            "unused5": False,
            "unused6": False,
            "unused7": False,
        }

        self.charsets = {
            1: "big5_chinese_ci", 
            2: "latin2_czech_cs", 
            3: "dec8_swedish_ci", 
            4: "cp850_general_ci",
            5: "latin1_german1_ci",
            6: "hp8_english_ci",
            7: "koi8r_general_ci",
            8: "latin1_swedish_ci",
            9: "latin2_general_ci",
            10: "swe7_swedish_ci",
            33: "utf8_general_ci",
            63: "binary"
        }

        self.commands = {
            "COM_SLEEP": 0x00,
            "COM_QUIT": 0x01,
            "COM_INIT_DB": 0x02,
            "COM_QUERY": 0x03,
        }

    def next(self, length = None, type=int, byteorder='little', signed=False, freeze=False):
        if not freeze:
            if length:
                self.end += length
                portion = self.resp[self.start:self.end]
                self.start = self.end
            else:
                portion = self.resp[self.start:]
                self.start = self.end = 0
        else:
            if length:
                portion = self.resp[self.start:self.start + length]
            else:
                portion = self.resp[self.start:]

        if type is int:
            return int.from_bytes(portion, byteorder=byteorder, signed=signed)
        elif type is str:
            return portion.decode('utf-8')
        elif type is hex:
            return portion.hex()
        else:
            return portion

    def get_server_capabilities(self, resp):
        """
        See: https://dev.mysql.com/doc/internals/en/capability-flags.html#package-Protocol::CapabilityFlags
        """
        return {
            "Long Password": resp&1 != 0,
            "Found Rows": resp&2 != 0,
            "Long Column Flags": resp&3 != 0,
            "Connect With Database": resp&4 != 0,
            "Don't Allow database.table.column": resp&5 != 0,
            "Can use compression protocol": resp&6 != 0,
            "ODBC Client": resp&7 != 0,
            "Can Use LOAD DATA LOCAL": resp&8 != 0,
            "Ignore Spaces before '('": resp&9 != 0,
            "Speaks 4.1 protocol (new flag)": resp&10 != 0,
            "Interactive Client": resp&11 != 0,
            "Switch to SSL after handshake": resp&12 != 0,
            "Ignore sigpipes": resp&13 != 0,
            "Knows about transactions": resp&14 != 0,
            "Speaks 4.1 protocol (old flag)": resp&15 != 0,
            "Can do 4.1 authentication": resp&16 != 0
        }

    def get_character_set(self, resp):
        """
            See: https://dev.mysql.com/doc/internals/en/character-set.html
        """
        if resp in self.charsets:
            return self.charsets[resp]
    
    def get_server_status(self, resp):
        """
        See: https://dev.mysql.com/doc/internals/en/status-flags.html#package-Protocol::StatusFlags
        """
        return {
            "SERVER_STATUS_IN_TRANS": resp&1 != 0, # transaction is active
            "SERVER_STATUS_AUTOCOMMIT": resp&2 != 0, # auto commit
            "SERVER_MORE_RESULTS_EXISTS": resp&3 != 0, # more results
            "Multi query - more resultsets": resp&4 != 0,
            "SERVER_STATUS_NO_GOOD_INDEX_USED": resp&5 != 0, # Bad index used
            "SERVER_STATUS_NO_INDEX_USED": resp&6 != 0, # No index used
            "SERVER_STATUS_CURSOR_EXISTS": resp&7 != 0, # Cursor exists
            "SERVER_STATUS_LAST_ROW_SENT": resp&8 != 0, # Last row sent
            "SERVER_STATUS_DB_DROPPED": resp&9 != 0, # database dropped
            "SERVER_STATUS_NO_BACKSLASH_ESCAPES": resp&10 != 0, # No backslash escapes
            "SERVER_SESSION_STATE_CHANGED": resp&11 != 0, # Session state changed
            "SERVER_QUERY_WAS_SLOW": resp&12 != 0, # Query was slow
            "SERVER_PS_OUT_PARAMS": resp&13 != 0, # PS Out Params
        }

    def get_server_extended_capabilities(self, resp):
        """
        See: https://dev.mysql.com/doc/internals/en/capability-flags.html#package-Protocol::CapabilityFlags
        """

        return {
            "Multiple statements": resp&1 != 0,
            "Multiple results": resp&1 != 0,
            "PS Multiple results": resp&1 != 0,
            "Plugin Auth": resp&1 != 0,
            "Connect attrs": resp&1 != 0,
            "Plugin Auth LENENC Client Data": resp&1 != 0,
            "Client can handle expired passwords": resp&1 != 0,
            "Session variable tracking": resp&1 != 0,
            "Deprecate EOF": resp&1 != 0,
        }
    
    def encrypt_password(self, salt, password):
        bytes1 = sha1(password.encode("utf-8")).digest()
        concat1 = salt.encode('utf-8')
        concat2 = sha1(sha1(password.encode("utf-8")).digest()).digest()
        bytes2 = bytearray()
        bytes2.extend(concat1)
        bytes2.extend(concat2)
        bytes2 = sha1(bytes2).digest()
        hash = bytearray(x ^ y for x, y in zip(bytes1, bytes2))
        return hash
    
    def capabilities_2_bytes(self, capabilities):
        capabilities = ''.join(str(int(x)) for x in capabilities.values())[::-1]
        capabilities = int(capabilities, 2).to_bytes(2, byteorder='little')
        return capabilities

class LOGIN_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, handshake):
        super().__init__()
        self.handshake_info = handshake.parse()
    
    def create_package(self, user, password, package_number):
        package = bytearray()
        # client capabilities
        package.extend(self.capabilities_2_bytes(self.client_capabilities))
        # extended client capabilities
        package.extend(self.capabilities_2_bytes(self.extended_client_capabilities))
        # max package -> 16777216
        max_package = (16777216).to_bytes(4, byteorder='little')
        package.extend(max_package)
        # charset -> 33 (utf8_general_ci)
        package.append(33)
        # 23 bytes are reserved
        reserved = (0).to_bytes(23, byteorder='little')
        package.extend(reserved)
        # username (null byte end)
        package.extend(user.encode('utf-8'))
        package.append(0)
        # password
        salt = self.handshake_info['salt1'] + self.handshake_info['salt2']
        encrypted_password = self.encrypt_password(salt.strip(), password)
        length = len(encrypted_password)
        package.append(length)
        package.extend(encrypted_password)
        # authentication plugin
        plugin = self.handshake_info['authentication_plugin'].encode('utf-8')
        package.extend(plugin)

        finpack = bytearray()
        package_length = len(package)
        
        finpack.append(package_length)
        finpack.extend((0).to_bytes(2, byteorder='little'))
        finpack.append(package_number)
        finpack.extend(package)

        return finpack

class HANDSHAKE_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, resp):
        super().__init__(resp)
    
    def parse(self):
        return {
            "package_name": "HANDSHAKE_PACKAGE",
            "package_length": Int(self, 3).next(), #self.next(3),
            "package_number": Int(self, 1).next(), #self.next(1),
            "protocol": Int(self, 1).next(), #self.next(1),
            "server_version": Str(self, type='null').next(),
            "connection_id": Int(self, 4).next(), #self.next(4),
            "salt1": Str(self, type='null').next(),
            "server_capabilities": self.get_server_capabilities(Int(self, 2).next()),
            "server_language": self.get_character_set(Int(self, 1).next()),
            "server_status": self.get_server_status(Int(self, 2).next()),
            "server_extended_capabilities": self.get_server_extended_capabilities(Int(self, 2).next()),
            "authentication_plugin_length": Int(self, 1).next(),
            "unused": Int(self, 10).next(), #self.next(10, hex),
            "salt2": Str(self, type='null').next(),
            "authentication_plugin": Str(self, type='eof').next()
        }

class OK_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, resp):
        super().__init__(resp)

    def parse(self):
        return {
            "package_name": "OK_PACKAGE",
            "package_length": Int(self, 3).next(), #self.next(3),
            "package_number": Int(self, 1).next(), #self.next(1),
            "header": hex(Int(self, 1).next()),
            "affected_rows": Int(self, 1).next(), #self.next(1),
            "last_insert_id": Int(self, 1).next(), #self.next(1),
            "server_status": self.get_server_status(Int(self, 2).next()),
            "warnings": Int(self, 2).next()
        }


class ERR_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, resp):
        super().__init__(resp)

    def parse(self):
        return {
            "package_name": "ERR_PACKAGE",
            "package_length": Int(self, 3).next(), #self.next(3),
            "package_number": Int(self, 1).next(), #self.next(1),
            "header": hex(Int(self, 1).next()), #self.next(1, hex),
            "error_code": Int(self, 2).next(), #self.next(2),
            "sql_state": Str(self, 6).next(),
            "error_message": Str(self, type='eof').next()
        }


class EOF_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, resp):
        super().__init__(resp)

    def parse(self):
        return {
            "package_name": "EOF_PACKAGE",
            "package_length": Int(self, 3).next(),
            "package_number": Int(self, 1).next(),
            "header": hex(Int(self, 1).next()),
            "auth_method_name": Str(self, type='eof').next()
        }


class INIT_DB_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, db):
        super().__init__()
        self.db = db
    
    def create_package(self):
        package = bytearray()
        package.append(self.commands['COM_INIT_DB'])
        package.extend(self.db.encode("utf-8"))
        package_length = len(package)
        package_number = 0
        finpack = bytearray()
        finpack.append(package_length)
        finpack.extend((0).to_bytes(2, byteorder='little'))
        finpack.append(package_number)
        finpack.extend(package)
        return finpack

class QUERY_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, sql):
        super().__init__()
        self.sql = sql
    
    def create_package(self):
        package = bytearray()
        package.append(self.commands['COM_QUERY'])
        package.extend(self.sql.encode("utf-8"))
        package_length = len(package)
        package_number = 0
        finpack = bytearray()
        finpack.append(package_length)
        finpack.extend((0).to_bytes(2, byteorder='little'))
        finpack.append(package_number)
        finpack.extend(package)
        return finpack


class QUERY_RESPONSE_PACKAGE(MYSQL_PACKAGE):
    def __init__(self, resp):
        super().__init__(resp)

    def parse(self):
        package_length = Int(self, 3).next()
        package_number = Int(self, 1).next()
        field_number = Int(self, 1).next()

        ret = {
            "package_name": "QUERY_RESPONSE_PACKAGE",
        }

        ret['fields'] = []
        for i in range(field_number):
            ret["fields"].append(self.get_fields())

        skip_first_eof = self.get_eof()
        
        ret['rows'] = []
        while True:
            row = self.get_row(field_number)
            if not row:
                break

            ret['rows'].append(row)

        return ret
    
    def get_eof(self):
        return {
            "package_length": Int(self, 3).next(),
            "package_number": Int(self, 1).next(),
            "eof_marker": hex(Int(self, 1).next()),
            "warnings": Int(self, 2).next(),
            "server_status": self.get_server_status(Int(self, 2).next())
        }
    
    def is_eof(self):
        return self.next(1, freeze=True) == 0xfe
        
    def get_fields(self):
        package_length = Int(self, 3).next()
        package_number = Int(self, 1).next()
        catalog = Str(self, type='lenenc').next()
        database = Str(self, type='lenenc').next()
        table = Str(self, type='lenenc').next()
        original_table = Str(self, type='lenenc').next()
        name = Str(self, type='lenenc').next()
        original_name = Str(self, type='lenenc').next()
        encoding = Int(self, 1).next()
        charset_number = Int(self, 2).next()
        length = Int(self, 4).next()
        field_type = Int(self, 1).next()
        flags = self.get_flags(Int(self, 2).next())
        decimals = Int(self, 3).next()

        return {
            "database": database,
            "table": original_table,
            "name": original_name,
            "length": length,
            "flags": flags,
            "field_type": field_type
        }

    def get_flags(self, flags):
        return {
            "not_null": flags & 1 != 0,
            "primary_key": flags & 2 != 0,
            "unique_key": flags & 3 != 0,
            "multiple_key": flags & 4 != 0,
            "blob": flags & 5 != 0,
            "unsigned": flags & 6 != 0,
            "zero_fill": flags & 7 != 0,
            "binary": flags & 8 != 0,
            "enum": flags & 9 != 0,
            "auto_increment": flags & 10 != 0,
            "timestamp": flags & 11 != 0,
            "set": flags & 12 != 0
        }
    
    def get_row(self, field_number):
        packet_length = Int(self, 3).next()
        packet_number = Int(self, 1).next()
        ret = []

        for i in range(field_number):
            if self.is_eof():
                break

            text = Str(self, type='lenenc').next()
            ret.append(text)
        
        return ret

class SHOW_DATABASES_PACKAGE(QUERY_PACKAGE):
    def __init__(self):
        super().__init__("show databases")
    
    def create_package(self):
        return super().create_package()

    def parse (self, resp):
        ret = {
            "databases": []
        }
        response = QUERY_RESPONSE_PACKAGE(resp)
        response = response.parse()
        ret['databases'] = ({'text': x[0]} for x in response['rows'])
        return ret