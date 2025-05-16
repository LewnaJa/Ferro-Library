"""
Ferro ORM - Rozszerzenie SQLAlchemy dla integracji z ekosystemem Ferro Framework
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.inspection import inspect
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Callable, Union
import datetime
import json
import os
import re
from pathlib import Path

__version__ = "0.1.0"

# Bazowy model SQLAlchemy
Base = declarative_base()

# Typ generyczny dla modeli
T = TypeVar('T', bound=Base)

class FerroORM:
    """
    Główna klasa konfiguracyjna dla integracji ORM z Ferro Framework
    """
    
    def __init__(self, 
                 connection_string: str,
                 models_dir: str = "models",
                 auto_generate_types: bool = True,
                 echo: bool = False):
        """
        Inicjalizacja FerroORM
        
        Args:
            connection_string: Ciąg połączenia do bazy danych
            models_dir: Katalog z definicjami modeli
            auto_generate_types: Czy automatycznie generować typy TypeScript
            echo: Czy logować zapytania SQL
        """
        self.connection_string = connection_string
        self.models_dir = models_dir
        self.auto_generate_types = auto_generate_types
        self.echo = echo
        self.engine = None
        self.Session = None
        self.registered_models = []
        
        # Automatyczne utworzenie silnika i sesji
        self.setup_database()
    
    def setup_database(self):
        """Konfiguracja silnika bazy danych i sesji"""
        self.engine = create_engine(self.connection_string, echo=self.echo)
        session_factory = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.Session = scoped_session(session_factory)
        
        # Słuchacz zdarzeń dla automatycznego zapisywania daty utworzenia/modyfikacji
        @event.listens_for(Base, 'before_insert', propagate=True)
        def set_created_at(mapper, connection, instance):
            if hasattr(instance, 'created_at') and not instance.created_at:
                instance.created_at = datetime.datetime.utcnow()
            if hasattr(instance, 'updated_at'):
                instance.updated_at = datetime.datetime.utcnow()
        
        @event.listens_for(Base, 'before_update', propagate=True)
        def set_updated_at(mapper, connection, instance):
            if hasattr(instance, 'updated_at'):
                instance.updated_at = datetime.datetime.utcnow()
    
    def create_tables(self):
        """Tworzenie wszystkich zdefiniowanych tabel w bazie danych"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Usuwanie wszystkich tabel z bazy danych"""
        Base.metadata.drop_all(self.engine)
    
    def register_model(self, model: Type[Base]):
        """
        Rejestracja modelu w systemie do automatycznego generowania typów
        
        Args:
            model: Klasa modelu SQLAlchemy do zarejestrowania
        """
        self.registered_models.append(model)
        return model
    
    def generate_typescript_types(self, output_dir: str = None):
        """
        Generowanie plików TypeScript dla zarejestrowanych modeli
        
        Args:
            output_dir: Katalog wyjściowy dla plików TypeScript
        """
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), 'client/src/types/models')
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generowanie interfejsów dla wszystkich modeli
        models_file_path = os.path.join(output_dir, 'models.ts')
        with open(models_file_path, 'w') as f:
            f.write('// Automatycznie wygenerowane typy z Ferro ORM\n\n')
            
            # Generowanie interfejsów dla wszystkich zarejestrowanych modeli
            for model in self.registered_models:
                f.write(self._generate_typescript_interface(model))
            
            # Generowanie typu zbiorczego
            f.write('export type ModelTypes = ')
            f.write(' | '.join([f"'{model.__name__}'" for model in self.registered_models]))
            f.write(';\n\n')
            
            # Generowanie mapowania typów
            f.write('export const ModelMap = {\n')
            for model in self.registered_models:
                f.write(f"  '{model.__name__}': '{model.__name__}',\n")
            f.write('} as const;\n')
    
    def _generate_typescript_interface(self, model: Type[Base]) -> str:
        """
        Generowanie interfejsu TypeScript dla pojedynczego modelu
        
        Args:
            model: Klasa modelu SQLAlchemy
        
        Returns:
            Kod interfejsu TypeScript jako string
        """
        mapper = inspect(model)
        result = f'export interface {model.__name__} {{\n'
        
        # Dodanie pól
        for column in mapper.columns:
            ts_type = self._map_sql_to_ts_type(column.type)
            nullable = '?' if column.nullable else ''
            result += f'  {column.name}{nullable}: {ts_type};\n'
        
        # Dodanie relacji
        for relationship_name, relationship in mapper.relationships.items():
            related_model = relationship.mapper.class_.__name__
            if relationship.uselist:
                result += f'  {relationship_name}?: {related_model}[];\n'
            else:
                result += f'  {relationship_name}?: {related_model};\n'
        
        result += '}\n\n'
        return result
    
    def _map_sql_to_ts_type(self, sql_type) -> str:
        """
        Mapowanie typów SQLAlchemy na typy TypeScript
        
        Args:
            sql_type: Typ SQLAlchemy
        
        Returns:
            Odpowiadający typ TypeScript
        """
        type_name = sql_type.__class__.__name__
        
        # Mapowanie podstawowych typów
        type_map = {
            'Integer': 'number',
            'BigInteger': 'number',
            'SmallInteger': 'number',
            'Float': 'number',
            'Numeric': 'number',
            'String': 'string',
            'Text': 'string',
            'Unicode': 'string',
            'UnicodeText': 'string',
            'Boolean': 'boolean',
            'Date': 'string',
            'DateTime': 'string',
            'Time': 'string',
            'Enum': 'string',
            'JSON': 'any',
            'ARRAY': 'any[]'
        }
        
        return type_map.get(type_name, 'any')

