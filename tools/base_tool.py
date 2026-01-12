from abc import ABC, abstractmethod
from aiogram import Router

class BaseTool(ABC):
    """
    Базовый класс для всех инструментов (плагинов).
    Каждый инструмент должен наследоваться от этого класса.
    """
    
    def __init__(self):
        # У каждого инструмента может быть свой роутер для хендлеров
        self.router = Router()

    @property
    @abstractmethod
    def name(self) -> str:
        """Уникальное имя инструмента"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Краткое описание того, что делает инструмент"""
        pass

    @abstractmethod
    def register_handlers(self):
        """
        Метод, где мы регистрируем хендлеры (команды, сообщения) 
        в self.router.
        """
        pass
