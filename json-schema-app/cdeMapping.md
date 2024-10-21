## CDE Mapping

Version: 0.0.1

Top Level Terminology:

- <b>stainID</b>:  This is the internal / local identifier for a stain.  It is not necessarily unique, but it is consistent.
      Common Data Element Terminology:  
         Currently I do not see a single CDE with all of the stains.  However DigiPath has a CDE for each stain.  
         The CDE's are named brainRegion_<i>path_stain</i>

         Delimit multiple stains or antibodies with "|". Examples include: ["Silver","CD68","TDP-43","alpha-syn","Tau","AB","H&E"].
   
        Our terminology will be:  path_stain
        Values will be:  ["Silver","CD68","TDP-43","alpha-syn","Tau","AB","H&E","Thioflavin"]
        Modifications:  We added Thioflavin to the list.

- <b>caseID</b> :  This is the identifier for a case.  It is a string that uniquely identifies a case.  It is consistent for a given case, but not necessarily unique across cases.  The caseID will have subtypes (caseSource), valid types include:
        ["local","bdsa","nacc","nigad","adni"]

    - blockID:  This is the identifier for a block.  It is a string that uniquely identifies a block.  It is consistent for a given case, i.e. all slides with a unique blockID belong to the same region for a case.  Sometimes this identifier is actually consistent across cases, but but always.  Not all centers may need this, if regionName is specified in the input CSV, we will not need this.


Brain Region Mapping:
    - This maps a local region name to the BDSA Schema.  Our slide may simply say Hipp where the BDSA schema would be mapped as Hippocampus --> L --> Axial --> 2uM

    Properties:
        - brain_region:  This is one of the following standardized region names:
            [  "Medulla",  "Pons",  "Midbrain",  "Thalamus",  "Basal_Ganglia","Cerebellum", "Hippocampus", "Amygdala", "Ant_Cingulate",
                "Post_Cingulate", "Frontal",  "Parietal", "Occipital",
                "Temporal", "Olfactory",  "White_matter",  "Motor_cortex",  "Insula",  "Frontal_pole","Temporal_pole",  "Spinal_cord",  "Hypothalamus"
            ]
        - hemisphere:  This is one of the following:
            ["L","R","Unknown]
        - sliceOrientation:  This is one of the following:
            ["Axial","Coronal","Sagittal","Other"]
        - damage:  This is an array of the following:
            ["Infarct","Lacune","Microinfarct","CTE","TBI"]


    TO DO:  Add Stain Level Properties
        Dilution, Vendor, Phospho-specific, Epitope