class Repository(Generic[T]):
    """
    Generyczna klasa repozytorium dla operacji CRUD na modelach
    
    Przykład użycia:
        user_repo = Repository(User)
        users = user_repo.find_all()
    """
    
    def __init__(self, model: Type[T], db_session = None):
        """
        Inicjalizacja repozytorium
        
        Args:
            model: Klasa modelu
            db_session: Opcjonalna sesja bazy danych
        """
        self.model = model
        self.session = db_session or FerroORM.Session()
    
    def find_by_id(self, id: int) -> Optional[T]:
        """Pobieranie pojedynczego rekordu po ID"""
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def find_all(self, limit: int = None, offset: int = None) -> List[T]:
        """Pobieranie wszystkich rekordów z opcjonalnym limitem i offsetem"""
        query = self.session.query(self.model)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def find_by(self, **kwargs) -> List[T]:
        """Pobieranie rekordów spełniających warunki"""
        return self.session.query(self.model).filter_by(**kwargs).all()
    
    def find_one_by(self, **kwargs) -> Optional[T]:
        """Pobieranie pierwszego rekordu spełniającego warunki"""
        return self.session.query(self.model).filter_by(**kwargs).first()
    
    def create(self, **kwargs) -> T:
        """Tworzenie nowego rekordu"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Aktualizacja istniejącego rekordu"""
        instance = self.find_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.session.commit()
        return instance
    
    def delete(self, id: int) -> bool:
        """Usuwanie rekordu po ID"""
        instance = self.find_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
    
    def count(self, **kwargs) -> int:
        """Liczenie rekordów spełniających warunki"""
        return self.session.query(self.model).filter_by(**kwargs).count()

# Model bazowy z wspólnymi polami
class BaseModel(Base):
    """
    Model bazowy zawierający wspólne pola dla wszystkich modeli
    
    Ta klasa jest abstrakcyjna i powinna być używana jako klasa bazowa dla innych modeli.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja modelu do słownika"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Konwersja typów datetime na ISO string
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result
    
    def to_json(self) -> str:
        """Konwersja modelu do JSON"""
        return json.dumps(self.to_dict()) 