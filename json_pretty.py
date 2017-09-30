sp='    '

class Token:
    def __init__(self,type,value=None):
        self.type=type
        self.value=value

    def __str__(self):
        return self.type+':'+ str(self.value)

class Lexer:
    def __init__(self,text):
        self.text=text
        self.pos=0
        self.char=text[0]

    def advance(self):
        self.pos+=1
        if self.pos < len(self.text):
            self.char=self.text[self.pos]
        else:
            self.char=None

    def peek(self):
        pos=self.pos+1
        if pos < len(self.text):
            return self.text[pos]
        else:
            return None

    def id(self):
        result=''
        while self.char.isalnum() or self.char=='_' or self.char=='`' or self.char=='.':
            result+=self.char
            self.advance()
        result=result.lower()
        return Token('id',result)

    def skip_space(self):
        while self.char is not None and self.char.isspace():
            self.advance()
        return self.get_next_token()

    def string(self):
        result=''
        self.advance()
        while self.char is not None:
            if self.char=='\\' and self.peek()=='"':
                self.advance()
                self.advance()
                result+='"'
            elif self.char=='"':
                self.advance()
                break
            else:
                result+=self.char
                self.advance()
        return Token('string',result)

    def digit(self):
        result=''
        while self.char is not None and self.char.isdigit():
            result+=self.char
            self.advance()
        if self.char!='.':
            return Token('int',int(result))

        result+='.'
        self.advance()
        while self.char is not None and self.char.isdigit():
            result+=self.char
            self.advance()

        return Token('float',float(result))

    def get_next_token(self):
        if self.char is None:
            return Token('eof')

        if self.char.isspace():
            return self.skip_space()

        if self.char.isdigit():
            return self.digit()

        if self.char=='"':
            return self.string()

        if self.char.isalnum():
            return self.id()

        if self.char==',':
            self.advance()
            return Token(',')

        if self.char==':':
            self.advance()
            return Token(':')

        if self.char=='{':
            self.advance()
            return Token('{')

        if self.char=='}':
            self.advance()
            return Token('}')

        if self.char=='[':
            self.advance()
            return Token('[')

        if self.char==']':
            self.advance()
            return Token(']')

        raise Exception(self.char+' undefined')

class JArray:
    def __init__(self,arr):
        self.arr=arr

    def visit(self,dep=0):
        if len(self.arr)==0:
            return "[]"

        ret='[\n'
        for k,v in enumerate(self.arr):
            ret+=sp*(dep+1)
            ret+=v.visit(dep+1)
            if k < len(self.arr)-1:
                ret+=',\n'
        ret+='\n'
        ret+=sp*dep
        ret+=']'
        return ret

    def __str__(self):
        return "[ {arr} ]".format(
            arr=[str(item) for item in self.arr]
        )

class KeyValuePair:
    def __init__(self,key,value):
        self.key=key
        self.value=value

    def visit(self,dep=0):
        return "\"{key}\" : {value}".format(
            key=self.key,
            value=self.value.visit(dep)
        )

    def __str__(self):
        return "{key} : {value}".format(
            key=self.key,
            value=str(self.value)
        )

class JObject:
    def __init__(self,list):
        self.list=list

    def visit(self,dep=0):
        if len(self.list)==0:
            return "{}"

        ret='{\n'
        for k,v in enumerate(self.list):
            ret+= sp*(dep+1)
            ret+=v.visit(dep+1)
            if k < len(self.list)-1:
                ret+=',\n'

        ret+='\n'
        ret+=sp*dep
        ret+='}'
        return ret

    def __str__(self):
        return "{{ {arr} }}".format(
            arr=[str(item) for item in self.list]
        )

class Jid:
    def __init__(self,id,type=None):
        self.id=id
        self.type=type

    def visit(self,dep=0):
        return self.__str__()

    def __str__(self):
        if self.type=='string':
            ret=self.id.replace('"',r'\"')
            return "\""+ret+"\""
        return str(self.id)

class Parser:
    def __init__(self,lexer):
        self.lexer=lexer
        self.token=lexer.get_next_token()

    def eat(self,type):
        if self.token.type==type:
            self.token=self.lexer.get_next_token()
        else:
            raise Exception(type+' -> '+str(self.token))
 
    def json(self):
        if self.token.type=='{':
            return self.object()
        elif self.token.type=='[':
            return self.array()
        elif self.token.type in ('id','string','int','float'):
            token=self.token
            self.eat(self.token.type)
            return Jid(token.value,token.type)
        return None

    def object(self):
        self.eat('{')
        arr=[]
        while self.token.type!='eof':
            if self.token.type not in ('string','int','float','id'):
                break
            key=self.token.value
            self.eat(self.token.type)
            self.eat(':')
            value=self.json()

            arr.append(KeyValuePair(key,value))

            if self.token.type!=',':
                break
            self.eat(',')

        self.eat('}')
        return JObject(arr)

    def array(self):
        self.eat('[')
        arr=[]
        while self.token.type!='eof':
            item=self.json()
            if item==None:
                break
            arr.append(item)

            if self.token.type!=',':
                break
            self.eat(',')

        self.eat(']')
        return JArray(arr)


def json_pretty(json):
    lexer = Lexer(json)
    parser = Parser(lexer)
    json = parser.json()
    if parser.token.type!='eof':
        raise Exception('json syntax error')
    return json.visit()