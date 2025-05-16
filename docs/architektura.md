# Architektura Ferro Framework

Ferro Framework to zaawansowany framework integracyjny łączący technologie Next.js, Flask, Tailwind CSS i ORM (SQLAlchemy/TypeORM) w jeden spójny ekosystem deweloperski. Poniżej przedstawiono szczegółowy opis architektury frameworka oraz przepływu danych między komponentami.

## Główne komponenty

### 1. Ferro Flask (`server/ferro_flask`)

Rozszerzenie Flask, które dostarcza:
- Dekoratory endpointów z automatycznym zbieraniem metadanych
- Generowanie dokumentacji API
- Eksport typów danych do TypeScript
- Integrację z WebSocket
- Middleware uwierzytelniania i autoryzacji

### 2. Ferro ORM (`server/orm`)

Rozszerzenie SQLAlchemy, które dostarcza:
- Bazowe modele z polami utworzenia/aktualizacji
- Repository Pattern dla operacji CRUD
- Automatyczne generowanie typów TypeScript z modeli
- Wsparcie dla migracji
- Walidację danych

### 3. Ferro Next Integration (`client/next-integration`)

Integracja z Next.js, która dostarcza:
- Hooki do komunikacji z API
- SSR z danymi z backendu Flask
- Generowane klienty API
- Obsługę WebSockets
- Zarządzanie formularzami i walidację

### 4. Ferro UI Components (`packages/ui-components`)

Biblioteka komponentów UI z Tailwind CSS:
- Responsywne komponenty
- Motywy i style
- Dostępność (a11y)
- Formularze i walidacja
- Wizualizacja danych

### 5. Ferro CLI (`packages/cli`)

Narzędzie wiersza poleceń dla:
- Tworzenia projektów
- Generowania komponentów
- Zarządzania migracjami
- Uruchamiania środowiska deweloperskiego
- Synchronizacji typów

## Przepływ danych

```
+---------------+       +---------------+       +---------------+
|               |       |               |       |               |
|   Models      |------>|   API         |------>|   React       |
|   (Python)    |       |   (Flask)     |       |   (Next.js)   |
|               |       |               |       |               |
+---------------+       +---------------+       +---------------+
        |                                               |
        |                                               |
        v                                               v
+---------------+                               +---------------+
|               |                               |               |
|   TypeScript  |<----------------------------->|   UI          |
|   Types       |                               |   Components  |
|               |                               |               |
+---------------+                               +---------------+
```

### Szczegółowy przepływ informacji:

1. **Definicja modeli** - Modele danych definiowane są w SQLAlchemy przy użyciu `BaseModel` z `ferro_orm`.

2. **Automatyczne generowanie typów** - Na podstawie modeli SQLAlchemy, framework generuje odpowiadające interfejsy TypeScript.

3. **Implementacja API** - Endpointy API są definiowane przy użyciu dekoratorów `@api.endpoint` z `ferro_flask`, które automatycznie zbierają metadane.

4. **Generowanie klientów API** - Na podstawie metadanych API, framework generuje klienty API dla frontendu.

5. **Użycie w React** - Komponenty React używają wygenerowanych hooków i typów do komunikacji z API.

6. **Renderowanie UI** - Komponenty UI z `ferro_ui` wykorzystują Tailwind CSS do spójnego wyglądu.

## Mechanizmy synchronizacji typów

Jednym z kluczowych aspektów Ferro Framework jest automatyczna synchronizacja typów między backendem Python a frontendem TypeScript.

### Proces synchronizacji:

1. **Analiza modeli SQLAlchemy**:
   - Inspekcja pól (nazwa, typ, czy nullable)
   - Analiza relacji (one-to-many, many-to-one)
   - Wykrywanie walidatorów

2. **Generowanie interfejsów TypeScript**:
   - Mapowanie typów Python na TypeScript
   - Generowanie typów dla relacji
   - Dodawanie komentarzy dokumentacji

3. **Generowanie klientów API**:
   - Analiza sygnatur funkcji endpointów
   - Mapowanie parametrów i typów zwracanych
   - Generowanie funkcji pomocniczych

4. **Wyzwalanie synchronizacji**:
   - Automatycznie przy uruchomieniu serwera
   - Na żądanie przez `ferro sync-types`
   - W trybie watch przez `ferro sync-types --watch`

## Bezpieczeństwo

Framework implementuje kilka warstw bezpieczeństwa:

1. **Uwierzytelnianie**:
   - Wsparcie dla JWT
   - Integracja z OAuth
   - Obsługa sesji

2. **Autoryzacja**:
   - Role i uprawnienia
   - Kontrola dostępu na poziomie endpointów
   - Kontrola dostępu na poziomie pól

3. **Walidacja danych**:
   - Walidacja na poziomie modeli
   - Walidacja na poziomie formularzy
   - Sanityzacja danych wejściowych

4. **Ochrona przed atakami**:
   - CSRF protection
   - XSS protection
   - Rate limiting

## Skalowanie

Framework został zaprojektowany z myślą o skalowaniu:

1. **Horyzontalnie**:
   - Bezstanowy backend
   - Wsparcie dla load balancingu
   - Cachowanie współdzielone

2. **Wertykalnie**:
   - Optymalizacje zapytań do bazy danych
   - Lazy loading relacji
   - Efektywne wykorzystanie pamięci

## Rozszerzalność

Ferro Framework może być rozszerzany na wiele sposobów:

1. **Wtyczki**:
   - System wtyczek dla Flask
   - Integracja z zewnętrznymi API
   - Dodatkowe generatory typów

2. **Własne komponenty UI**:
   - Rozszerzanie biblioteki komponentów
   - Własne motywy Tailwind
   - Niestandardowe animacje

3. **Middleware**:
   - Dodawanie własnych middleware
   - Integracja z systemami monitoringu
   - Zaawansowane logowanie

## Podsumowanie

Ferro Framework dostarcza kompleksowe rozwiązanie dla tworzenia aplikacji webowych, łącząc najlepsze praktyki z różnych ekosystemów technologicznych. Dzięki automatycznej synchronizacji typów, spójnej bibliotece komponentów UI i wydajnemu narzędziu CLI, framework znacząco przyspiesza proces tworzenia aplikacji oraz redukuje błędy wynikające z niezgodności między frontendem a backendem. 