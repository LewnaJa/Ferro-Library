# Ferro Framework

## Przegląd

Ferro to zaawansowany framework integracyjny łączący technologie Next.js, Flask, Tailwind CSS i ORM w jeden spójny ekosystem. Framework został zaprojektowany, aby umożliwić programistom pełne wykorzystanie:

- **Next.js** - dla nowoczesnego, wydajnego frontendu z renderowaniem po stronie serwera
- **Flask** - dla elastycznego i skalowalnego backendu w Pythonie
- **Tailwind CSS** - dla szybkiego i responsywnego projektowania interfejsu
- **ORM** - dla typowo bezpiecznego dostępu do bazy danych (SQLAlchemy + TypeORM)

## Główne funkcjonalności

- 🔄 **Dwukierunkowa synchronizacja typów** - automatyczne generowanie typów TypeScript z modeli Pythona
- 🔌 **Bezproblemowa integracja API** - wywoływanie endpointów Flask bezpośrednio z kodu Next.js
- 🛠️ **Wspólne narzędzia deweloperskie** - pojedynczy interfejs dla uruchamiania, testowania i wdrażania
- 🎨 **Komponenty UI z Tailwind** - biblioteka predefiniowanych, spójnych komponentów
- 📊 **Wspólne warstwy danych** - jednolity sposób dostępu do danych z obu stron

## Wymagania

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+ (lub inna kompatybilna baza danych)

## Instalacja

```bash
npx create-ferro-app my-project
```

## Dokumentacja

Pełna dokumentacja dostępna jest w katalogu `/docs` lub online na [docs.ferroframework.pl](https://docs.ferroframework.pl).

## Licencja

MIT 