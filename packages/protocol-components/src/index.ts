// Protocol Components - Clean state management for BDSA protocols

// Context and Hook (State Management)
export { ProtocolProvider, useProtocols } from './context/ProtocolContext';

// UI Components
export { default as ProtocolCard } from './components/ProtocolCard';
export { default as ProtocolList } from './components/ProtocolList';
export { default as ProtocolModal } from './components/ProtocolModal';

// Storage
export {
    LocalStorageProtocolStorage,
    InMemoryProtocolStorage,
    defaultStorage,
    generateProtocolId
} from './storage/protocolStorage';

// Types (for future TypeScript support)
export type Protocol = {
    id: string;
    type: 'stain' | 'region';
    name: string;
    description?: string;
    [key: string]: any;
};

