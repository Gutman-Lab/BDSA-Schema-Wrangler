import tifftools

# ts = ImageItem().tileSource(sampleSlide)
# sourcePath = ts._getLargeImagePath()
# tiffinfo = tifftools.read_tiff(sourcePath)

from large_image_source_tiff import TiffFileTileSource

sampleSVSfile = "/Users/dagutman/devel/nci-dsa-deid/devops/nci-dsa-deid/import/SmallSampleFiles/TCGA-06-5416-01A-01-TS1.1749a247-c33d-4a06-88f2-4deef3c5d982.svs"

import large_image_source_tiff.girder_source

# large_image_source_tiff.girder_source.TiffGirderTileSource = TiffFileTileSource
# tiffSource = large_image_source_tiff.girder_source.TiffGirderTileSource(sampleSVSfile)
##tiffSource = large_image_source_tiff.girder_source.TiffGirderTileSource(item)

tiffSource = large_image_source_tiff.TiffFileTileSource(sampleSVSfile)
