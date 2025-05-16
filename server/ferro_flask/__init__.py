"""
Ferro Flask - moduł integracyjny dla Flask w ekosystemie Ferro Framework
"""

from flask import Flask
from typing import Callable, Dict, Any, Optional, Type, List, Union
import json
import os
import inspect
from functools import wraps
from dataclasses import is_dataclass, asdict
import enum

__version__ = "0.1.0"

class FerroFlask:
    """
    Główna klasa opakowująca Flask do integracji z ekosystemem Ferro
    """
    
    def __init__(self, app: Optional[Flask] = None, 
                 auto_generate_types: bool = True,
                 cors_origin: Optional[str] = None,
                 enable_websockets: bool = False):
        self.endpoints = []
        self.models = []
        self.app = app
        self.auto_generate_types = auto_generate_types
        self.cors_origin = cors_origin
        self.enable_websockets = enable_websockets
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicjalizacja aplikacji Flask z rozszerzeniami Ferro"""
        self.app = app
        
        # Konfiguracja CORS jeśli wymagane
        if self.cors_origin:
            from flask_cors import CORS
            CORS(app, resources={r"/api/*": {"origins": self.cors_origin}})
        
        # Konfiguracja WebSocket jeśli wymagane
        if self.enable_websockets:
            from flask_socketio import SocketIO
            self.socketio = SocketIO(app, cors_allowed_origins=self.cors_origin or "*")
        
        # Dodanie middleware do obsługi błędów
        app.errorhandler(Exception)(self._handle_error)
        
        # Dodanie endpoint'u z metadanymi API dla frontendu
        @app.route('/_ferro/api-metadata')
        def api_metadata():
            return json.dumps({
                'endpoints': self.endpoints,
                'models': self.models
            })
    
    def _handle_error(self, error):
        """Domyślny handler błędów w formacie JSON"""
        response = {
            "error": str(error),
            "type": error.__class__.__name__
        }
        return json.dumps(response), 500
    
    def endpoint(self, route: str, methods: List[str] = None, auth_required: bool = False):
        """
        Dekorator do rejestracji endpointów API z metadanymi
        
        Args:
            route: Ścieżka endpointu
            methods: Lista dozwolonych metod HTTP
            auth_required: Czy endpoint wymaga uwierzytelnienia
        """
        methods = methods or ["GET"]
        
        def decorator(func: Callable):
            # Zbieranie metadanych o funkcji
            sig = inspect.signature(func)
            return_type = sig.return_annotation
            params = {
                name: {
                    "type": param.annotation.__name__ 
                           if hasattr(param.annotation, "__name__") 
                           else str(param.annotation),
                    "default": None if param.default is inspect.Parameter.empty else param.default
                }
                for name, param in sig.parameters.items()
                if name != 'self'
            }
            
            endpoint_meta = {
                "route": route,
                "methods": methods,
                "params": params,
                "return_type": return_type.__name__ if hasattr(return_type, "__name__") else str(return_type),
                "auth_required": auth_required,
                "name": func.__name__,
                "doc": func.__doc__
            }
            
            self.endpoints.append(endpoint_meta)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Tutaj można dodać logikę uwierzytelniania
                if auth_required:
                    # Implementacja sprawdzania uwierzytelnienia
                    pass
                
                result = func(*args, **kwargs)
                
                # Konwersja obiektów dataclass na słowniki
                if is_dataclass(result) and not isinstance(result, type):
                    return json.dumps(asdict(result))
                
                # Obsługa typów wyliczeniowych
                if isinstance(result, enum.Enum):
                    return json.dumps(result.value)
                
                # Standardowa serializacja JSON
                return json.dumps(result)
            
            # Rejestracja endpointu w aplikacji Flask
            if self.app:
                self.app.route(route, methods=methods)(wrapper)
            
            return wrapper
        
        return decorator
    
    def register_model(self, model: Type):
        """
        Rejestracja modelu ORM do automatycznego generowania typów
        
        Args:
            model: Klasa modelu SQLAlchemy
        """
        model_meta = {
            "name": model.__name__,
            "fields": {},
            "relationships": {}
        }
        
        # Zbieranie informacji o polach modelu
        if hasattr(model, "__table__"):
            for column in model.__table__.columns:
                model_meta["fields"][column.name] = {
                    "type": str(column.type),
                    "nullable": column.nullable,
                    "primary_key": column.primary_key
                }
        
        # Zbieranie informacji o relacjach
        if hasattr(model, "__mapper__"):
            for relationship in model.__mapper__.relationships:
                model_meta["relationships"][relationship.key] = {
                    "target": relationship.target.name,
                    "type": "one_to_many" if relationship.uselist else "many_to_one"
                }
        
        self.models.append(model_meta)
        return model
    
    def generate_typescript_types(self, output_path: str = None):
        """
        Generowanie plików TypeScript z interfejsami na podstawie zarejestrowanych modeli i endpointów
        
        Args:
            output_path: Ścieżka do zapisania wygenerowanych plików
        """
        if not output_path:
            output_path = os.path.join(os.getcwd(), 'client/src/types/api.ts')
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generowanie interfejsów TypeScript dla modeli
        with open(output_path, 'w') as f:
            f.write('// Automatycznie wygenerowane typy z Ferro Framework\n\n')
            
            # Generowanie typów dla modeli
            for model in self.models:
                f.write(f'export interface {model["name"]} {{\n')
                for field_name, field_info in model["fields"].items():
                    ts_type = self._map_sql_to_ts_type(field_info["type"])
                    nullable = "?" if field_info["nullable"] else ""
                    f.write(f'  {field_name}{nullable}: {ts_type};\n')
                f.write('}\n\n')
            
            # Generowanie typów dla endpointów API
            f.write('export interface ApiEndpoints {\n')
            for endpoint in self.endpoints:
                params_list = []
                for param_name, param_info in endpoint.get("params", {}).items():
                    ts_type = self._map_python_to_ts_type(param_info["type"])
                    params_list.append(f'{param_name}: {ts_type}')
                
                return_type = self._map_python_to_ts_type(endpoint["return_type"])
                f.write(f'  {endpoint["name"]}: ({", ".join(params_list)}) => Promise<{return_type}>;\n')
            f.write('}\n')
    
    def _map_sql_to_ts_type(self, sql_type: str) -> str:
        """Mapowanie typów SQL na typy TypeScript"""
        type_map = {
            'INTEGER': 'number',
            'BIGINT': 'number',
            'FLOAT': 'number',
            'NUMERIC': 'number',
            'DECIMAL': 'number',
            'VARCHAR': 'string',
            'TEXT': 'string',
            'BOOLEAN': 'boolean',
            'DATETIME': 'Date',
            'DATE': 'Date',
            'JSON': 'any'
        }
        
        for sql, ts in type_map.items():
            if sql in sql_type:
                return ts
        
        return 'any'
    
    def _map_python_to_ts_type(self, python_type: str) -> str:
        """Mapowanie typów Python na typy TypeScript"""
        type_map = {
            'str': 'string',
            'int': 'number',
            'float': 'number',
            'bool': 'boolean',
            'list': 'any[]',
            'dict': 'Record<string, any>',
            'None': 'void',
            'NoneType': 'void',
            'Any': 'any'
        }
        
        # Obsługa typów generycznych jak List[str]
        if 'list[' in python_type.lower():
            # Wyodrębnienie typu wewnętrznego
            inner_type = python_type.lower().split('list[')[1].split(']')[0]
            ts_inner_type = self._map_python_to_ts_type(inner_type)
            return f'Array<{ts_inner_type}>'
        
        # Obsługa typów generycznych jak Dict[str, Any]
        if 'dict[' in python_type.lower():
            # Uproszczone mapowanie na Record<string, any>
            return 'Record<string, any>'
        
        return type_map.get(python_type, python_type) 