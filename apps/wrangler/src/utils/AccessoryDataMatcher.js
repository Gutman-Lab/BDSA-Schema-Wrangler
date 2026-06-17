// AccessoryDataMatcher - Handles loading and matching accessory metadata files with primary data

import * as XLSX from 'xlsx';

class AccessoryDataMatcher {
    constructor() {
        // This class is stateless
    }

    async loadAccessoryFile(file, dataStoreInstance, csvLoader) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                try {
                    let accessoryData;

                    if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                        // Handle CSV file
                        const csvText = e.target.result;
                        accessoryData = csvLoader.parseCsv(csvText, file.name);
                    } else {
                        // Handle Excel file
                        const data = e.target.result;
                        const workbook = XLSX.read(data, { type: 'binary' });
                        const worksheet = workbook.Sheets[workbook.SheetNames[0]];
                        accessoryData = XLSX.utils.sheet_to_json(worksheet);
                    }

                    if (!accessoryData || accessoryData.length === 0) {
                        throw new Error('Accessory file is empty or could not be parsed');
                    }

                    // Match accessory data with existing DSA data based on filename
                    const matchedData = this.matchAccessoryData(accessoryData, dataStoreInstance);

                    resolve({
                        success: true,
                        itemCount: accessoryData.length,
                        matchedCount: matchedData.matchedCount,
                        data: accessoryData,
                        matchedData: matchedData.matchedData,
                        message: `Successfully loaded ${accessoryData.length} accessory items, matched ${matchedData.matchedCount} with DSA data`
                    });
                } catch (error) {
                    reject(new Error(`Failed to parse accessory file: ${error.message}`));
                }
            };

            reader.onerror = () => {
                reject(new Error('Failed to read accessory file'));
            };

            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                reader.readAsText(file);
            } else {
                reader.readAsBinaryString(file);
            }
        });
    }

    matchAccessoryData(accessoryData, dataStoreInstance) {
        if (!dataStoreInstance.processedData || dataStoreInstance.processedData.length === 0) {
            return { matchedData: [], matchedCount: 0 };
        }

        const matchedData = [];
        let matchedCount = 0;

        // Create a map of DSA filenames for quick lookup
        const dsaFilenameMap = new Map();
        dataStoreInstance.processedData.forEach((item, index) => {
            const filename = item.name || item.dsa_name || '';
            if (filename) {
                // Store both exact match and normalized versions
                dsaFilenameMap.set(filename, { item, index });
                dsaFilenameMap.set(filename.toLowerCase(), { item, index });

                // Also try without extension
                const nameWithoutExt = filename.replace(/\.[^/.]+$/, '');
                dsaFilenameMap.set(nameWithoutExt, { item, index });
                dsaFilenameMap.set(nameWithoutExt.toLowerCase(), { item, index });
            }
        });

        // Try to match each accessory item
        accessoryData.forEach((accessoryItem, accessoryIndex) => {
            let matched = false;
            let dsaItem = null; // Declare dsaItem at the top of the loop scope

            // Look for filename field in accessory data (could be 'new_filename', 'filename', 'name', etc.)
            const possibleFilenameFields = ['new_filename', 'filename', 'name', 'file_name', 'image_name', 'FileName', 'Filename', 'ImageName'];
            let accessoryFilename = '';

            for (const field of possibleFilenameFields) {
                if (accessoryItem[field]) {
                    accessoryFilename = accessoryItem[field];
                    console.log(`🔍 Found filename in field "${field}": ${accessoryFilename}`);
                    break;
                }
            }

            // If no match found, try case-insensitive search through all fields
            if (!accessoryFilename) {
                const allKeys = Object.keys(accessoryItem);
                for (const key of allKeys) {
                    if (key.toLowerCase().includes('filename') || key.toLowerCase().includes('name')) {
                        accessoryFilename = accessoryItem[key];
                        console.log(`🔍 Found filename in field "${key}" (case-insensitive): ${accessoryFilename}`);
                        break;
                    }
                }
            }

            if (accessoryFilename) {
                // Try exact match first
                dsaItem = dsaFilenameMap.get(accessoryFilename);

                if (!dsaItem) {
                    // Try case-insensitive match
                    dsaItem = dsaFilenameMap.get(accessoryFilename.toLowerCase());
                }

                if (!dsaItem) {
                    // Try without extension
                    const nameWithoutExt = accessoryFilename.replace(/\.[^/.]+$/, '');
                    dsaItem = dsaFilenameMap.get(nameWithoutExt);
                    if (!dsaItem) {
                        dsaItem = dsaFilenameMap.get(nameWithoutExt.toLowerCase());
                    }
                }

                if (dsaItem) {
                    // Add accessory data as temporary fields to the DSA item
                    if (!dsaItem.item.accessoryData) {
                        dsaItem.item.accessoryData = {};
                    }

                    // Add all accessory fields with a prefix to avoid conflicts
                    // Skip filename fields, BDSA fields, and other internal fields
                    Object.keys(accessoryItem).forEach(key => {
                        // Skip filename fields
                        if (key === 'new_filename' || key === 'filename' || key === 'name') {
                            return;
                        }

                        // Skip BDSA fields (these are app-internal, not from the original accessory file)
                        if (key === 'BDSA' || key.startsWith('BDSA.')) {
                            console.log(`⚠️ Skipping internal BDSA field from accessory item: ${key}`);
                            return;
                        }

                        // Skip internal fields
                        if (key.startsWith('_')) {
                            return;
                        }

                        dsaItem.item.accessoryData[`accessory_${key}`] = accessoryItem[key];
                    });

                    // Mark the item as modified
                    dataStoreInstance.modifiedItems.add(dsaItem.item.id || dsaItem.index);
                    matched = true;
                    matchedCount++;
                }
            }

            matchedData.push({
                accessoryIndex,
                accessoryItem,
                matched,
                dsaItem: matched ? dsaItem : null
            });
        });

        // Save changes and notify listeners
        // Skip saveToStorage() for large datasets to avoid quota errors
        // dataStoreInstance.saveToStorage();
        dataStoreInstance.notify();

        console.log(`🔗 Accessory data matching complete: ${matchedCount}/${accessoryData.length} items matched with DSA data`);

        return { matchedData, matchedCount, itemCount: accessoryData.length };
    }

    retryAccessoryMatching(accessoryData, filenameField, dataStoreInstance) {
        if (!dataStoreInstance.processedData || dataStoreInstance.processedData.length === 0) {
            return { matchedData: [], matchedCount: 0, itemCount: accessoryData.length };
        }

        const matchedData = [];
        let matchedCount = 0;

        // Create a map of DSA filenames for quick lookup
        const dsaFilenameMap = new Map();
        dataStoreInstance.processedData.forEach((item, index) => {
            const filename = item.name || item.dsa_name || '';
            if (filename) {
                // Store both exact match and normalized versions
                dsaFilenameMap.set(filename, { item, index });
                dsaFilenameMap.set(filename.toLowerCase(), { item, index });

                // Also try without extension
                const nameWithoutExt = filename.replace(/\.[^/.]+$/, '');
                dsaFilenameMap.set(nameWithoutExt, { item, index });
                dsaFilenameMap.set(nameWithoutExt.toLowerCase(), { item, index });
            }
        });

        // Try to match each accessory item using the specified filename field
        accessoryData.forEach((accessoryItem, accessoryIndex) => {
            let matched = false;
            let dsaItem = null;

            const accessoryFilename = accessoryItem[filenameField];

            if (accessoryFilename) {
                // Try exact match first
                dsaItem = dsaFilenameMap.get(accessoryFilename);

                if (!dsaItem) {
                    // Try case-insensitive match
                    dsaItem = dsaFilenameMap.get(accessoryFilename.toLowerCase());
                }

                if (!dsaItem) {
                    // Try without extension
                    const nameWithoutExt = accessoryFilename.replace(/\.[^/.]+$/, '');
                    dsaItem = dsaFilenameMap.get(nameWithoutExt);
                    if (!dsaItem) {
                        dsaItem = dsaFilenameMap.get(nameWithoutExt.toLowerCase());
                    }
                }

                if (dsaItem) {
                    // Add accessory data as temporary fields to the DSA item
                    if (!dsaItem.item.accessoryData) {
                        dsaItem.item.accessoryData = {};
                    }

                    // Add all accessory fields with a prefix to avoid conflicts
                    Object.keys(accessoryItem).forEach(key => {
                        if (key !== filenameField) {
                            dsaItem.item.accessoryData[`accessory_${key}`] = accessoryItem[key];
                        }
                    });

                    // Mark the item as modified
                    dataStoreInstance.modifiedItems.add(dsaItem.item.id || dsaItem.index);
                    matched = true;
                    matchedCount++;
                }
            }

            matchedData.push({
                accessoryIndex,
                accessoryItem,
                matched,
                dsaItem: matched ? dsaItem : null
            });
        });

        // Save changes and notify listeners
        // Skip saveToStorage() for large datasets to avoid quota errors
        // dataStoreInstance.saveToStorage();
        dataStoreInstance.notify();

        console.log(`🔗 Retry matching complete: ${matchedCount}/${accessoryData.length} items matched using field "${filenameField}"`);

        return { matchedData, matchedCount, itemCount: accessoryData.length };
    }
}

const accessoryDataMatcher = new AccessoryDataMatcher();
export default accessoryDataMatcher;
