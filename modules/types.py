class Int:
    """see documentation: https://dev.mysql.com/doc/internals/en/integer.html"""

    def __init__(self, package, length=-1, type='fix'):
        self.package = package
        self.length = length
        self.type = type
            

    def next(self):
        # int<n>
        if self.type == 'fix' and self.length > 0:
            return self.package.next(self.length)
        # int<lenenc>
        if self.type == 'lenenc':
            byte = self.package.next(1)
            if byte < 0xfb:
                return self.package.next(1)
            elif byte == 0xfc:
                return self.package.next(2)
            elif byte == 0xfd:
                return self.package.next(3)
            elif byte == 0xfe:
                return self.package.next(8)


class Str:
    """see documentation: https://dev.mysql.com/doc/internals/en/string.html"""
    def __init__(self, package, length = -1, type="fix"):
        self.package = package
        self.length = length
        self.type = type

    def next(self):
        # string<fix>
        if self.type == 'fix' and self.length > 0:
            return self.package.next(self.length, str)
        # string<lenenc>
        elif self.type == 'lenenc':
            length = self.package.next(1)
            if length == 0x00:
                return ""
            elif length == 0xfb:
                return "NULL"
            elif length == 0xff:
                return "undefined"
            return self.package.next(length, str)
        # string<var>
        elif self.type == 'var':
            length = Int(self.package, type='lenenc').next()
            return self.package.next(length, str)
        # string<eof>
        elif self.type == 'eof':
            return self.package.next(type=str)
        # string<null> - null terminated strings
        elif self.type == 'null':
            strbytes = bytearray()

            byte = self.package.next(1)
            while True:
                if byte == 0x00:
                    break
                else:
                    strbytes.append(byte)
                    byte = self.package.next(1)
            
            return strbytes.decode('utf-8')

        
    