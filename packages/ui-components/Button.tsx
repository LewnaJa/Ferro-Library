import React, { ButtonHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from './utils';

// Definicja wariantów przycisku używając class-variance-authority
const buttonVariants = cva(
  // Podstawowe style wspólne dla wszystkich wariantów
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      // Warianty stylu
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      // Warianty rozmiaru
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 px-3 text-sm',
        lg: 'h-12 px-8 text-lg',
        icon: 'h-10 w-10 p-0',
      },
      // Warianty rozciągnięcia na pełną szerokość
      fullWidth: {
        true: 'w-full',
      },
      // Warianty zaokrąglenia
      rounded: {
        default: 'rounded-md',
        full: 'rounded-full',
        none: 'rounded-none',
      },
      // Warianty stanu ładowania
      loading: {
        true: 'relative text-transparent transition-none hover:text-transparent',
      },
    },
    // Domyślne wartości dla wariantów
    defaultVariants: {
      variant: 'default',
      size: 'default',
      rounded: 'default',
      loading: false,
    },
  }
);

// Typ definiujący dostępne właściwości dla komponentu przycisku
export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /** Właściwość określająca stan ładowania przycisku */
  loading?: boolean;
  /** Zawartość przycisku */
  children: ReactNode;
  /** Ikona, która ma być wyświetlana przed tekstem przycisku */
  startIcon?: ReactNode;
  /** Ikona, która ma być wyświetlana po tekście przycisku */
  endIcon?: ReactNode;
}

/**
 * Komponent przycisku Ferro, zbudowany z użyciem Tailwind CSS.
 * Zapewnia konsystentny wygląd i zachowanie w całej aplikacji.
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant,
    size,
    rounded,
    fullWidth,
    loading = false,
    children,
    startIcon,
    endIcon,
    disabled,
    ...props
  }, ref) => {
    return (
      <button
        className={cn(buttonVariants({
          variant,
          size,
          rounded,
          fullWidth,
          loading,
          className
        }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {/* Ikona ładowania wyświetlana, gdy przycisk jest w stanie ładowania */}
        {loading && (
          <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <svg
              className="animate-spin h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </span>
        )}
        
        {/* Ikona początkowa, jeśli istnieje */}
        {startIcon && <span className={cn("mr-2", { "opacity-0": loading })}>{startIcon}</span>}
        
        {/* Zawartość przycisku */}
        <span className={cn({ "opacity-0": loading })}>{children}</span>
        
        {/* Ikona końcowa, jeśli istnieje */}
        {endIcon && <span className={cn("ml-2", { "opacity-0": loading })}>{endIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'FerroButton';

export default Button; 