import os
import importlib
import inspect
from aiogram import Dispatcher
from .base_tool import BaseTool

def register_all_tools(dp: Dispatcher):
    """
    Автоматически находит и регистрирует все инструменты в папке tools
    """
    tools_dir = os.path.dirname(__file__)
    
    print(f"[*] Ищем инструменты в {tools_dir}...")
    
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "base_tool.py":
            module_name = filename[:-3]
            full_module_name = f"tools.{module_name}"
            
            try:
                # Импортируем модуль динамически
                module = importlib.import_module(full_module_name)
                
                # Ищем классы, наследуемые от BaseTool
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj is not BaseTool:
                        # Создаем экземпляр инструмента
                        tool_instance = obj()
                        tool_instance.register_handlers()
                        
                        # Подключаем роутер инструмента к главному диспетчеру
                        dp.include_router(tool_instance.router)
                        
                        print(f"    [+] Загружен инструмент: {tool_instance.name} ({tool_instance.description})")
            except Exception as e:
                print(f"    [!] Ошибка загрузки {filename}: {e}")
