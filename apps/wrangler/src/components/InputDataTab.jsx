import React, { useState, useEffect } from 'react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import dataStore, { getItemsToSyncCount } from '../utils/dataStore';
import dsaAuthStore from '../utils/dsaAuthStore';
import RegexRulesModal from './RegexRulesModal';
import BdsaMappingModal from './BdsaMappingModal';
import DsaSyncModal from './DsaSyncModal';
import ExcelSheetSelectionModal from './ExcelSheetSelectionModal';
import AccessoryFieldMappingModal from './AccessoryFieldMappingModal';
import StatusCellRenderer from './StatusCellRenderer';
import DataControlsToolbar from './DataControlsToolbar';
import DataGrid from './DataGrid';
import ColumnVisibilityModal from './ColumnVisibilityModal';
import ProtocolArrayCellRenderer from './ProtocolArrayCellRenderer';
import NameCellRenderer from './NameCellRenderer';
import { getDefaultRegexRules, applyRegexRules } from '../utils/regexExtractor';
import { HIDDEN_DSA_FIELDS, PRIORITY_BDSA_FIELDS, DEFAULT_COLUMN_VISIBILITY, DATA_SOURCE_TYPES } from '../utils/constants';
import { generateColumnDefinitions, getColumnDisplayName, generateNestedKeys } from '../utils/columnDefinitionGenerator';
import { useColumnVisibility } from '../hooks/useColumnVisibility';
import './InputDataTab.css';



