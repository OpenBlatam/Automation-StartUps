/**
 * Prettier Configuration - CFDI 4.0 IA 2025
 */

module.exports = {
  // Tamaño de línea
  printWidth: 100,
  
  // Tabulaciones
  tabWidth: 2,
  useTabs: false,
  
  // Punto y coma
  semi: true,
  
  // Comillas
  singleQuote: true,
  quoteProps: 'as-needed',
  
  // JSX (si lo usas)
  jsxSingleQuote: true,
  
  // Paréntesis de funciones
  arrowParens: 'always',
  
  // Espacios finales
  endOfLine: 'lf',
  
  // Otros
  trailingComma: 'none',
  bracketSpacing: true,
  bracketSameLine: false,
  
  // Organización de imports
  importOrder: [
    '^react$',
    '^next',
    '^@/',
    '<THIRD_PARTY_MODULES>',
    '^[./]'
  ]
};



