import dis

class ClientVerifer(type):
    def __init__(self, class_name, bases, class_dict):
        methods = []
        for functions in class_dict:
            try:
                ret = dis.get_instructions(class_dict[functions])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('the use of a forbidden method was detected in the class')
        if 'get_message' or 'send_message' in methods:
            pass
        else:
            raise TypeError('missing socket function calls')
        super().__init__(class_name, bases, class_dict)

class ServerVerifier(type):
    def __init__(self, class_name, bases, class_dict):
        methods = []
        arguments = []
        for functions in class_dict:
            try:
                ret = dis.get_instructions(class_dict[functions])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in arguments:
                            arguments.append(i.argval)
        print(methods)
        if 'connect' in methods:
            raise TypeError('Using the connect method is not allowed in a server class')
        if not ('SOCK_STREAM' in arguments and 'AF_INET' in arguments):
            raise TypeError('Incorrect socket initialization')
        super().__init__(class_name, bases, class_dict)

