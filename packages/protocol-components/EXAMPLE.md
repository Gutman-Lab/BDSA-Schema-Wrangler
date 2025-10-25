# Protocol Components Usage Examples

## Complete Protocol Management Example

This example shows how to use all the protocol components together for a full-featured protocol management UI:

```jsx
import React, { useState } from 'react';
import {
  ProtocolProvider,
  useProtocols,
  ProtocolList,
  ProtocolModal
} from '@bdsa/protocol-components';

// Your main app
function App() {
  return (
    <ProtocolProvider>
      <ProtocolManagementPage />
    </ProtocolProvider>
  );
}

// Protocol management page with tabs
function ProtocolManagementPage() {
  const [activeTab, setActiveTab] = useState('stain');

  return (
    <div className="protocols-page">
      <h1>Protocol Management</h1>
      
      <div className="tabs">
        <button
          className={activeTab === 'stain' ? 'active' : ''}
          onClick={() => setActiveTab('stain')}
        >
          Stain Protocols
        </button>
        <button
          className={activeTab === 'region' ? 'active' : ''}
          onClick={() => setActiveTab('region')}
        >
          Region Protocols
        </button>
      </div>

      {activeTab === 'stain' && <StainProtocolsTab />}
      {activeTab === 'region' && <RegionProtocolsTab />}
    </div>
  );
}

// Stain protocols tab
function StainProtocolsTab() {
  const { stainProtocols, addProtocol, updateProtocol, deleteProtocol } = useProtocols();
  const [showModal, setShowModal] = useState(false);
  const [editingProtocol, setEditingProtocol] = useState(null);

  const handleEdit = (protocol) => {
    setEditingProtocol(protocol);
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingProtocol(null);
    setShowModal(true);
  };

  const handleSave = async (formData) => {
    if (editingProtocol) {
      await updateProtocol(editingProtocol.id, formData);
    } else {
      await addProtocol({ ...formData, type: 'stain' });
    }
    setShowModal(false);
    setEditingProtocol(null);
  };

  const handleDelete = async (protocol) => {
    if (confirm(`Delete protocol "${protocol.name}"?`)) {
      await deleteProtocol(protocol.id);
    }
  };

  return (
    <div className="stain-protocols-tab">
      <div className="tab-header">
        <h2>Stain Protocols ({stainProtocols.length})</h2>
        <button onClick={handleAdd} className="add-button">
          + Add Stain Protocol
        </button>
      </div>

      <ProtocolList
        protocols={stainProtocols}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {showModal && (
        <ProtocolModal
          protocol={editingProtocol}
          type="stain"
          onSave={handleSave}
          onClose={() => {
            setShowModal(false);
            setEditingProtocol(null);
          }}
          // Optional: pass your schema validator for advanced validation
          // schemaValidator={mySchemaValidator}
        />
      )}
    </div>
  );
}

// Region protocols tab (similar structure)
function RegionProtocolsTab() {
  const { regionProtocols, addProtocol, updateProtocol, deleteProtocol } = useProtocols();
  const [showModal, setShowModal] = useState(false);
  const [editingProtocol, setEditingProtocol] = useState(null);

  const handleEdit = (protocol) => {
    setEditingProtocol(protocol);
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingProtocol(null);
    setShowModal(true);
  };

  const handleSave = async (formData) => {
    if (editingProtocol) {
      await updateProtocol(editingProtocol.id, formData);
    } else {
      await addProtocol({ ...formData, type: 'region' });
    }
    setShowModal(false);
    setEditingProtocol(null);
  };

  const handleDelete = async (protocol) => {
    if (confirm(`Delete protocol "${protocol.name}"?`)) {
      await deleteProtocol(protocol.id);
    }
  };

  return (
    <div className="region-protocols-tab">
      <div className="tab-header">
        <h2>Region Protocols ({regionProtocols.length})</h2>
        <button onClick={handleAdd} className="add-button">
          + Add Region Protocol
        </button>
      </div>

      <ProtocolList
        protocols={regionProtocols}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {showModal && (
        <ProtocolModal
          protocol={editingProtocol}
          type="region"
          onSave={handleSave}
          onClose={() => {
            setShowModal(false);
            setEditingProtocol(null);
          }}
        />
      )}
    </div>
  );
}

export default App;
```

