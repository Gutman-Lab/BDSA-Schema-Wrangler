# Changelog - @bdsa/protocol-components

## v1.0.0 - Initial Release

### Created
Complete protocol management package for BDSA applications.

### Features

#### State Management
- ✅ `ProtocolContext` - React Context for unified protocol state
- ✅ `useProtocols` hook - Easy access to protocols and operations
- ✅ Single source of truth for all protocol data
- ✅ Automatic filtering: `stainProtocols` and `regionProtocols`
- ✅ Protected default protocols (IGNORE)

#### Storage
- ✅ `LocalStorageProtocolStorage` - Browser localStorage persistence
- ✅ `InMemoryProtocolStorage` - In-memory backend for testing
- ✅ Storage abstraction layer for custom backends
- ✅ Automatic protocol ID generation

#### UI Components
- ✅ `ProtocolCard` - Display individual protocol details
- ✅ `ProtocolList` - Grid layout for multiple protocols with actions
- ✅ `ProtocolModal` - Create/edit modal form with validation
- ✅ Schema-driven validation support
- ✅ Dynamic field rendering based on protocol type

#### Testing
- ✅ Comprehensive test suite with Vitest
- ✅ React Testing Library for component tests
- ✅ 8 passing tests for context and state management
- ✅ Pre-commit hooks to prevent breaking changes

#### Documentation
- ✅ Complete README with usage examples
- ✅ EXAMPLE.md with full implementation examples
- ✅ ARCHITECTURE.md explaining design decisions
- ✅ API documentation for all exports

### Architecture Decisions

**Chose React Context over class-based store:**
- Simpler mental model
- No manual subscriptions needed
- Automatic re-renders
- Better integration with React hooks

**Separated from wrangler app:**
- Wrangler app needs DSA sync (complex, app-specific)
- Shared package is for simpler use cases
- Each serves its purpose well

**Storage abstraction:**
- Easy testing with in-memory backend
- Future-proof for API integration
- Pluggable architecture

### Breaking Changes from Old System

**Before (class-based store with subscriptions):**
```javascript
const unsubscribe = dataStore.subscribe(() => {
  setProtocols(dataStore.getProtocols('stain'));
});
dataStore.addProtocol('stain', protocol);
```

**After (Context + Hook):**
```javascript
const { stainProtocols, addProtocol } = useProtocols();
addProtocol({ ...protocol, type: 'stain' });
```

### Migration Guide

See README.md "Migration from Old System" section.

### Performance

- Storage operations are async (non-blocking)
- React Context prevents unnecessary re-renders via `useMemo`
- Callbacks are memoized with `useCallback`
- CSS is modular and scoped

### Browser Support

- Modern browsers with ES6+ support
- localStorage API required
- React 18+ required

### Dependencies

**Peer Dependencies:**
- react ^18.0.0
- react-dom ^18.0.0

**Dev Dependencies:**
- vitest ^1.0.4
- @testing-library/react ^14.0.0
- @testing-library/jest-dom ^6.1.5
- jsdom ^23.0.1

### Files

```
packages/protocol-components/
├── src/
│   ├── context/
│   │   ├── ProtocolContext.jsx        # State management
│   │   └── ProtocolContext.test.jsx   # Tests
│   ├── storage/
│   │   └── protocolStorage.js         # Storage layer
│   ├── components/
│   │   ├── ProtocolCard.jsx           # Display component
│   │   ├── ProtocolCard.css
│   │   ├── ProtocolList.jsx           # List component
│   │   ├── ProtocolList.css
│   │   ├── ProtocolModal.jsx          # Modal form
│   │   └── ProtocolModal.css
│   ├── index.ts                       # Exports
│   └── test-setup.js                  # Test config
├── vitest.config.js
├── package.json
├── README.md
├── EXAMPLE.md
├── ARCHITECTURE.md
└── CHANGELOG.md
```

### Known Limitations

1. **No DSA Integration**: Designed for standalone use
2. **No Undo/Redo**: Simple CRUD operations only
3. **No Search/Filter**: Provided via separate logic
4. **Basic Validation**: Schema validator is optional
5. **No Import/Export**: Future enhancement

### Future Enhancements (Maybe)

- Optimistic UI updates
- Protocol versioning
- Import/Export functionality
- Search and filtering
- Protocol templates
- Bulk operations

### Credits

Built as part of the BDSA Schema Wrangler monorepo to enable component reuse across BDSA applications.

---

## Release Notes

**Total Lines of Code:** ~1200
**Test Coverage:** 8 passing tests
**Bundle Size:** ~15KB (unminified)

Ready for use in any React 18+ application! 🚀

