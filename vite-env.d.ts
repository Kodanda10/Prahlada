/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN?: string;
    readonly NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN?: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