## With Schema Validation

If you have a schema validator (like in the wrangler app):

```jsx
import schemaValidator from './utils/schemaValidator';
import { ProtocolModal } from '@bdsa/protocol-components';

function MyComponent() {
  const [showModal, setShowModal] = useState(false);

  // Load schema on mount
  useEffect(() => {
    schemaValidator.loadSchemas();
  }, []);

  return (
    <ProtocolModal
      protocol={null}
      type="stain"
      onSave={handleSave}
      onClose={() => setShowModal(false)}
      schemaValidator={schemaValidator}  // Enables advanced validation
    />
  );
}
```

## Individual Components

### Using ProtocolCard Alone

```jsx
import { ProtocolCard } from '@bdsa/protocol-components';

function ProtocolDetails() {
  const protocol = {
    id: 'abc123',
    type: 'stain',
    name: 'TDP-43 Protocol',
    description: 'Standard immunohistochemistry protocol',
    stainType: 'TDP-43',
    antibody: 'Mouse monoclonal',
    dilution: '1:1000'
  };

  return (
    <ProtocolCard
      protocol={protocol}
      onEdit={(p) => console.log('Edit', p)}
      onDelete={(p) => console.log('Delete', p)}
    />
  );
}
```

### Using Only the State Hook

If you want to build your own UI but use the state management:

```jsx
import { useProtocols } from '@bdsa/protocol-components';

function CustomProtocolUI() {
  const {
    protocols,
    stainProtocols,
    regionProtocols,
    addProtocol,
    updateProtocol,
    deleteProtocol,
    loading,
    error
  } = useProtocols();

  if (loading) return <div>Loading protocols...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>All Protocols</h2>
      <ul>
        {protocols.map(p => (
          <li key={p.id}>
            {p.name} ({p.type})
            <button onClick={() => deleteProtocol(p.id)}>Delete</button>
          </li>
        ))}
      </ul>

      <button onClick={() => addProtocol({
        type: 'stain',
        name: 'New Protocol',
        stainType: 'HE'
      })}>
        Add H&E Protocol
      </button>
    </div>
  );
}
```

## CSS Styling

The components come with default styles. You can:

1. **Use default styles** (automatically imported)
2. **Override with your own CSS**:

```css
/* Override card styles */
.protocol-card {
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Override modal styles */
.protocol-modal-content {
  max-width: 800px;
}

/* Customize button colors */
.protocol-modal-save-button {
  background: #00a86b;
}
```

## Advanced: Custom Storage Backend

Replace localStorage with your own backend:

```jsx
import { ProtocolProvider } from '@bdsa/protocol-components';

class APIStorage {
  async load() {
    const response = await fetch('/api/protocols');
    return await response.json();
  }

  async save(protocols) {
    await fetch('/api/protocols', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(protocols)
    });
  }
}

function App() {
  return (
    <ProtocolProvider storage={new APIStorage()}>
      <YourApp />
    </ProtocolProvider>
  );
}
```

## Testing Your Components

```jsx
import { render, screen } from '@testing-library/react';
import { ProtocolProvider, InMemoryProtocolStorage } from '@bdsa/protocol-components';

test('shows protocols', () => {
  const storage = new InMemoryProtocolStorage([
    { id: '1', type: 'stain', name: 'Test Protocol' }
  ]);

  render(
    <ProtocolProvider storage={storage}>
      <MyProtocolComponent />
    </ProtocolProvider>
  );

  expect(screen.getByText('Test Protocol')).toBeInTheDocument();
});
```
