
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'input': NextflowParameter(
        type=LatchFile,
        default=None,
        section_title='Input/output options',
        description='Path to comma-separated file containing information about the samples in the experiment.',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Email address for completion summary.',
    ),
    'multiqc_title': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='MultiQC report title. Printed as page header, used for filename if not otherwise specified.',
    ),
    'spaceranger_probeset': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title='Space Ranger options',
        description='Location of Space Ranger probeset file.',
    ),
    'spaceranger_reference': NextflowParameter(
        type=typing.Optional[str],
        default='https://cf.10xgenomics.com/supp/spatial-exp/refdata-gex-GRCh38-2020-A.tar.gz',
        section_title=None,
        description='Location of Space Ranger reference directory. May be packed as `tar.gz` file.',
    ),
    'spaceranger_save_reference': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Optional outputs',
        description='Save the extracted tar archive of the Space Ranger reference.',
    ),
    'save_untar_output': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Save extracted tar archives of input data.',
    ),
    'qc_min_counts': NextflowParameter(
        type=typing.Optional[int],
        default=500,
        section_title='Analysis options',
        description='The minimum number of UMIs needed in a spot for that spot to pass the filtering.',
    ),
    'qc_min_genes': NextflowParameter(
        type=typing.Optional[int],
        default=250,
        section_title=None,
        description='The minimum number of expressed genes in a spot needed for that spot to pass the filtering.',
    ),
    'qc_min_spots': NextflowParameter(
        type=typing.Optional[int],
        default=1,
        section_title=None,
        description='The minimum number of spots in which a gene is expressed for that gene to pass the filtering.',
    ),
    'qc_mito_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=20,
        section_title=None,
        description='The maximum proportion of mitochondrial content that a spot is allowed to have to pass the filtering.',
    ),
    'qc_ribo_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=0,
        section_title=None,
        description='The minimum proportion of ribosomal content that a spot is needs to have to pass the filtering (no filtering is done by default).',
    ),
    'qc_hb_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=100,
        section_title=None,
        description='The maximum proportion of haemoglobin content that a spot is allowed to have to pass the filtering (no filtering is done by default).',
    ),
    'cluster_n_hvgs': NextflowParameter(
        type=typing.Optional[int],
        default=2000,
        section_title=None,
        description='The number of top highly variable genes to use for the analyses.',
    ),
    'cluster_resolution': NextflowParameter(
        type=typing.Optional[float],
        default=1,
        section_title=None,
        description='The resolution for the clustering of the spots.',
    ),
    'svg_autocorr_method': NextflowParameter(
        type=typing.Optional[str],
        default='moran',
        section_title=None,
        description='The method to use for spatially variable gene autocorrelation.',
    ),
    'n_top_svgs': NextflowParameter(
        type=typing.Optional[int],
        default=14,
        section_title=None,
        description='The number of top spatially variable genes to plot.',
    ),
    'multiqc_methods_description': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Generic options',
        description='Custom MultiQC yaml file containing HTML including a methods description.',
    ),
}

