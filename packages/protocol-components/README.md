# @bdsa/protocol-components

Shared protocol management components and state for BDSA applications.

## Features

- **Unified State Management**: Single `ProtocolContext` with `useProtocols` hook
- **Storage Abstraction**: localStorage-backed protocol persistence with default IGNORE protocols
- **UI Components**: Ready-to-use React components for protocol display and editing
- **Type Safety**: Support for both stain and region protocol types

## Installation

```bash
# In a workspace package
npm install @bdsa/protocol-components
```

## Core Concepts

### Default Protocols

The system includes two default "IGNORE" protocols:
- `ignore-stain` (Stain): Mark slide for exclusion from stain processing
- `ignore-region` (Region): Mark slide for exclusion from region processing

These cannot be deleted and are always available.

## Usage

### 1. Wrap Your App with ProtocolProvider

```jsx
import { ProtocolProvider } from '@bdsa/protocol-components';

function App() {
  return (
    <ProtocolProvider>
      <YourAppContent />
    </ProtocolProvider>
  );
}
```

### 2. Use the useProtocols Hook

```jsx
import { useProtocols } from '@bdsa/protocol-components';

function ProtocolsTab() {
  const {
    protocols,           // All protocols
    stainProtocols,      // Filtered stain protocols
    regionProtocols,     // Filtered region protocols
    addProtocol,         // (protocol) => void
    updateProtocol,      // (id, updates) => void
    deleteProtocol,      // (id) => void
    loading,             // boolean
    error               // string | null
  } = useProtocols();

  // Add a new protocol
  const handleAdd = async () => {
    await addProtocol({
      type: 'stain',
      name: 'My Stain',
      description: 'Custom stain protocol',
      stainType: 'TDP-43',
      // ... other fields
    });
  };

  // Update an existing protocol
  const handleUpdate = async (id) => {
    await updateProtocol(id, {
      name: 'Updated Name',
      description: 'Updated description'
    });
  };

  // Delete a protocol (default protocols are protected)
  const handleDelete = async (id) => {
    await deleteProtocol(id);
  };

  return (
    <div>
      <h2>Stain Protocols ({stainProtocols.length})</h2>
      {stainProtocols.map(protocol => (
        <div key={protocol.id}>{protocol.name}</div>
      ))}
    </div>
  );
}
```

### 3. Use UI Components

#### ProtocolList

Display a grid of protocols with edit/delete actions:

```jsx
import { ProtocolList } from '@bdsa/protocol-components';

function MyProtocolsPage() {
  const { stainProtocols, deleteProtocol } = useProtocols();
  const [editingProtocol, setEditingProtocol] = useState(null);

  return (
    <ProtocolList
      protocols={stainProtocols}
      onEdit={setEditingProtocol}
      onDelete={deleteProtocol}
    />
  );
}
```

#### ProtocolCard

Display a single protocol:

```jsx
import { ProtocolCard } from '@bdsa/protocol-components';

function ProtocolDetails({ protocol }) {
  return (
    <ProtocolCard
      protocol={protocol}
      onEdit={() => console.log('Edit', protocol.id)}
      onDelete={() => console.log('Delete', protocol.id)}
    />
  );
}
```

#### ProtocolModal

Modal for creating/editing protocols with schema-driven validation:

```jsx
import { useState } from 'react';
import { ProtocolModal, useProtocols } from '@bdsa/protocol-components';

function ProtocolManagement() {
  const { addProtocol, updateProtocol } = useProtocols();
  const [showModal, setShowModal] = useState(false);
  const [editingProtocol, setEditingProtocol] = useState(null);

  const handleSave = async (formData) => {
    if (editingProtocol) {
      await updateProtocol(editingProtocol.id, formData);
    } else {
      await addProtocol(formData);
    }
    setShowModal(false);
    setEditingProtocol(null);
  };

  return (
    <>
      <button onClick={() => setShowModal(true)}>Add Protocol</button>
      
      {showModal && (
        <ProtocolModal
          protocol={editingProtocol}
          type="stain"  // or "region"
          onSave={handleSave}
          onClose={() => {
            setShowModal(false);
            setEditingProtocol(null);
          }}
          schemaValidator={mySchemaValidator} // optional
        />
      )}
    </>
  );
}
```

