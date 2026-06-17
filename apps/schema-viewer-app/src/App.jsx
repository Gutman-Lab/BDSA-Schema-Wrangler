import React, { useState } from 'react';
import SchemaViewer from '../../../packages/schema-components/src/SchemaViewer';
import FlattenedDataView from './components/FlattenedDataView';
import CdeReferenceView from './components/CdeReferenceView';
import './App.css';

const App = () => {
    const [activeSchema, setActiveSchema] = useState('clinical');

    const schemas = [
        { id: 'clinical', label: 'Clinical Schema', file: '/bdsa-schema.json', section: 'clinical' },
        { id: 'region', label: 'Region Schema', file: '/bdsa-schema.json', section: 'region' },
        { id: 'stain', label: 'Stain Schema', file: '/bdsa-schema.json', section: 'stain' },
        { id: 'bdsa', label: 'BDSA Schema', file: '/bdsa-schema.json', section: 'bdsa' },
        { id: 'flattened', label: 'Flattened View', file: '/bdsa-schema.json', section: 'flattened' },
        { id: 'cde-reference', label: 'CDE Reference', file: '/bdsa-schema.json', section: 'cde-reference' }
    ];

    return (
        <div className="app">
            <div className="app-header">
                <div className="header-left">
                    <img src="/BDSA_logo_clear.png" alt="BDSA Logo" className="logo" />
                    <div className="header-text">
                        <h1>BDSA Schema Viewer</h1>
                        <p>View and explore the JSON schemas used for data harmonization</p>
                    </div>
                </div>
                <div className="header-right">
                    <button
                        className="api-button"
                        onClick={() => window.open('/api/docs', '_blank')}
                        title="Open API Documentation"
                    >
                        📚 API Docs
                    </button>
                </div>
            </div>

            <div className="schema-navigation">
                {schemas.map(schema => (
                    <button
                        key={schema.id}
                        className={`schema-nav-button ${activeSchema === schema.id ? 'active' : ''}`}
                        onClick={() => setActiveSchema(schema.id)}
                    >
                        {schema.label}
                    </button>
                ))}
            </div>

            <div className="schema-content">
                {activeSchema === 'flattened' ? (
                    <FlattenedDataView
                        schemaFile={schemas.find(s => s.id === activeSchema)?.file}
                    />
                ) : activeSchema === 'cde-reference' ? (
                    <CdeReferenceView
                        schemaFile={schemas.find(s => s.id === activeSchema)?.file}
                    />
                ) : (
                    <SchemaViewer
                        schemaFile={schemas.find(s => s.id === activeSchema)?.file}
                        schemaType={activeSchema}
                        schemaSection={schemas.find(s => s.id === activeSchema)?.section}
                    />
                )}
            </div>
        </div>
    );
};

export default App;
