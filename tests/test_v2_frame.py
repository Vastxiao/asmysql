

class Engine:
    def __repr__(self):
        return f"<{self.__class__.__name__} 这是引擎>"

    def use(self, cls):
        return cls()



class AsMysql:
    def __repr__(self):
        return f"<{self.__class__.__name__} 这是业务逻辑类>"


engine = Engine()


# 从引擎实现逻辑类
mysq_exec_asmysql = engine.use(AsMysql)
