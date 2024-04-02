class ParamsError(Exception):
    """自定义参数错误异常类"""

    def __init__(self, message="参数错误"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"
