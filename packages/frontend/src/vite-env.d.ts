/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  readonly VITE_DEFAULT_INPUT?: string;
  readonly VITE_DEFAULT_OUTPUT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
