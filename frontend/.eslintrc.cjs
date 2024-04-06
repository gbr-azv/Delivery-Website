module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    //'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:@typescript-eslint/recommended-type-checked', // Ativa regras que necessitam de verificação de tipos
    'plugin:@typescript-eslint/stylistic-type-checked',
    'plugin:react/recommended', // Usa as recomendações do plugin React
    'plugin:react/jsx-runtime' // Necessário para o novo transform JSX
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest', // Versão do ECMAScript
    sourceType: 'module', // Permite o uso de importações ES6
    project: ['./tsconfig.json', './tsconfig.node.json'], // Caminho para os arquivos tsconfig
    tsconfigRootDir: __dirname, // Define o diretório raiz para o ESLint encontrar o tsconfig
    ecmaFeatures: {
      jsx: true, // Permite o parsing de JSX
    },
  },
  plugins: [
    'react-refresh',
    '@typescript-eslint', // Adiciona o plugin do TypeScript
    'react' // Adiciona o plugin do React
  ],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}