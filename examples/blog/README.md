# Przykładowa Aplikacja Bloga z Ferro Framework

Ten przykład pokazuje, jak zbudować pełną aplikację bloga z wykorzystaniem Ferro Framework, integrując Next.js, Flask, Tailwind CSS i ORM.

## Funkcjonalności

- Autentykacja użytkowników (rejestracja, logowanie, zarządzanie profilem)
- Tworzenie, edycja i usuwanie postów
- Komentowanie postów
- Tagi i kategorie
- Markdown dla treści
- Wyszukiwanie i filtrowanie
- Responsywny design z Tailwind CSS

## Struktura projektu

```
blog/
├── client/                  # Frontend Next.js
│   ├── components/          # Komponenty React
│   ├── pages/               # Strony Next.js
│   ├── public/              # Statyczne pliki
│   ├── styles/              # Style Tailwind
│   └── types/               # Typy TypeScript (generowane)
├── server/                  # Backend Flask
│   ├── config/              # Konfiguracja serwera
│   ├── models/              # Modele SQLAlchemy
│   ├── routes/              # Endpointy API
│   └── services/            # Logika biznesowa
└── shared/                  # Współdzielony kod
    └── types/               # Współdzielone typy
```

## Uruchamianie aplikacji

### Instalacja zależności

```bash
# Instalacja zależności dla backendu
cd server
pip install -r requirements.txt

# Instalacja zależności dla frontendu
cd ../client
npm install
```

### Konfiguracja bazy danych

```bash
# Tworzenie i migracja bazy danych
cd ../server
python manage.py create_db
python manage.py migrate
```

### Uruchamianie w trybie deweloperskim

```bash
# Uruchamianie backendu
cd server
python app.py

# Uruchamianie frontendu
cd ../client
npm run dev
```

## Diagram przepływu danych

Aplikacja używa Ferro Framework do zapewnienia płynnej integracji między komponentami:

1. **Modele danych** - Definiowane w SQLAlchemy, automatycznie generują typy TypeScript
2. **API Flask** - Endpointy automatycznie dokumentowane i eksponowane dla frontendu
3. **Integracja Next.js** - Komponenty React używają wygenerowanych klientów API
4. **Komponenty UI** - Spójny system projektowania z Tailwind CSS

## Przykładowy kod

### Model danych (Python)

```python
from server.ferro_orm import BaseModel
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Post(BaseModel):
    __tablename__ = 'posts'
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relacje
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
```

### Endpoint API (Python)

```python
from server.ferro_flask import api

@api.endpoint('/api/posts', methods=['GET'])
def get_posts():
    """Pobieranie wszystkich postów"""
    posts = Post.query.all()
    return [post.to_dict() for post in posts]

@api.endpoint('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id: int):
    """Pobieranie pojedynczego posta"""
    post = Post.query.get_or_404(post_id)
    return post.to_dict()
```

### Komponent React (TypeScript)

```tsx
import { useApi } from 'ferro/next-integration';
import { Button } from 'ferro/ui-components';

export default function PostsList() {
  const { data: posts, loading, error } = useApi<Post[]>('/api/posts');
  
  if (loading) return <div>Ładowanie...</div>;
  if (error) return <div>Błąd: {error.message}</div>;
  
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Lista postów</h1>
      {posts?.map(post => (
        <div key={post.id} className="p-4 border rounded">
          <h2 className="text-xl">{post.title}</h2>
          <p className="text-gray-600">{post.author.name}</p>
          <Button variant="outline" href={`/posts/${post.id}`}>
            Czytaj więcej
          </Button>
        </div>
      ))}
    </div>
  );
}
```

## Rozszerzanie aplikacji

To tylko początkowy przykład. Możesz go rozszerzyć o:

1. System powiadomień w czasie rzeczywistym (z WebSockets)
2. Zaawansowane wyszukiwanie (z pełnotekstowym wyszukiwaniem)
3. Zarządzanie multimediami (przesyłanie obrazów/wideo)
4. Analitykę i raportowanie
5. System uprawnień i ról

Dokumentacja Ferro Framework zawiera więcej informacji o zaawansowanych funkcjach i najlepszych praktykach. 