const InputDataTab = () => {
    const [dataSource, setDataSource] = useState(DATA_SOURCE_TYPES.DSA);
    const [dataStatus, setDataStatus] = useState(dataStore.getStatus());
    const [authStatus, setAuthStatus] = useState(dsaAuthStore.getStatus());
    const [isLoading, setIsLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState('');
    const [error, setError] = useState(null);
    const [csvFile, setCsvFile] = useState(null);
    const [excelFile, setExcelFile] = useState(null);
    const [accessoryFile, setAccessoryFile] = useState(null);
    const [showExcelSheetModal, setShowExcelSheetModal] = useState(false);
    const [excelSheetNames, setExcelSheetNames] = useState([]);
    const [accessoryData, setAccessoryData] = useState(null);
    const [accessoryMatchInfo, setAccessoryMatchInfo] = useState(null);
    const [showAccessoryFieldMapping, setShowAccessoryFieldMapping] = useState(false);
    const [accessoryFilenameField, setAccessoryFilenameField] = useState('');
    // Column visibility management
    const {
        showColumnPanel,
        setShowColumnPanel,
        columnVisibility,
        columnOrder,
        toggleColumnVisibility,
        showAllColumns,
        hideAllColumns,
        moveColumn,
        resetColumnOrder
    } = useColumnVisibility(dataStatus);
    const [showRegexRules, setShowRegexRules] = useState(false);
    const [regexRules, setRegexRules] = useState(() => {
        // Load saved regex rules from localStorage
        const savedRules = localStorage.getItem('regexRules');
        if (savedRules) {
            try {
                return JSON.parse(savedRules);
            } catch (error) {
                console.error('Error loading saved regex rules:', error);
            }
        }
        return getDefaultRegexRules();
    });
    const [selectedRuleSet, setSelectedRuleSet] = useState(() => {
        // Load saved rule set from localStorage
        return localStorage.getItem('selectedRegexRuleSet') || '';
    });
    const [showBdsaMapping, setShowBdsaMapping] = useState(false);
    const [columnMappings, setColumnMappings] = useState(() => {
        // Load saved column mappings from localStorage
        const savedMappings = localStorage.getItem('columnMappings');
        if (savedMappings) {
            try {
                return JSON.parse(savedMappings);
            } catch (error) {
                console.error('Error loading saved column mappings:', error);
            }
        }
        return {
            localCaseId: '',
            localStainID: '',
            localRegionId: '',
            localImageType: ''
        };
    });
    const [showDsaSync, setShowDsaSync] = useState(false);
    const [isDataRefresh, setIsDataRefresh] = useState(false);
    const [hasAppliedInitialRegex, setHasAppliedInitialRegex] = useState(false);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [loadMoreProgress, setLoadMoreProgress] = useState({ current: 0, total: 0 });
    const [modifiedItemsCount, setModifiedItemsCount] = useState(0);
    const [hasMoreData, setHasMoreData] = useState(true); // Track if there's more data to load
    const [hasCheckedForMoreData, setHasCheckedForMoreData] = useState(false); // Track if we've determined there's no more data
    const [showFileFilterNotification, setShowFileFilterNotification] = useState(false);
    const [isNotificationFading, setIsNotificationFading] = useState(false);

    // Generate nested keys from an object (excluding meta.bdsaLocal fields)

    // Generate a unique key for the current data source

    // Load column configuration from localStorage

    useEffect(() => {
        const unsubscribeData = dataStore.subscribe(() => {
            const newStatus = dataStore.getStatus();
            console.log('🔄 InputDataTab received data update:', {
                processedDataLength: newStatus.processedData?.length || 0,
                dataSource: newStatus.dataSource,
                hasData: !!newStatus.processedData,
                dataType: typeof newStatus.processedData
            });
            setDataStatus(newStatus);

            // Update modified items count separately (using accurate count method)
            const newModifiedCount = dataStore.getModifiedItemsCount();
            console.log(`🔍 Updating modified items count: ${modifiedItemsCount} → ${newModifiedCount}`);
            console.log(`🔍 Current modifiedItems Set:`, Array.from(dataStore.modifiedItems));
            console.log(`🔍 Current modifiedItems Set size:`, dataStore.modifiedItems.size);
            console.log(`🔍 Setting modifiedItemsCount state to: ${newModifiedCount}`);

            // Force update if there's a mismatch
            if (newModifiedCount !== modifiedItemsCount) {
                console.log(`🔍 FORCE UPDATE: Count changed from ${modifiedItemsCount} to ${newModifiedCount}`);
                setModifiedItemsCount(newModifiedCount);
            }

            // Column loading is now handled in a separate useEffect
        });

        const unsubscribeAuth = dsaAuthStore.subscribe(() => {
            setAuthStatus(dsaAuthStore.getStatus());
        });

        return () => {
            unsubscribeData();
            unsubscribeAuth();
        };
    }, []);

    // Separate effect to watch for modifiedItems changes specifically
    useEffect(() => {
        const checkModifiedItems = () => {
            const currentCount = dataStore.getModifiedItemsCount();
            console.log(`🔍 MODIFIED ITEMS CHECK: Current count = ${currentCount}, State = ${modifiedItemsCount}`);
            if (currentCount !== modifiedItemsCount) {
                console.log(`🔍 MODIFIED ITEMS MISMATCH: Updating state from ${modifiedItemsCount} to ${currentCount}`);
                setModifiedItemsCount(currentCount);
            }
        };

        // Check immediately
        checkModifiedItems();

        // Set up interval to check periodically (as fallback)
        const interval = setInterval(checkModifiedItems, 1000);

        return () => clearInterval(interval);
    }, [modifiedItemsCount]);

    // Note: hasMoreData is now managed by the API responses from loadDsaData and loadMoreDsaData
    // No need for heuristic-based logic here

    // Auto-dismiss file filter notification
    useEffect(() => {
        if (window.dsaSkipStats && window.dsaSkipStats.totalSkipped > 0) {
            setShowFileFilterNotification(true);
            setIsNotificationFading(false);

            // Start fade-out after 4 seconds, then hide after 5 seconds
            const fadeTimer = setTimeout(() => {
                setIsNotificationFading(true);
            }, 4000);

            const hideTimer = setTimeout(() => {
                setShowFileFilterNotification(false);
                setIsNotificationFading(false);
                // Also clear the global stats to prevent re-showing
                window.dsaSkipStats = null;
            }, 5000);

            return () => {
                clearTimeout(fadeTimer);
                clearTimeout(hideTimer);
            };
        }
    }, [window.dsaSkipStats?.totalSkipped]);

    // Auto-apply regex rules when data is loaded (if no column mappings exist)
    // Only run this once when data is first loaded, not on every data change
    useEffect(() => {
        // Check if this is data loaded from localStorage (page refresh scenario)
        // If data exists but we haven't explicitly refreshed, it's likely from localStorage
        const isLoadedFromStorage = dataStatus.processedData && dataStatus.processedData.length > 0 &&
            !isDataRefresh && hasAppliedInitialRegex;

        console.log('🔍 Auto-apply useEffect triggered:', {
            hasData: dataStatus.processedData && dataStatus.processedData.length > 0,
            dataLength: dataStatus.processedData?.length || 0,
            isDataRefresh,
            isLoadedFromStorage,
            hasAppliedInitialRegex,
            dataLoadTimestamp: dataStatus.dataLoadTimestamp,
            shouldRun: dataStatus.processedData && dataStatus.processedData.length > 0 && !isDataRefresh && !isLoadedFromStorage && !hasAppliedInitialRegex
        });

        // TEMPORARILY DISABLED: Auto-apply logic is marking all items as modified on page refresh
        // TODO: Fix the isLoadedFromStorage detection logic
        if (false && dataStatus.processedData && dataStatus.processedData.length > 0 && !isDataRefresh && !isLoadedFromStorage && !hasAppliedInitialRegex) {
            // Check which fields need regex extraction on a per-field basis
            const fieldsNeedingExtraction = {
                localCaseId: 0,
                localStainID: 0,
                localRegionId: 0
            };

            dataStatus.processedData.forEach(item => {
                const bdsaLocal = item.BDSA?.bdsaLocal;
                if (!bdsaLocal) return;

                // Count items missing each field
                if (!bdsaLocal.localCaseId || bdsaLocal.localCaseId.trim() === '') {
                    fieldsNeedingExtraction.localCaseId++;
                }
                if (!bdsaLocal.localStainID || bdsaLocal.localStainID.trim() === '') {
                    fieldsNeedingExtraction.localStainID++;
                }
                if (!bdsaLocal.localRegionId || bdsaLocal.localRegionId.trim() === '') {
                    fieldsNeedingExtraction.localRegionId++;
                }
            });

            // If any fields need extraction, apply regex rules
            const totalNeedingExtraction = Object.values(fieldsNeedingExtraction).reduce((sum, count) => sum + count, 0);

            console.log(`🔍 Fields needing extraction:`, fieldsNeedingExtraction, `Total: ${totalNeedingExtraction}`);

            if (totalNeedingExtraction > 0) {
                console.log(`🔄 Found items needing regex extraction:`, fieldsNeedingExtraction);
                console.log(`🔄 Auto-applying regex rules to extract missing field values...`);
                // Don't mark items as modified during data refresh or page refresh - only mark as modified for initial load
                const shouldMarkAsModified = !isDataRefresh && !isLoadedFromStorage;
                const result = dataStore.applyRegexRules(regexRules, shouldMarkAsModified);
                if (result.success) {
                    const action = shouldMarkAsModified ? 'marked as modified for sync' : 'extracted (not marked as modified - data refresh)';
                    console.log(`✅ Auto-applied regex rules: ${result.extractedCount} items updated (${action})`);
                    console.log(`📊 Modified items count after regex: ${dataStore.modifiedItems.size}`);
                }
            } else {
                console.log('🔄 All items already have BDSA field values, skipping auto-apply of regex rules');
            }

            // Also auto-apply column mappings if they exist
            if (columnMappings && (columnMappings.localCaseId || columnMappings.localStainID || columnMappings.localRegionId)) {
                console.log(`🔄 Auto-applying column mappings:`, columnMappings);
                // Don't mark items as modified during data refresh or page refresh - only mark as modified for initial load
                const shouldMarkAsModified = !isDataRefresh && !isLoadedFromStorage;
                const mappingResult = dataStore.applyColumnMappings(columnMappings, shouldMarkAsModified);
                if (mappingResult.success) {
                    const action = shouldMarkAsModified ? 'updated' : 'mapped (not marked as modified - data refresh)';
                    console.log(`✅ Auto-applied column mappings: ${mappingResult.updatedCount} items ${action}`);
                    console.log(`📊 Modified items count after column mappings: ${dataStore.modifiedItems.size}`);
                }
            } else {
                console.log(`🔄 No column mappings to auto-apply:`, columnMappings);
            }

            // Mark that we've applied initial regex to prevent infinite loop
            setHasAppliedInitialRegex(true);

            // Debug: Check final modified items count
            console.log(`📊 Final modified items count after auto-apply: ${dataStore.modifiedItems.size}`);
        }
    }, [dataStatus.processedData, dataStatus.dataSource, isDataRefresh, hasAppliedInitialRegex]); // Removed regexRules from dependencies

    // Auto-load DSA data when authenticated and no data is loaded
    useEffect(() => {
        if (authStatus.isAuthenticated &&
            dataSource === DATA_SOURCE_TYPES.DSA &&
            (!dataStatus.processedData || dataStatus.processedData.length === 0) &&
            !isLoading) {
            console.log('🚀 Auto-loading DSA data...');
            handleLoadDsa();
        }
    }, [authStatus.isAuthenticated, dataSource, dataStatus.processedData, isLoading]);

    // Auto-refresh DSA data when resource ID changes
    useEffect(() => {
        if (authStatus.isAuthenticated &&
            dataSource === DATA_SOURCE_TYPES.DSA &&
            authStatus.resourceId &&
            dataStatus.processedData &&
            dataStatus.processedData.length > 0 &&
            !isLoading) {
            // Check if the resource ID has changed by comparing with stored data source info
            const currentResourceId = dataStatus.dataSourceInfo?.resourceId;
            if (currentResourceId && currentResourceId !== authStatus.resourceId) {
                console.log('🔄 DSA resource changed, auto-refreshing data...');
                console.log(`Previous resource: ${currentResourceId}, New resource: ${authStatus.resourceId}`);
                handleLoadDsa();
            }
        }
    }, [authStatus.resourceId, authStatus.isAuthenticated, dataSource, dataStatus.processedData, dataStatus.dataSourceInfo, isLoading]);

    const handleDataSourceChange = (newDataSource) => {
        setDataSource(newDataSource);
        setError(null);

        // Clear data when switching data sources
        if (newDataSource !== dataStatus.dataSource) {
            dataStore.clearData();
            setHasAppliedInitialRegex(false); // Reset regex flag when clearing data
        }
    };

    const handleCsvFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            setCsvFile(file);
            setError(null);
        } else {
            setError('Please select a valid CSV file');
            setCsvFile(null);
        }
    };

    const handleLoadCsv = async () => {
        if (!csvFile) {
            setError('Please select a CSV file first');
            return;
        }

        setIsLoading(true);
        setLoadingMessage('Loading CSV file...');
        setError(null);

        try {
            const result = await dataStore.loadCsvData(csvFile);
            if (result.success) {
                console.log(`✅ Successfully loaded ${result.itemCount} items from CSV`);
            }
        } catch (error) {
            console.error('Error loading CSV:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
            setLoadingMessage('');
        }
    };

    const handleExcelFileChange = (event) => {
        const file = event.target.files[0];
        if (file && (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
            file.type === 'application/vnd.ms-excel' ||
            file.name.endsWith('.xlsx') ||
            file.name.endsWith('.xls'))) {
            setExcelFile(file);
            setError(null);
        } else {
            setError('Please select a valid Excel file (.xlsx or .xls)');
            setExcelFile(null);
        }
    };

    const handleLoadExcel = async () => {
        if (!excelFile) {
            setError('Please select an Excel file first');
            return;
        }

        setIsLoading(true);
        setLoadingMessage('Reading Excel file...');
        setError(null);

        try {
            // First, get the sheet names
            const sheetNames = await dataStore.getExcelSheetNames(excelFile);

            if (sheetNames.length === 1) {
                // Only one sheet, load it directly
                const result = await dataStore.loadExcelData(excelFile, sheetNames[0]);
                if (result.success) {
                    console.log(`✅ Successfully loaded ${result.itemCount} items from Excel`);
                }
            } else {
                // Multiple sheets, show selection modal
                setExcelSheetNames(sheetNames);
                setShowExcelSheetModal(true);
            }
        } catch (error) {
            console.error('Error loading Excel:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
            setLoadingMessage('');
        }
    };

    const handleSheetSelect = async (sheetName) => {
        setIsLoading(true);
        setLoadingMessage(`Loading sheet "${sheetName}"...`);
        setError(null);

        try {
            const result = await dataStore.loadExcelData(excelFile, sheetName);
            if (result.success) {
                console.log(`✅ Successfully loaded ${result.itemCount} items from Excel sheet "${sheetName}"`);
            }
        } catch (error) {
            console.error('Error loading Excel sheet:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
            setLoadingMessage('');
        }
    };

    const handleLoadDsa = async () => {
        if (!authStatus.isAuthenticated) {
            setError('Please login to DSA server first');
            return;
        }

        if (!authStatus.resourceId) {
            setError('Please configure a Resource ID first. Go to the DSA configuration and select a folder or collection.');
            return;
        }

        // Check if this is a refresh (data already exists from same source)
        const isRefresh = dataStatus.processedData && dataStatus.processedData.length > 0 &&
            dataStatus.dataSource === 'dsa';
        setIsDataRefresh(isRefresh);

        // If this is a refresh, clear modified items since we're reloading fresh data
        if (isRefresh) {
            console.log('🔄 Data refresh detected - clearing modified items count');
            dataStore.clearModifiedItems();
        }

        setIsLoading(true);
        setLoadingMessage('Loading data from DSA server...');
        setError(null);

        try {
            const result = await dataStore.loadDsaData(dsaAuthStore);
            if (result.success) {
                console.log(`✅ Successfully loaded ${result.itemCount} items from DSA`);

                // Use the hasMoreData information from the API response
                if (result.hasMoreData !== undefined) {
                    setHasMoreData(result.hasMoreData);
                    console.log(`🔍 DEBUG: hasMoreData set to: ${result.hasMoreData} (from API response)`);
                } else {
                    // Fallback: Check if we got a full page of data to determine if there might be more
                    const itemCount = result.itemCount || 0;
                    // If we got exactly 100 items (page size), there might be more. If less, we've reached the end.
                    const mightHaveMore = itemCount >= 100;
                    console.log(`🔍 DEBUG: Loaded ${itemCount} items, setting hasMoreData to ${mightHaveMore} (fallback logic)`);
                    setHasMoreData(mightHaveMore);
                }

                // Check for file filtering stats
                if (window.dsaSkipStats && window.dsaSkipStats.totalSkipped > 0) {
                    console.log('📁 File filtering applied:', window.dsaSkipStats);
                }

                // Auto-pull regex rules from DSA server if available
                const config = dsaAuthStore.getConfig();
                // Use metadataSyncTargetFolder if set, otherwise fall back to resourceId
                const metadataTargetFolder = config.metadataSyncTargetFolder && config.metadataSyncTargetFolder.trim()
                    ? config.metadataSyncTargetFolder.trim()
                    : config.resourceId;

                try {
                    const { getRegexRulesFromFolder } = await import('../utils/dsaIntegration.js');

                    const regexResult = await getRegexRulesFromFolder(
                        config.baseUrl,
                        metadataTargetFolder,
                        dsaAuthStore.getToken()
                    );

                    if (regexResult.success && regexResult.regexRules) {
                        const pulledRules = regexResult.regexRules.rules;
                        const pulledRuleSetName = regexResult.regexRules.ruleSetName || '';

                        // Auto-apply pulled regex rules
                        setRegexRules(pulledRules);
                        setSelectedRuleSet(pulledRuleSetName);

                        // Save to localStorage
                        localStorage.setItem('regexRules', JSON.stringify(pulledRules));
                        localStorage.setItem('selectedRegexRuleSet', pulledRuleSetName);

                        console.log('✅ Auto-pulled regex rules from DSA server:', pulledRuleSetName || 'custom');
                    } else {
                        console.log('ℹ️ No regex rules found on DSA server, using local rules');
                    }
                } catch (regexError) {
                    console.warn('⚠️ Could not auto-pull regex rules:', regexError.message);
                    // Non-fatal error - continue with local regex rules
                }

                // Auto-pull column mappings from DSA server if available
                try {
                    const { getColumnMappingsFromFolder } = await import('../utils/dsaIntegration.js');
                    const mappingsResult = await getColumnMappingsFromFolder(
                        config.baseUrl,
                        metadataTargetFolder,
                        dsaAuthStore.getToken()
                    );

                    if (mappingsResult.success && mappingsResult.columnMappings) {
                        const pulledMappings = mappingsResult.columnMappings.mappings;

                        // Auto-apply pulled column mappings
                        setColumnMappings(pulledMappings);

                        // Save to localStorage
                        localStorage.setItem('columnMappings', JSON.stringify(pulledMappings));

                        console.log('✅ Auto-pulled column mappings from DSA server for this collection');
                    } else {
                        console.log('ℹ️ No column mappings found on DSA server, using local mappings');
                    }
                } catch (mappingsError) {
                    console.warn('⚠️ Could not auto-pull column mappings:', mappingsError.message);
                    // Non-fatal error - continue with local column mappings
                }

                // Auto-pull protocols from DSA server if available
                try {
                    const { pullProtocolsFromDSA } = await import('../utils/dsaIntegration.js');
                    const protocolResult = await pullProtocolsFromDSA(
                        config.baseUrl,
                        metadataTargetFolder,
                        dsaAuthStore.getToken()
                    );

                    if (protocolResult.success) {
                        console.log('✅ Auto-pulled protocols from DSA server for this collection');
                        console.log(`📊 Pulled ${protocolResult.stainProtocols?.length || 0} stain protocols and ${protocolResult.regionProtocols?.length || 0} region protocols`);
                    } else {
                        console.log('ℹ️ No protocols found on DSA server for this collection');
                    }
                } catch (protocolError) {
                    console.warn('⚠️ Could not auto-pull protocols:', protocolError.message);
                    // Non-fatal error - continue with default protocols
                }

            }
        } catch (error) {
            console.error('Error loading DSA data:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
            setLoadingMessage('');
            // Reset the refresh flag after a short delay
            setTimeout(() => setIsDataRefresh(false), 100);
        }
    };

    const handleLoadMoreData = async () => {
        if (!authStatus.isAuthenticated) {
            setError('Please login to DSA server first');
            return;
        }

        if (!dataStatus.processedData || dataStatus.processedData.length === 0) {
            setError('Please load initial data first');
            return;
        }

        setIsLoadingMore(true);
        setError(null);

        try {
            // Load data in the background
            const result = await dataStore.loadMoreDsaData(dsaAuthStore, (progress) => {
                setLoadMoreProgress(progress);
            });

            if (result.success) {
                const newItemsCount = result.data?.length || 0;
                console.log(`✅ Successfully loaded ${result.totalItemCount} total items from DSA`);

                // Use the hasMoreData information from the API response
                if (result.hasMoreData !== undefined) {
                    setHasMoreData(result.hasMoreData);
                    console.log(`🏁 hasMoreData set to: ${result.hasMoreData} (from API response)`);
                } else {
                    // Fallback: If we got no new items, we've reached the end
                    if (newItemsCount === 0) {
                        setHasMoreData(false);
                        setHasCheckedForMoreData(true);
                        console.log('🏁 No more data available - reached end of dataset');
                    }
                }
            } else {
                console.error('❌ Failed to load more data:', result.error);
                setHasMoreData(false); // Assume no more data if loading failed
            }
        } catch (error) {
            console.error('Error loading more DSA data:', error);
            setError(error.message);
        } finally {
            setIsLoadingMore(false);
            setLoadMoreProgress({ current: 0, total: 0 });
        }
    };

    const handleAccessoryFileChange = (event) => {
        const file = event.target.files[0];
        if (file && (file.type === 'text/csv' ||
            file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
            file.type === 'application/vnd.ms-excel' ||
            file.name.endsWith('.csv') ||
            file.name.endsWith('.xlsx') ||
            file.name.endsWith('.xls'))) {
            setAccessoryFile(file);
            setError(null);
        } else {
            setError('Please select a valid CSV or Excel file');
            setAccessoryFile(null);
        }
    };

    const handleLoadAccessoryFile = async () => {
        if (!accessoryFile) {
            setError('Please select an accessory file first');
            return;
        }

        if (!dataStatus.processedData || dataStatus.processedData.length === 0) {
            setError('Please load DSA data first before uploading accessory file');
            return;
        }

        setIsLoading(true);
        setLoadingMessage('Loading accessory file...');
        setError(null);

        try {
            const result = await dataStore.loadAccessoryFile(accessoryFile);
            if (result.success) {
                console.log(`✅ Successfully loaded accessory data: ${result.itemCount} items`);
                console.log(`🔗 Matched ${result.matchedCount} items with DSA data`);
                console.log('📊 Matching details:', result.matchedData);
                setAccessoryData(result.data);

                // Show detailed matching info to user
                if (result.matchedCount > 0) {
                    console.log(`🎯 Found ${result.matchedCount} matches out of ${result.itemCount} accessory items`);
                    console.log('💡 Accessory fields added with "accessory_" prefix - check the data grid columns');
                    setAccessoryMatchInfo({
                        matched: result.matchedCount,
                        total: result.itemCount,
                        unmatched: result.itemCount - result.matchedCount
                    });
                } else {
                    console.warn('⚠️ No matches found - check if filenames in accessory file match DSA item names');
                    setAccessoryMatchInfo({
                        matched: 0,
                        total: result.itemCount,
                        unmatched: result.itemCount
                    });
                    // Show field mapping dialog if no matches found
                    setShowAccessoryFieldMapping(true);
                }
            }
        } catch (error) {
            console.error('Error loading accessory file:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
            setLoadingMessage('');
        }
    };

    const handleAccessoryFieldMapping = (filenameField) => {
        setAccessoryFilenameField(filenameField);
        setShowAccessoryFieldMapping(false);

        // Retry matching with the specified filename field
        if (accessoryData && filenameField) {
            setIsLoading(true);
            setLoadingMessage('Retrying accessory data matching...');

            try {
                const result = dataStore.retryAccessoryMatching(accessoryData, filenameField);
                setAccessoryMatchInfo({
                    matched: result.matchedCount,
                    total: result.itemCount,
                    unmatched: result.itemCount - result.matchedCount
                });

                if (result.matchedCount > 0) {
                    console.log(`🎯 Retry successful: ${result.matchedCount} matches found using field "${filenameField}"`);
                } else {
                    console.warn(`⚠️ Still no matches found using field "${filenameField}"`);
                }
            } catch (error) {
                console.error('Error retrying accessory matching:', error);
                setError(error.message);
            } finally {
                setIsLoading(false);
                setLoadingMessage('');
            }
        }
    };

    const handleClearData = () => {
        if (window.confirm('Are you sure you want to clear all loaded data?')) {
            dataStore.clearData();
            setCsvFile(null);
            setAccessoryFile(null);
            setAccessoryData(null);
            setError(null);
            setHasAppliedInitialRegex(false); // Reset regex flag when clearing data
        }
    };


    const handleSaveRegexRules = (newRules, ruleSetKey = '') => {
        setRegexRules(newRules);
        setSelectedRuleSet(ruleSetKey);

        // Save to localStorage for persistence
        localStorage.setItem('regexRules', JSON.stringify(newRules));
        localStorage.setItem('selectedRegexRuleSet', ruleSetKey);
        console.log('💾 Saved regex rules:', newRules);
        console.log('💾 Saved rule set:', ruleSetKey);

        // Apply the regex rules to the current data
        const result = dataStore.applyRegexRules(newRules);
        if (result.success) {
            console.log(`✅ Applied regex rules: ${result.extractedCount} items updated`);
        } else {
            console.error('❌ Failed to apply regex rules:', result.error);
        }
    };

    const handleSaveColumnMappings = (newMappings) => {
        setColumnMappings(newMappings);
        // Save to localStorage for persistence
        localStorage.setItem('columnMappings', JSON.stringify(newMappings));
        console.log('💾 Saved column mappings:', newMappings);

        // Update dataStore with column mappings
        dataStore.setColumnMappings(newMappings);

        // Apply the mappings to the current data
        const result = dataStore.applyColumnMappings(newMappings);
        if (result.success) {
            console.log(`✅ Applied column mappings: ${result.updatedCount} items updated`);
        } else {
            console.error('❌ Failed to apply column mappings:', result.error);
        }
    };

    const getAvailableColumns = () => {
        if (!dataStatus.processedData || dataStatus.processedData.length === 0) {
            return [];
        }

        // Generate nested column keys from all rows to capture accessory data columns
        // that might not be present in the first row
        const allKeys = new Set();

        // Scan all rows to find all possible column keys
        dataStatus.processedData.forEach((row, index) => {
            const rowKeys = generateNestedKeys(row);
            rowKeys.forEach(key => allKeys.add(key));
        });

        return Array.from(allKeys).sort();
    };

    // Generate column definitions from the first row of data
    const getColumnDefs = () => {
        if (!dataStatus.processedData || dataStatus.processedData.length === 0) {
            console.log('🔍 No data for column definitions');
            return [];
        }

        const firstRow = dataStatus.processedData[0];

        // Generate column definitions with proper nested field paths
        const generateColumnDefs = (obj, prefix = '') => {
            const columns = [];

            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    const fullKey = prefix ? `${prefix}.${key}` : key;
                    const value = obj[key];

                    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
                        // Recursively process nested objects
                        columns.push(...generateColumnDefs(value, fullKey));
                    } else {
                        // Add column for primitive values
                        const columnDef = {
                            field: fullKey,
                            headerName: getColumnDisplayName(fullKey),
                            sortable: true,
                            filter: true,
                            resizable: true,
                            minWidth: 150,
                            // Hide if explicitly set to false in columnVisibility OR if it's in HIDDEN_DSA_FIELDS (unless explicitly overridden)
                            hide: (columnVisibility[fullKey] === false) || (HIDDEN_DSA_FIELDS.includes(fullKey) && columnVisibility[fullKey] !== true),
                            cellStyle: (params) => {
                                const rowData = params.data;
                                const isModified = dataStore.modifiedItems?.has(rowData?.id);

                                // Highlight BDSA fields with different colors based on data source
                                if (fullKey.startsWith('BDSA.bdsaLocal.')) {
                                    const fieldName = fullKey.replace('BDSA.bdsaLocal.', '');
                                    const dataSource = rowData?.BDSA?._dataSource?.[fieldName];

                                    if (dataSource === 'column_mapping') {
                                        return {
                                            backgroundColor: '#e8f5e8',
                                            borderLeft: '4px solid #28a745',
                                            fontWeight: '500'
                                        };
                                    } else if (dataSource === 'regex') {
                                        return {
                                            backgroundColor: '#fff3cd',
                                            borderLeft: '4px solid #ffc107',
                                            fontWeight: '500'
                                        };
                                    } else if (dataSource === 'case_id_mapping') {
                                        return {
                                            backgroundColor: '#d4edda',
                                            borderLeft: '4px solid #28a745',
                                            fontWeight: '600'
                                        };
                                    } else if (params.value && params.value !== null && params.value !== '') {
                                        return {
                                            backgroundColor: '#f8f9fa',
                                            borderLeft: '4px solid #6c757d',
                                            fontWeight: '500'
                                        };
                                    }
                                }

                                // Highlight DSA-specific fields
                                if (fullKey.startsWith('dsa_') || fullKey === 'id' || fullKey === 'name') {
                                    return { backgroundColor: '#f0f7ff', fontWeight: 'bold' };
                                }

                                // Highlight modified rows
                                if (isModified) {
                                    return { backgroundColor: '#fff3e0', borderTop: '2px solid #ff9800' };
                                }

                                return null;
                            }
                        };

                        // Make BDSA local fields editable
                        if (fullKey.startsWith('BDSA.bdsaLocal.')) {
                            columnDef.editable = true;

                            // Use custom cell renderer for protocol fields
                            if (fullKey.includes('Protocol')) {
                                columnDef.cellRenderer = ProtocolArrayCellRenderer;
                                columnDef.editable = false; // Disable AG Grid editing, use modal instead
                            }
                        }

                        // Use custom cell renderer for name field to show tooltip on hover
                        if (fullKey === 'name') {
                            columnDef.cellRenderer = NameCellRenderer;
                        }

                        // Add cell value change handler for BDSA fields
                        if (fullKey.startsWith('BDSA.bdsaLocal.')) {
                            columnDef.onCellValueChanged = (params) => {
                                const { data, newValue, oldValue, colDef } = params;
                                if (newValue !== oldValue) {
                                    // Update the BDSA field
                                    if (!data.BDSA) {
                                        data.BDSA = {};
                                    }
                                    if (!data.BDSA.bdsaLocal) {
                                        data.BDSA.bdsaLocal = {};
                                    }
                                    const fieldName = colDef.field.replace('BDSA.bdsaLocal.', '');

                                    // Handle protocol arrays properly
                                    if (colDef.field.includes('Protocol')) {
                                        // Ensure we store as array
                                        data.BDSA.bdsaLocal[fieldName] = Array.isArray(newValue) ? newValue : [];
                                    } else {
                                        data.BDSA.bdsaLocal[fieldName] = newValue;
                                    }

                                    // Set data source to manual and update timestamp
                                    if (!data.BDSA._dataSource) {
                                        data.BDSA._dataSource = {};
                                    }
                                    data.BDSA._dataSource[fieldName] = 'manual';
                                    data.BDSA._lastModified = new Date().toISOString();

                                    // Mark item as modified
                                    dataStore.modifiedItems.add(data.id);
                                    dataStore.saveToStorage();
                                    dataStore.notify();

                                    console.log(`Manually updated ${colDef.field} to:`, newValue);
                                }
                            };
                        }

                        columns.push(columnDef);
                    }
                }
            }

            return columns;
        };

        const allColumns = generateColumnDefs(firstRow);

        // Use the priority fields from constants
        const preferredOrder = PRIORITY_BDSA_FIELDS;

        // Create ordered columns array
        const orderedColumns = [];
        const remainingColumns = [...allColumns];

        // console.log('🔍 Column generation debug:', {
        //     allColumns: allColumns.map(col => col.field),
        //     columnOrder: columnOrder,
        //     preferredOrder: preferredOrder
        // });

        // If we have a saved column order, use it (this takes precedence)
        if (columnOrder.length > 0) {
            columnOrder.forEach(field => {
                const column = remainingColumns.find(col => col.field === field);
                if (column) {
                    orderedColumns.push(column);
                    const index = remainingColumns.indexOf(column);
                    remainingColumns.splice(index, 1);
                }
            });
        } else {
            // Only use preferred order if no saved order exists
            preferredOrder.forEach(field => {
                const column = remainingColumns.find(col => col.field === field);
                if (column) {
                    orderedColumns.push(column);
                    const index = remainingColumns.indexOf(column);
                    remainingColumns.splice(index, 1);
                }
            });
        }

        // Finally, add any remaining columns
        orderedColumns.push(...remainingColumns);

        // Add status column at the beginning
        const statusColumn = {
            field: '_status',
            headerName: 'Status',
            sortable: true,
            filter: true,
            resizable: false,
            width: 120,
            hide: false,
            pinned: 'left',
            cellRenderer: StatusCellRenderer
        };

        // Insert status column at the beginning
        const columnDefs = [statusColumn, ...orderedColumns];

        // console.log('🔍 Generated column definitions:', {
        //     count: columnDefs.length,
        //     sampleColumns: columnDefs.slice(0, 5).map(col => col.field)
        // });

        return columnDefs;
    };

    return (
        <div className="input-data-tab">
            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-content">
                        <div className="loading-spinner"></div>
                        <p>{loadingMessage}</p>
                    </div>
                </div>
            )}

            {error && (
                <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    {error}
                </div>
            )}

            {/* Status Legend with Update Count and Clear Button - Compact inline legend */}
            {dataStatus.processedData && dataStatus.processedData.length > 0 && (
                <div className="status-legend">
                    <div className="legend-left">
                        <span className="legend-title">Status:</span>
                        <span className="status-badge column-mapping" title="Column mapping applied">
                            <span className="status-indicator column-mapping"></span>
                            Column
                        </span>
                        <span className="status-badge regex-extraction" title="Regex extraction applied">
                            <span className="status-indicator regex-extraction"></span>
                            Regex
                        </span>
                        <span className="status-badge manual-edit" title="Manual edit">
                            <span className="status-indicator manual-edit"></span>
                            Manual
                        </span>
                    </div>
                    <div className="legend-right">
                        {/* {console.log(`🔍 RENDER: modifiedItemsCount = ${modifiedItemsCount}, condition = ${modifiedItemsCount > 0}`)} */}
                        {modifiedItemsCount > 0 && (
                            <span className="update-count-text">
                                {modifiedItemsCount} of {dataStatus.processedData.length} items updated
                            </span>
                        )}
                        <button
                            onClick={() => {
                                if (window.confirm('🗑️ Clear ALL data and start fresh?\n\nThis will delete all loaded data, localStorage, and modified items.')) {
                                    localStorage.clear();
                                    dataStore.clearData();
                                    setCsvFile(null);
                                    setAccessoryFile(null);
                                    setAccessoryData(null);
                                    setHasAppliedInitialRegex(false);
                                    window.location.reload();
                                }
                            }}
                            className="btn btn-danger"
                            style={{
                                fontSize: '12px',
                                padding: '4px 8px',
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                marginLeft: '10px'
                            }}
                        >
                            🗑️ Clear ALL Data & Restart
                        </button>
                    </div>
                </div>
            )}

            {/* File Filtering Alert - Toast notification */}
            {showFileFilterNotification && window.dsaSkipStats && window.dsaSkipStats.totalSkipped > 0 && (
                <div className={`file-filter-notification ${isNotificationFading ? 'fade-out' : ''}`}>
                    <span className="notification-icon">📁</span>
                    <span className="notification-text">
                        {window.dsaSkipStats.totalSkipped.toLocaleString()} files filtered (image files only)
                    </span>
                    <button
                        className="notification-close"
                        onClick={() => {
                            setShowFileFilterNotification(false);
                            setIsNotificationFading(false);
                            window.dsaSkipStats = null;
                        }}
                        title="Dismiss"
                    >
                        ×
                    </button>
                </div>
            )}

            {/* Load More Data Button - Compact */}
            {(() => {
                // Only show if we're certain there's more data and haven't determined there isn't
                const shouldShow = dataStatus.processedData &&
                    dataStatus.processedData.length > 0 &&
                    dataStatus.dataSource === 'dsa' &&
                    !isLoadingMore &&
                    hasMoreData &&
                    !hasCheckedForMoreData;
                console.log(`🔍 DEBUG: Load More button conditions:`, {
                    hasData: !!dataStatus.processedData,
                    dataLength: dataStatus.processedData?.length || 0,
                    isDSA: dataStatus.dataSource === 'dsa',
                    notLoadingMore: !isLoadingMore,
                    hasMoreData,
                    hasCheckedForMoreData,
                    shouldShow
                });
                return shouldShow;
            })() && (
                    <div className="compact-notification load-more-notification">
                        <span className="notification-icon">⬇️</span>
                        <span className="notification-text">
                            Showing {dataStatus.processedData.length.toLocaleString()} items
                        </span>
                        <button className="notification-btn" onClick={handleLoadMoreData}>
                            Load More
                        </button>
                        <button
                            className="notification-btn"
                            onClick={() => {
                                console.log(`🔍 DEBUG: Current hasMoreData state: ${hasMoreData}`);
                                console.log(`🔍 DEBUG: Current hasCheckedForMoreData state: ${hasCheckedForMoreData}`);
                                console.log(`🔍 DEBUG: Current item count: ${dataStatus.processedData.length}`);
                                console.log(`🔍 DEBUG: Data source: ${dataStatus.dataSource}`);
                                console.log(`🔍 DEBUG: Loading more: ${isLoadingMore}`);
                                console.log(`🔍 DEBUG: Should show bar: ${dataStatus.processedData && dataStatus.processedData.length > 0 && dataStatus.dataSource === 'dsa' && !isLoadingMore && hasMoreData && !hasCheckedForMoreData}`);
                            }}
                            style={{ marginLeft: '5px', fontSize: '10px', padding: '2px 6px' }}
                            title="Debug Load More State"
                        >
                            ?
                        </button>
                        <button
                            className="notification-btn"
                            onClick={() => {
                                console.log(`🔍 Manually marking as no more data available`);
                                setHasMoreData(false);
                                setHasCheckedForMoreData(true);
                            }}
                            style={{ marginLeft: '5px', fontSize: '10px', padding: '2px 6px', backgroundColor: '#dc3545' }}
                            title="Mark as No More Data"
                        >
                            ✕
                        </button>
                    </div>
                )}

            {/* Loading More Progress */}
            {isLoadingMore && (
                <div className="loading-more-alert">
                    <div className="alert-header">
                        <span className="alert-icon">⏳</span>
                        <span className="alert-title">Loading More Data...</span>
                    </div>
                    <div className="alert-content">
                        <p>
                            Loading page {loadMoreProgress.current} of {loadMoreProgress.total}...
                            You can continue working while data loads in the background.
                        </p>
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${(loadMoreProgress.current / loadMoreProgress.total) * 100}%` }}
                            ></div>
                        </div>
                    </div>
                </div>
            )}

            {/* Toolbar */}
            <DataControlsToolbar
                dataSource={dataSource}
                handleDataSourceChange={handleDataSourceChange}
                csvFile={csvFile}
                handleCsvFileChange={handleCsvFileChange}
                handleLoadCsv={handleLoadCsv}
                excelFile={excelFile}
                handleExcelFileChange={handleExcelFileChange}
                handleLoadExcel={handleLoadExcel}
                accessoryFile={accessoryFile}
                handleAccessoryFileChange={handleAccessoryFileChange}
                handleLoadAccessoryFile={handleLoadAccessoryFile}
                accessoryData={accessoryData}
                accessoryMatchInfo={accessoryMatchInfo}
                isLoading={isLoading}
                authStatus={authStatus}
                handleLoadDsa={handleLoadDsa}
                dataStatus={dataStatus}
                showColumnPanel={showColumnPanel}
                setShowColumnPanel={setShowColumnPanel}
                setShowBdsaMapping={setShowBdsaMapping}
                setShowRegexRules={setShowRegexRules}
                setShowDsaSync={setShowDsaSync}
            />


            {/* Accessory Data Help Message */}
            {accessoryData && accessoryMatchInfo && (
                <div className="accessory-help-message">
                    <div className="help-header">
                        <span className="help-icon">💡</span>
                        <span className="help-title">Accessory Data Loaded</span>
                    </div>
                    <div className="help-content">
                        <p>
                            <strong>{accessoryMatchInfo.matched}</strong> out of <strong>{accessoryMatchInfo.total}</strong> accessory items were matched with DSA data.
                        </p>
                        <p>
                            <strong>To see the accessory fields:</strong> Click the "Show Columns" button above to view all available columns.
                            Look for fields starting with <code>accessory_</code> (e.g., <code>accessory_R#</code>, <code>accessory_SB Stain/IHC</code>).
                        </p>
                        {accessoryMatchInfo.unmatched > 0 && (
                            <p className="unmatched-warning">
                                <strong>Note:</strong> {accessoryMatchInfo.unmatched} items couldn't be matched.
                                Check that filenames in your accessory file exactly match the DSA item names.
                            </p>
                        )}
                    </div>
                </div>
            )}


            {/* Column Visibility Modal */}
            <ColumnVisibilityModal
                isOpen={showColumnPanel && dataStatus.processedData && dataStatus.processedData.length > 0}
                onClose={() => setShowColumnPanel(false)}
                dataStatus={dataStatus}
                columnVisibility={columnVisibility}
                columnOrder={columnOrder}
                toggleColumnVisibility={toggleColumnVisibility}
                moveColumn={moveColumn}
                showAllColumns={showAllColumns}
                hideAllColumns={hideAllColumns}
                resetColumnOrder={resetColumnOrder}
            />

            {/* Data Grid */}
            <div className="data-grid-container">
                {(() => {
                    console.log('📊 About to render DataGrid with:', {
                        hasDataStatus: !!dataStatus,
                        processedDataLength: dataStatus.processedData?.length || 0,
                        dataSource: dataSource,
                        hasGetColumnDefs: typeof getColumnDefs === 'function'
                    });
                    return null;
                })()}
                <DataGrid
                    dataStatus={dataStatus}
                    getColumnDefs={getColumnDefs}
                    dataSource={dataSource}
                />
            </div>

            {/* BDSA Mapping Modal */}
            <BdsaMappingModal
                isOpen={showBdsaMapping}
                onClose={() => setShowBdsaMapping(false)}
                onSave={handleSaveColumnMappings}
                currentMappings={columnMappings}
                availableColumns={getAvailableColumns()}
            />

            {/* Regex Rules Modal */}
            <RegexRulesModal
                isOpen={showRegexRules}
                onClose={() => setShowRegexRules(false)}
                onSave={handleSaveRegexRules}
                currentRules={regexRules}
                selectedRuleSet={selectedRuleSet}
                sampleData={dataStatus.processedData || []}
            />

            {/* DSA Sync Modal */}
            <DsaSyncModal
                isOpen={showDsaSync}
                onClose={() => setShowDsaSync(false)}
            />

            {/* Excel Sheet Selection Modal */}
            <ExcelSheetSelectionModal
                isOpen={showExcelSheetModal}
                onClose={() => setShowExcelSheetModal(false)}
                sheetNames={excelSheetNames}
                onSheetSelect={handleSheetSelect}
                fileName={excelFile?.name || ''}
            />

            {/* Accessory Field Mapping Modal */}
            <AccessoryFieldMappingModal
                isOpen={showAccessoryFieldMapping}
                onClose={() => setShowAccessoryFieldMapping(false)}
                onSave={handleAccessoryFieldMapping}
                accessoryData={accessoryData}
                dsaData={dataStatus.processedData || []}
            />
        </div>
    );
};

export default InputDataTab;
