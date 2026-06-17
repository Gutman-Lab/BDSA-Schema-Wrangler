import React, { useState, useEffect } from 'react';
import SchemaViewer from '../../../../packages/schema-components/src/SchemaViewer';
import './SchemaTab.css';

const SchemaTab = () => {
    const [activeSchema, setActiveSchema] = useState('clinical');
    const [mainSchema, setMainSchema] = useState(null);
    const [loading, setLoading] = useState(true);

    const schemas = [
        { id: 'clinical', label: 'Clinical Schema', extractFrom: 'clinicalData' },
        { id: 'region', label: 'Region Schema', extractFrom: 'regionIDs' },
        { id: 'stain', label: 'Stain Schema', extractFrom: 'stainIDs' }
    ];

    useEffect(() => {
        loadMainSchema();
    }, []);

    const loadMainSchema = async () => {
        try {
            setLoading(true);
            const response = await fetch('/bdsa-schema.json');
            if (!response.ok) {
                throw new Error('Failed to load main BDSA schema');
            }
            const schema = await response.json();
            setMainSchema(schema);
        } catch (error) {
            console.error('Error loading main schema:', error);
        } finally {
            setLoading(false);
        }
    };

    const getExtractedSchema = () => {
        if (!mainSchema) return null;
        
        const currentSchema = schemas.find(s => s.id === activeSchema);
        if (!currentSchema) return null;

        const extractedData = mainSchema.properties?.[currentSchema.extractFrom];
        if (!extractedData) return null;

        // Create a standalone schema from the extracted part
        return {
            $schema: "https://json-schema.org/draft/2020-12/schema",
            title: currentSchema.label,
            type: extractedData.type || "object",
            properties: extractedData.properties || extractedData.items?.properties,
            required: extractedData.required || extractedData.items?.required,
            description: extractedData.description || `Extracted from main BDSA schema: ${currentSchema.extractFrom}`
        };
    };

    return (
        <div className="schema-tab">
            <div className="schema-header">
                <h2>BDSA Schema Documentation</h2>
                <p>View and explore the JSON schemas used for data harmonization</p>
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
                {loading ? (
                    <div className="schema-loading">Loading schema...</div>
                ) : (
                    <SchemaViewer
                        schemaData={getExtractedSchema()}
                        schemaType={activeSchema}
                    />
                )}
            </div>
        </div>
    );
};

export default SchemaTab;
