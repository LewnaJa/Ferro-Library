# Struktura Projektu Ferro Framework

```
ferro-framework/
├── packages/
│   ├── cli/                    # Narzędzie linii poleceń dla tworzenia i zarządzania projektami
│   ├── core/                   # Główne funkcje i logika frameworka
│   ├── type-sync/              # Narzędzie do synchronizacji typów między Python i TypeScript
│   ├── ui-components/          # Komponenty UI z Tailwind CSS
│   └── data-layer/             # Warstwa abstrakcji danych
├── server/
│   ├── ferro_flask/            # Rozszerzenia Flask dla integracji z Next.js
│   ├── orm/                    # Rozszerzenia ORM (SQLAlchemy) z generowaniem typów
│   └── middleware/             # Middleware do obsługi sesji, autoryzacji itp.
├── client/
│   ├── next-integration/       # Integracja z Next.js
│   ├── hooks/                  # React hooks do komunikacji z backendem
│   └── data-fetching/          # Narzędzia do pobierania danych z API Flask
├── templates/                  # Szablony projektów do użycia z CLI
├── examples/                   # Przykładowe aplikacje
│   ├── blog/
│   ├── e-commerce/
│   └── dashboard/
├── docs/                       # Dokumentacja
└── scripts/                    # Skrypty deweloperskie i narzędzia budowania
```

## Kluczowe Komponenty

### 1. Ferro CLI (`packages/cli`)

Narzędzie wiersza poleceń do:
- Tworzenia nowych projektów
- Generowania komponentów
- Zarządzania migracjami bazy danych
- Uruchamiania środowiska deweloperskiego (frontend + backend)
- Wdrażania aplikacji

### 2. Type Sync (`packages/type-sync`)

Dwukierunkowa synchronizacja typów:
- Generowanie interfejsów TypeScript z modeli SQLAlchemy
- Generowanie dokumentacji API z definicji endpointów Flask
- Walidacja typów w czasie rzeczywistym między środowiskami

### 3. Warstwa Danych (`packages/data-layer`)

Jednolity interfejs do pracy z danymi:
- Abstrakcja nad ORM (SQLAlchemy po stronie serwera)
- Klient GraphQL/REST dla frontendu
- Cachowanie i zarządzanie stanem po stronie klienta

### 4. Rozszerzenie Flask (`server/ferro_flask`)

Dostosowanie Flask do współpracy z Next.js:
- Dekoratory endpointów z automatyczną dokumentacją API
- Obsługa WebSocket do komunikacji w czasie rzeczywistym
- Middleware do uwierzytelniania i autoryzacji
- Integracja z systemami kolejkowania zadań

### 5. Integracja Next.js (`client/next-integration`)

Komponenty i narzędzia dla Next.js:
- Konfiguracja routingu dla komunikacji z Flask
- SSR z danymi z backendu Flask
- Klienty API generowane na podstawie backendu
- Obsługa stanów ładowania i błędów

### 6. Komponenty UI (`packages/ui-components`)

Biblioteka komponentów z Tailwind CSS:
- Dostosowywalne motywy
- Komponenty formularzy z walidacją
- Elementy układu i nawigacji
- Komponenty wyświetlania danych 