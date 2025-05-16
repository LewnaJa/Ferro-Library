/**
 * Ferro Framework - Integracja z Next.js
 * 
 * Moduł zapewniający bezproblemową integrację aplikacji Next.js z backendem Flask.
 */

import { useState, useEffect } from 'react';
import type { GetServerSidePropsContext } from 'next';

// Typy dla konfiguracji
export interface FerroConfig {
  /** Adres URL backendu Flask */
  apiUrl: string;
  /** Czy używać WebSockets do komunikacji w czasie rzeczywistym */
  useWebsockets?: boolean;
  /** Timeout dla żądań API (ms) */
  timeout?: number;
  /** Czy automatycznie odświeżać tokeny uwierzytelniające */
  autoRefreshAuth?: boolean;
}

// Domyślna konfiguracja
const defaultConfig: FerroConfig = {
  apiUrl: process.env.NEXT_PUBLIC_FLASK_API_URL || 'http://localhost:5000',
  useWebsockets: false,
  timeout: 10000,
  autoRefreshAuth: true
};

// Stan globalny
let ferroConfig: FerroConfig = { ...defaultConfig };
let metadataCache: any = null;

/**
 * Inicjalizacja Ferro dla aplikacji Next.js
 */
export function initFerro(config: Partial<FerroConfig> = {}): FerroConfig {
  ferroConfig = { ...defaultConfig, ...config };
  return ferroConfig;
}

/**
 * Hook do wykonywania żądań API z automatycznym mapowaniem typów
 */
