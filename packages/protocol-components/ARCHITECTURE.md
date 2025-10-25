# Protocol Components Architecture

## Design Decisions

### Why This Package Exists

The `@bdsa/protocol-components` package was created to provide **simple, reusable protocol management** for BDSA applications that don't require complex external synchronization.

### Target Use Cases

✅ **Use this package when:**
- Building new BDSA applications
- Need local protocol storage (localStorage)
- Want React Context-based state management
- Need basic CRUD operations for protocols
- Want tested, ready-to-use UI components

❌ **Don't use this package when:**
- You need DSA (Digital Slide Archive) integration
- You need protocol syncing with remote servers
- You need to track protocol versions and modifications
- You need GUID-based protocol IDs managed externally
- You need collection-aware protocol management

### Comparison with Wrangler App

The **wrangler app** uses a custom `protocolStore.js` implementation because it requires:

1. **DSA Integration**
   - Syncs protocols with DSA server
   - Tracks remote versions (`_remoteVersion`)
   - Shows sync status (local, synced, modified)
   
2. **Collection-Aware State**
   - Protocols are scoped to DSA collections
   - Switch between collections seamlessly
   - Multiple protocol sets per user

3. **Advanced Tracking**
   - GUIDs from DSA
   - Local modification flags (`_localModified`)
   - Sync timestamps
   - Conflict resolution

The **shared package** provides:

1. **Simple State Management**
   - React Context + Hook
   - Single protocol list
   - localStorage persistence
   
2. **Basic UI Components**
   - Protocol cards
   - Protocol lists
   - Create/Edit modal

3. **No External Dependencies**
   - No DSA integration
   - No server syncing
   - Self-contained

## Architecture

### State Flow

```
┌─────────────────────┐
│  ProtocolProvider   │  ← React Context
│  (Context)          │
└──────────┬──────────┘
           │
           ├─► useState (protocols)
           ├─► useEffect (load from storage)
           └─► callbacks (add, update, delete)
                    │
                    ▼
         ┌──────────────────────┐
         │  protocolStorage.js  │  ← Storage Layer
         │  - localStorage      │
         │  - InMemory (tests)  │
         └──────────────────────┘
```

### Component Hierarchy

```
App
└── ProtocolProvider
    ├── useProtocols()  ← Hook
    │
    ├── ProtocolList
    │   └── ProtocolCard (multiple)
    │
    └── ProtocolModal
        └── Form Fields
```

### Storage Abstraction

The storage layer is abstracted to support different backends:

```javascript
class ProtocolStorage {
  async load() { /* return protocols array */ }
  async save(protocols) { /* persist protocols */ }
}
```

- `LocalStorageProtocolStorage` - Browser localStorage (default)
- `InMemoryProtocolStorage` - In-memory (for tests)
- Custom implementations - API backends, IndexedDB, etc.

## Migration Path (If Needed)

If the wrangler app eventually needs to adopt this package, here's how:

### Phase 1: Extract DSA Logic
1. Keep `protocolStore.js` for DSA sync
2. Create an adapter that implements `ProtocolStorage` interface
3. Wrapper around DSA API calls

### Phase 2: UI Migration
1. Replace custom `ProtocolList` with shared component
2. Add DSA-specific rendering (sync badges, etc.) via props
3. Keep `ProtocolModal` with `schemaValidator` prop

### Phase 3: State Migration
1. Move from class-based store to Context
2. DSA sync as separate module
3. Hook-based state access

**Current Decision**: Keep wrangler app as-is. The custom implementation is justified by its complex requirements.

## Future Enhancements

Potential additions without breaking simplicity:

1. **Optimistic Updates**: UI updates before storage confirms
2. **Undo/Redo**: Protocol edit history
3. **Import/Export**: JSON protocol exchange
4. **Validation Schemas**: JSON Schema for protocol validation
5. **Search/Filter**: Protocol search and filtering
6. **Tags/Categories**: Group protocols by tags

## Key Benefits of Current Design

1. **Simple to Understand**: React Context + Hook pattern
2. **Easy to Test**: Storage abstraction, in-memory backend
3. **No Lock-in**: Replace storage backend easily
4. **Type-Safe Filters**: Automatic `stainProtocols` / `regionProtocols`
5. **Protected Defaults**: IGNORE protocols can't be deleted
6. **Self-Contained**: No external dependencies

## Lessons Learned

1. **Don't Over-Abstract**: The wrangler app's needs are legitimately different
2. **Storage Matters**: Abstracting storage early enables testing
3. **Context > Classes**: React Context is simpler than class-based stores with subscriptions
4. **UI Composition**: Small components (Card, List, Modal) are more flexible than one big component
5. **Tests First**: Writing tests revealed the need for `InMemoryProtocolStorage`

## Related Files

- `src/context/ProtocolContext.jsx` - Main state management
- `src/storage/protocolStorage.js` - Storage abstraction
- `src/components/ProtocolCard.jsx` - Protocol display
- `src/components/ProtocolList.jsx` - Protocol grid
- `src/components/ProtocolModal.jsx` - Create/Edit form
- `src/context/ProtocolContext.test.jsx` - Tests

## Questions?

See `README.md` for usage examples and API documentation.
See `EXAMPLE.md` for complete code examples.