**ProtocolModal Props:**
- `protocol`: Existing protocol to edit (null for new)
- `type`: `'stain'` or `'region'`
- `onSave`: `(formData) => Promise<void>` - called when form is submitted
- `onClose`: `() => void` - called when modal is closed
- `schemaValidator`: Optional schema validator instance for advanced validation and dynamic field options

**Without schemaValidator:** The modal provides basic form fields and validation.

**With schemaValidator:** The modal dynamically shows/hides fields based on schema definitions and provides advanced validation. The validator should have methods like:
- `getStainTypeOptions()` / `getRegionTypeOptions()`
- `getAntibodyOptions(stainType)`
- `getLandmarkOptions(regionType)`
- `validateStainProtocol(data)` / `validateRegionProtocol(data)`

### 4. Custom Storage (Advanced)

```jsx
import { ProtocolProvider } from '@bdsa/protocol-components';

class CustomStorage {
  async load() {
    // Load from API
    const response = await fetch('/api/protocols');
    return await response.json();
  }

  async save(protocols) {
    // Save to API
    await fetch('/api/protocols', {
      method: 'POST',
      body: JSON.stringify(protocols)
    });
  }
}

function App() {
  return (
    <ProtocolProvider storage={new CustomStorage()}>
      <YourApp />
    </ProtocolProvider>
  );
}
```

## Protocol Data Structure

### Stain Protocol
```typescript
{
  id: string;                    // Auto-generated
  type: 'stain';
  name: string;
  description?: string;
  stainType: string;             // e.g., 'TDP-43', 'HE', 'Silver'
  antibody?: string;
  technique?: string;
  phosphoSpecific?: string;
  dilution?: string;
  vendor?: string;
  chromogen?: string;
  _isDefault?: boolean;          // Protected from deletion
}
```

### Region Protocol
```typescript
{
  id: string;                    // Auto-generated
  type: 'region';
  name: string;
  description?: string;
  regionType: string;            // e.g., 'hippocampus', 'cortex'
  landmarks?: string[];          // Sub-regions
  hemisphere?: string;           // 'left', 'right', 'unknown'
  sliceOrientation?: string;     // 'axial', 'coronal', 'sagittal'
  sliceThickness?: number;       // in microns
  _isDefault?: boolean;          // Protected from deletion
}
```

## Testing

The package includes comprehensive tests:

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# With UI
npm run test:ui

# With coverage
npm run test:coverage
```

## Architecture

### Components
- `ProtocolContext.jsx`: React Context for state management
- `protocolStorage.js`: Storage abstraction layer
- `ProtocolCard.jsx`: Individual protocol display
- `ProtocolList.jsx`: Protocol grid with actions
- `ProtocolModal.jsx`: Create/edit modal form

### Key Benefits
- **Single Source of Truth**: All protocol state in one place
- **No Manual Subscriptions**: React Context handles updates automatically
- **Type-Safe Filtering**: Automatic `stainProtocols` and `regionProtocols`
- **Protected Defaults**: IGNORE protocols can't be deleted
- **Persistent**: Automatic localStorage sync
- **Tested**: Comprehensive test coverage

## Migration from Old System

If you're migrating from a class-based store with manual subscriptions:

**Before:**
```jsx
import dataStore from './utils/dataStore';

function MyComponent() {
  const [protocols, setProtocols] = useState([]);

  useEffect(() => {
    const unsubscribe = dataStore.subscribe(() => {
      setProtocols(dataStore.getProtocols('stain'));
    });
    return unsubscribe;
  }, []);

  const handleAdd = (protocol) => {
    dataStore.addProtocol('stain', protocol);
  };
}
```

**After:**
```jsx
import { useProtocols } from '@bdsa/protocol-components';

function MyComponent() {
  const { stainProtocols, addProtocol } = useProtocols();

  const handleAdd = (protocol) => {
    addProtocol({ ...protocol, type: 'stain' });
  };
}
```

## When NOT to Use This Package

This package is designed for standalone protocol management without external syncing. **Do not use this package if:**

- You need DSA (Digital Slide Archive) integration and protocol syncing
- You need to track remote versions and local modifications
- You need protocol GUIDs managed by external systems
- You need custom protocol collection management

For DSA-integrated applications (like the wrangler app), keep using the custom `protocolStore` implementation.

## License

MIT