export function useApi<T = any>(
  endpoint: string,
  options: {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    params?: Record<string, any>;
    body?: any;
    headers?: Record<string, string>;
    immediate?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  } = {}
) {
  const {
    method = 'GET',
    params = {},
    body,
    headers = {},
    immediate = true,
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(immediate);
  const [error, setError] = useState<Error | null>(null);

  // Funkcja wykonująca żądanie
  const execute = async (customParams?: Record<string, any>, customBody?: any): Promise<T | null> => {
    try {
      setLoading(true);
      setError(null);

      // Przygotowanie query string
      const queryParams = new URLSearchParams();
      const finalParams = { ...params, ...(customParams || {}) };
      
      Object.entries(finalParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });

      // Przygotowanie URL
      const queryString = queryParams.toString();
      const url = `${ferroConfig.apiUrl}${endpoint}${queryString ? `?${queryString}` : ''}`;

      // Przygotowanie nagłówków
      const defaultHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Dodanie tokena JWT jeśli istnieje
      const token = typeof window !== 'undefined' ? localStorage.getItem('ferro_auth_token') : null;
      if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
      }

      // Wykonanie żądania
      const response = await fetch(url, {
        method,
        headers: { ...defaultHeaders, ...headers },
        body: customBody || body ? JSON.stringify(customBody || body) : undefined,
        signal: AbortSignal.timeout(ferroConfig.timeout || 10000)
      });

      // Obsługa błędów HTTP
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Błąd HTTP: ${response.status}`);
      }

      // Parsowanie odpowiedzi
      const responseData = await response.json() as T;
      setData(responseData);
      onSuccess?.(responseData);
      return responseData;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      onError?.(error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Automatyczne wykonanie żądania przy montowaniu komponentu
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, []);

  return { data, loading, error, execute, refetch: execute };
}

/**
 * Funkcja do pobierania metadanych API z serwera Flask
 */
export async function getApiMetadata() {
  if (metadataCache) {
    return metadataCache;
  }

  try {
    const response = await fetch(`${ferroConfig.apiUrl}/_ferro/api-metadata`);
    if (!response.ok) {
      throw new Error(`Nie udało się pobrać metadanych API: ${response.status}`);
    }

    const metadata = await response.json();
    metadataCache = metadata;
    return metadata;
  } catch (error) {
    console.error('Błąd podczas pobierania metadanych API:', error);
    throw error;
  }
}

/**
 * Generator klienta API
 * 
 * Tworzy klienta API dla backendu Flask na podstawie metadanych endpointów
 */
export async function createApiClient<T = any>(): Promise<T> {
  const metadata = await getApiMetadata();
  const client: Record<string, any> = {};

  // Generowanie funkcji dla każdego endpointu
  for (const endpoint of metadata.endpoints) {
    client[endpoint.name] = async (params: Record<string, any> = {}) => {
      const { route, methods } = endpoint;
      const method = methods[0]; // Używamy pierwszej metody z listy
      
      // Parametry URL vs Body
      const urlParams: Record<string, any> = {};
      const bodyParams: Record<string, any> = {};
      
      if (method === 'GET') {
        Object.assign(urlParams, params);
      } else {
        Object.assign(bodyParams, params);
      }

      // Wywołanie API
      const { execute } = useApi(route, {
        method: method as any,
        params: urlParams,
        body: Object.keys(bodyParams).length > 0 ? bodyParams : undefined,
        immediate: false
      });

      return execute();
    };
  }

  return client as T;
}

/**
 * Hook do uzyskiwania danych na serwerze Next.js podczas SSR
 */
export function withServerData(
  handler: (context: GetServerSidePropsContext) => Promise<any>
) {
  return async (context: GetServerSidePropsContext) => {
    try {
      const data = await handler(context);
      
      return {
        props: {
          serverData: data || null,
          error: null
        }
      };
    } catch (err) {
      console.error('Błąd podczas pobierania danych na serwerze:', err);
      
      return {
        props: {
          serverData: null,
          error: err instanceof Error ? err.message : String(err)
        }
      };
    }
  };
}

/**
 * Hook do komunikacji w czasie rzeczywistym z użyciem WebSockets
 */
export function useRealtime<T = any>(
  channel: string,
  options: {
    onMessage?: (data: T) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
  } = {}
) {
  const [connected, setConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<T[]>([]);
  const [socket, setSocket] = useState<any>(null);

  useEffect(() => {
    if (!ferroConfig.useWebsockets) {
      console.warn('WebSockets nie są włączone w konfiguracji Ferro.');
      return;
    }

    // Importowanie biblioteki Socket.IO dynamicznie
    import('socket.io-client').then(({ io }) => {
      const socket = io(ferroConfig.apiUrl);
      
      socket.on('connect', () => {
        setConnected(true);
        options.onConnect?.();
        
        // Dołączanie do kanału
        socket.emit('join', { channel });
      });
      
      socket.on('disconnect', () => {
        setConnected(false);
        options.onDisconnect?.();
      });
      
      socket.on(channel, (data: T) => {
        setMessages(prev => [...prev, data]);
        options.onMessage?.(data);
      });
      
      setSocket(socket);
      
      // Czyszczenie
      return () => {
        socket.off(channel);
        socket.disconnect();
      };
    });
  }, [channel]);

  // Funkcja do wysyłania wiadomości
  const send = (data: any) => {
    if (socket && connected) {
      socket.emit(channel, data);
      return true;
    }
    return false;
  };

  return { connected, messages, send };
}

/**
 * Hook do synchronizacji stanu formularza z automatyczną walidacją
 */
export function useForm<T extends Record<string, any>>(
  initialData: T,
  validationSchema?: Record<string, (value: any) => string | null>
) {
  const [data, setData] = useState<T>(initialData);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [isDirty, setIsDirty] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean>(true);

  // Funkcja do aktualizacji pojedynczego pola
  const setField = (field: keyof T, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
    setIsDirty(true);
    
    // Walidacja pola
    if (validationSchema && validationSchema[field as string]) {
      const error = validationSchema[field as string](value);
      setErrors(prev => ({ ...prev, [field]: error }));
    }
  };

  // Walidacja całego formularza
  const validate = (): boolean => {
    if (!validationSchema) return true;
    
    const newErrors: Record<string, string | null> = {};
    let formIsValid = true;
    
    Object.entries(validationSchema).forEach(([field, validator]) => {
      const error = validator(data[field]);
      newErrors[field] = error;
      if (error) formIsValid = false;
    });
    
    setErrors(newErrors);
    setIsValid(formIsValid);
    return formIsValid;
  };

  // Resetowanie formularza
  const reset = () => {
    setData(initialData);
    setErrors({});
    setIsDirty(false);
    setIsValid(true);
  };

  // Automatyczna walidacja przy zmianie danych
  useEffect(() => {
    if (isDirty && validationSchema) {
      validate();
    }
  }, [data]);

  return {
    data,
    errors,
    setField,
    validate,
    reset,
    isDirty,
    isValid
  };
} 