#!/usr/bin/env python3
"""
Ferro CLI - Narzędzie wiersza poleceń dla Ferro Framework

To narzędzie umożliwia:
- Tworzenie nowych projektów Ferro
- Generowanie komponentów
- Zarządzanie środowiskiem deweloperskim
- Synchronizację typów między backendem i frontendem
"""

import argparse
import os
import sys
import shutil
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple

__version__ = "0.1.0"

# Ścieżki do szablonów
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

class FerroCommand:
    """Klasa bazowa dla wszystkich poleceń Ferro CLI"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Tworzenie parsera argumentów"""
        parser = argparse.ArgumentParser(
            description="Ferro CLI - Narzędzie wiersza poleceń dla Ferro Framework"
        )
        parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
        
        subparsers = parser.add_subparsers(dest='command', help='Dostępne polecenia')
        
        # Komenda: new
        new_parser = subparsers.add_parser('new', help='Utwórz nowy projekt Ferro')
        new_parser.add_argument('name', help='Nazwa projektu')
        new_parser.add_argument('--template', choices=['default', 'blog', 'dashboard', 'e-commerce'], 
                              default='default', help='Szablon projektu')
        new_parser.add_argument('--skip-install', action='store_true', help='Pomiń instalację zależności')
        
        # Komenda: generate
        gen_parser = subparsers.add_parser('generate', help='Generuj komponenty lub modele')
        gen_parser.add_argument('type', choices=['component', 'page', 'model', 'api'], 
                              help='Typ elementu do wygenerowania')
        gen_parser.add_argument('name', help='Nazwa elementu')
        
        # Komenda: dev
        dev_parser = subparsers.add_parser('dev', help='Uruchom serwer deweloperski')
        dev_parser.add_argument('--backend-only', action='store_true', help='Uruchom tylko backend')
        dev_parser.add_argument('--frontend-only', action='store_true', help='Uruchom tylko frontend')
        
        # Komenda: sync-types
        sync_parser = subparsers.add_parser('sync-types', help='Synchronizuj typy między backendem i frontendem')
        sync_parser.add_argument('--watch', action='store_true', help='Monitoruj zmiany i synchronizuj na bieżąco')
        
        # Komenda: build
        build_parser = subparsers.add_parser('build', help='Zbuduj projekt')
        build_parser.add_argument('--backend-only', action='store_true', help='Zbuduj tylko backend')
        build_parser.add_argument('--frontend-only', action='store_true', help='Zbuduj tylko frontend')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Główna metoda do uruchamiania CLI
        
        Args:
            args: Lista argumentów wiersza poleceń (domyślnie sys.argv[1:])
        
        Returns:
            Kod wyjścia (0 = sukces, inne = błąd)
        """
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 0
        
        # Wywołanie odpowiedniej metody na podstawie komendy
        method_name = f'cmd_{parsed_args.command.replace("-", "_")}'
        if hasattr(self, method_name):
            try:
                method = getattr(self, method_name)
                return method(parsed_args)
            except Exception as e:
                print(f"Błąd: {str(e)}")
                return 1
        else:
            print(f"Nieobsługiwana komenda: {parsed_args.command}")
            return 1
    
    def cmd_new(self, args: argparse.Namespace) -> int:
        """
        Tworzenie nowego projektu Ferro
        
        Args:
            args: Sparsowane argumenty
        
        Returns:
            Kod wyjścia
        """
        project_name = args.name
        template_name = args.template
        skip_install = args.skip_install
        
        # Sprawdzenie, czy katalog projektu już istnieje
        if os.path.exists(project_name):
            print(f"Błąd: Katalog '{project_name}' już istnieje.")
            return 1
        
        # Sprawdzenie, czy szablon istnieje
        template_dir = TEMPLATES_DIR / template_name
        if not template_dir.exists():
            print(f"Błąd: Szablon '{template_name}' nie istnieje.")
            return 1
        
        print(f"Tworzenie nowego projektu '{project_name}' na podstawie szablonu '{template_name}'...")
        
        # Kopiowanie szablonu
        shutil.copytree(template_dir, project_name)
        
        # Dostosowanie plików konfiguracyjnych
        self._customize_project(project_name)
        
        # Instalacja zależności
        if not skip_install:
            print("Instalowanie zależności...")
            
            # Instalacja zależności backendu
            os.chdir(os.path.join(project_name, 'server'))
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            
            # Instalacja zależności frontendu
            os.chdir(os.path.join('..', 'client'))
            subprocess.run(['npm', 'install'])
            
            # Powrót do katalogu nadrzędnego
            os.chdir('../..')
        
        print(f"Projekt '{project_name}' został utworzony pomyślnie!")
        print(f"Aby uruchomić serwer deweloperski, wykonaj:")
        print(f"  cd {project_name}")
        print(f"  ferro dev")
        
        return 0
    
    def _customize_project(self, project_dir: str) -> None:
        """
        Dostosowanie plików projektu
        
        Args:
            project_dir: Katalog projektu
        """
        # Dostosowanie pliku package.json
        package_json_path = os.path.join(project_dir, 'client', 'package.json')
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Aktualizacja nazwy projektu
            package_data['name'] = project_dir
            
            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
    
    def cmd_generate(self, args: argparse.Namespace) -> int:
        """
        Generowanie komponentów, stron, modeli lub API
        
        Args:
            args: Sparsowane argumenty
        
        Returns:
            Kod wyjścia
        """
        gen_type = args.type
        name = args.name
        
        # Sprawdzenie, czy jesteśmy w projekcie Ferro
        if not self._is_ferro_project():
            print("Błąd: Nie jesteś w projekcie Ferro.")
            return 1
        
        # Wywołanie odpowiedniej metody generowania
        generator_method = getattr(self, f'_generate_{gen_type}', None)
        if generator_method:
            try:
                generator_method(name)
                print(f"{gen_type.capitalize()} '{name}' został wygenerowany pomyślnie!")
                return 0
            except Exception as e:
                print(f"Błąd podczas generowania {gen_type}: {str(e)}")
                return 1
        else:
            print(f"Nieobsługiwany typ generatora: {gen_type}")
            return 1
    
    def _generate_component(self, name: str) -> None:
        """
        Generowanie komponentu React
        
        Args:
            name: Nazwa komponentu
        """
        # Przygotowanie ścieżki komponentu
        component_dir = Path('client/components')
        component_dir.mkdir(exist_ok=True, parents=True)
        
        # Tworzenie pliku komponentu
        component_path = component_dir / f"{name}.tsx"
        with open(component_path, 'w') as f:
            f.write(f'''import React from 'react';

interface {name}Props {{
  // Zdefiniuj właściwości komponentu
}}

export const {name}: React.FC<{name}Props> = (props) => {{
  return (
    <div className="component-{name.lower()}">
      {/* Implementacja komponentu */}
    </div>
  );
}};

export default {name};
''')
    
    def _generate_page(self, name: str) -> None:
        """
        Generowanie strony Next.js
        
        Args:
            name: Nazwa strony
        """
        # Przygotowanie ścieżki strony
        page_dir = Path('client/pages')
        page_dir.mkdir(exist_ok=True, parents=True)
        
        # Tworzenie pliku strony
        page_path = page_dir / f"{name}.tsx"
        with open(page_path, 'w') as f:
            f.write(f'''import React from 'react';
import {{ GetServerSideProps }} from 'next';
import {{ withServerData }} from 'ferro/next-integration';

interface {name.capitalize()}PageProps {{
  // Zdefiniuj właściwości strony
  serverData?: any;
}}

export const {name.capitalize()}Page: React.FC<{name.capitalize()}PageProps> = (props) => {{
  return (
    <div className="page-{name.lower()}">
      <h1>{name.capitalize()}</h1>
      {/* Implementacja strony */}
    </div>
  );
}};

export const getServerSideProps: GetServerSideProps = withServerData(async (context) => {{
  // Pobieranie danych na serwerze
  return {{
    // Zwróć dane, które będą dostępne jako props
  }};
}});

export default {name.capitalize()}Page;
''')
    
    def _generate_model(self, name: str) -> None:
        """
        Generowanie modelu SQLAlchemy
        
        Args:
            name: Nazwa modelu
        """
        # Przygotowanie ścieżki modelu
        model_dir = Path('server/models')
        model_dir.mkdir(exist_ok=True, parents=True)
        
        # Tworzenie pliku modelu
        model_path = model_dir / f"{name.lower()}.py"
        with open(model_path, 'w') as f:
            f.write(f'''from server.ferro_orm import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime

class {name.capitalize()}(BaseModel):
    """
    Model {name.capitalize()}
    """
    __tablename__ = '{name.lower()}s'
    
    # Definicja kolumn
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relacje
    # Przykład: items = relationship("Item", back_populates="{name.lower()}")
    
    def __repr__(self):
        return f"<{name.capitalize()}(id={{self.id}}, name={{self.name}})>"
''')
    
    def _generate_api(self, name: str) -> None:
        """
        Generowanie endpointu API
        
        Args:
            name: Nazwa endpointu API
        """
        # Przygotowanie ścieżki API
        api_dir = Path('server/routes')
        api_dir.mkdir(exist_ok=True, parents=True)
        
        # Tworzenie pliku API
        api_path = api_dir / f"{name.lower()}.py"
        with open(api_path, 'w') as f:
            f.write(f'''from server.ferro_flask import api
from flask import request, jsonify
from typing import List, Dict, Any

@api.endpoint('/api/{name.lower()}', methods=['GET'])
def get_{name.lower()}s() -> List[Dict[str, Any]]:
    """
    Pobieranie wszystkich {name.lower()}s
    
    Returns:
        Lista {name.lower()}s
    """
    # Implementacja pobierania danych
    return []

@api.endpoint('/api/{name.lower()}/<int:id>', methods=['GET'])
def get_{name.lower()}(id: int) -> Dict[str, Any]:
    """
    Pobieranie pojedynczego {name.lower()} po ID
    
    Args:
        id: ID {name.lower()}
    
    Returns:
        Dane {name.lower()}
    """
    # Implementacja pobierania pojedynczego elementu
    return {{"id": id, "name": "Example"}}

@api.endpoint('/api/{name.lower()}', methods=['POST'])
def create_{name.lower()}() -> Dict[str, Any]:
    """
    Tworzenie nowego {name.lower()}
    
    Returns:
        Utworzony {name.lower()}
    """
    data = request.json
    # Implementacja tworzenia
    return {{"id": 1, **data}}

@api.endpoint('/api/{name.lower()}/<int:id>', methods=['PUT'])
def update_{name.lower()}(id: int) -> Dict[str, Any]:
    """
    Aktualizacja {name.lower()} po ID
    
    Args:
        id: ID {name.lower()}
    
    Returns:
        Zaktualizowany {name.lower()}
    """
    data = request.json
    # Implementacja aktualizacji
    return {{"id": id, **data}}

@api.endpoint('/api/{name.lower()}/<int:id>', methods=['DELETE'])
def delete_{name.lower()}(id: int) -> Dict[str, Any]:
    """
    Usuwanie {name.lower()} po ID
    
    Args:
        id: ID {name.lower()}
    
    Returns:
        Status operacji
    """
    # Implementacja usuwania
    return {{"success": True, "id": id}}
''')
    
    def cmd_dev(self, args: argparse.Namespace) -> int:
        """
        Uruchamianie serwera deweloperskiego
        
        Args:
            args: Sparsowane argumenty
        
        Returns:
            Kod wyjścia
        """
        backend_only = args.backend_only
        frontend_only = args.frontend_only
        
        # Sprawdzenie, czy jesteśmy w projekcie Ferro
        if not self._is_ferro_project():
            print("Błąd: Nie jesteś w projekcie Ferro.")
            return 1
        
        try:
            # Uruchamianie backendu
            if not frontend_only:
                print("Uruchamianie backendu Flask...")
                backend_process = subprocess.Popen(
                    [sys.executable, "-m", "flask", "run", "--debugger", "--reload"],
                    cwd="server",
                    env={**os.environ, "FLASK_APP": "app.py", "FLASK_ENV": "development"}
                )
            
            # Uruchamianie frontendu
            if not backend_only:
                print("Uruchamianie frontendu Next.js...")
                frontend_process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd="client"
                )
            
            # Oczekiwanie na zakończenie procesów
            try:
                if not frontend_only:
                    backend_process.wait()
                if not backend_only:
                    frontend_process.wait()
            except KeyboardInterrupt:
                print("\nZatrzymywanie serwerów...")
                # Zakończenie procesów po przerwaniu
                if not frontend_only:
                    backend_process.terminate()
                if not backend_only:
                    frontend_process.terminate()
            
            return 0
        
        except Exception as e:
            print(f"Błąd podczas uruchamiania serwerów: {str(e)}")
            return 1
    
    def cmd_sync_types(self, args: argparse.Namespace) -> int:
        """
        Synchronizacja typów między backendem i frontendem
        
        Args:
            args: Sparsowane argumenty
        
        Returns:
            Kod wyjścia
        """
        watch_mode = args.watch
        
        # Sprawdzenie, czy jesteśmy w projekcie Ferro
        if not self._is_ferro_project():
            print("Błąd: Nie jesteś w projekcie Ferro.")
            return 1
        
        try:
            # Jednorazowa synchronizacja
            self._sync_types()
            
            # Tryb ciągłego monitorowania
            if watch_mode:
                import time
                from watchdog.observers import Observer
                from watchdog.events import FileSystemEventHandler
                
                class TypeSyncHandler(FileSystemEventHandler):
                    def on_modified(self, event):
                        if event.src_path.endswith('.py') and 'models' in event.src_path:
                            print(f"Zmiana wykryta w: {event.src_path}")
                            self._sync_types()
                
                handler = TypeSyncHandler()
                observer = Observer()
                observer.schedule(handler, 'server/models', recursive=True)
                observer.start()
                
                print("Monitorowanie zmian w modelach... (Ctrl+C, aby zatrzymać)")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    observer.stop()
                observer.join()
            
            return 0
        
        except Exception as e:
            print(f"Błąd podczas synchronizacji typów: {str(e)}")
            return 1
    
    def _sync_types(self) -> None:
        """
        Wykonanie synchronizacji typów
        """
        print("Generowanie typów TypeScript z modeli SQLAlchemy...")
        
        # Uruchamianie skryptu synchronizacji
        subprocess.run([
            sys.executable, "-c",
            "from server.app import ferro_orm; ferro_orm.generate_typescript_types()"
        ])
        
        print("Synchronizacja typów zakończona pomyślnie!")
    
    def cmd_build(self, args: argparse.Namespace) -> int:
        """
        Budowanie projektu
        
        Args:
            args: Sparsowane argumenty
        
        Returns:
            Kod wyjścia
        """
        backend_only = args.backend_only
        frontend_only = args.frontend_only
        
        # Sprawdzenie, czy jesteśmy w projekcie Ferro
        if not self._is_ferro_project():
            print("Błąd: Nie jesteś w projekcie Ferro.")
            return 1
        
        try:
            # Budowanie backendu
            if not frontend_only:
                print("Budowanie backendu...")
                # W przypadku Pythona, zazwyczaj wystarczy przygotować requirements.txt
                # i ewentualnie wygenerować pliki statyczne
                
                # Generowanie listy zależności
                subprocess.run([
                    sys.executable, "-m", "pip", "freeze"
                ], stdout=open("server/requirements-prod.txt", "w"))
                
                print("Backend zbudowany pomyślnie!")
            
            # Budowanie frontendu
            if not backend_only:
                print("Budowanie frontendu...")
                subprocess.run([
                    "npm", "run", "build"
                ], cwd="client")
                
                print("Frontend zbudowany pomyślnie!")
            
            return 0
        
        except Exception as e:
            print(f"Błąd podczas budowania projektu: {str(e)}")
            return 1
    
    def _is_ferro_project(self) -> bool:
        """
        Sprawdzenie, czy bieżący katalog zawiera projekt Ferro
        
        Returns:
            True, jeśli jesteśmy w projekcie Ferro, False w przeciwnym razie
        """
        # Sprawdzenie podstawowych katalogów
        return (
            os.path.isdir('server') and
            os.path.isdir('client') and
            os.path.exists('server/app.py')
        )

def main():
    """Punkt wejścia dla CLI"""
    command = FerroCommand()
    sys.exit(command.run())

if __name__ == "__main__":
    main() 