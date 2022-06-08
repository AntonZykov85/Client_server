import dis


class ServerVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        print(methods)
        if 'connect' in methods:
            raise TypeError('Usung "connect" method invalid in server_module class')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Incorrect socket initialization.')
        super().__init__(clsname, bases, clsdict)

class ClientVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('The use of a forbidden method was detected in a class')
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('There are no socket function calls')
        super().__init__(clsname, bases, clsdict)

