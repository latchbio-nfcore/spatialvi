
import typing
from dataclasses import dataclass

import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import (FlowBase, Fork, ForkBranch,
                                  NextflowParameter, Params, Section, Spoiler)

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

flow: typing.List[FlowBase] = [
    Section(
        "Input / Output",
        Params(
            "input",
            "visium_hd",
            "outdir",
        ),
    ),
    Section(
        "SpaceRanger",
        Params("visium_hd",
               "spaceranger_probeset",
               "spaceranger_reference",
               "spaceranger_save_reference",
               "save_untar_output"),
    ),
    Spoiler(
        "QC Parameters",
        Params("qc_min_counts",
               "qc_min_genes",
               "qc_min_spots",
               "qc_mito_threshold"
               "qc_ribo_threshold"
               "qc_hb_threshold"
               "qc_min_spots"),
    ),
    Spoiler(
        "Clustering Parameters",
        Params(
            "cluster_n_hvgs",
            "cluster_resolution",
            "svg_autocorr_method",
            "n_top_svgs",
        ),
    ),
    Spoiler(
        "Spatially Variable Genes Parameters",
        Params(
            "svg_autocorr_method",
            "n_top_svgs",
        ),
    ),
    Spoiler(
        "MultiQC Parameters",
        Params("multiqc_title",
               "email",
               "multiqc_methods_description"),
    ),
]


@dataclass(frozen=True)
class Sample:
    sample: str
    fastq_dir: LatchDir
    image: LatchFile
    slide: str
    area: str
    manual_alignment: typing.Optional[LatchFile]
    slidefile: typing.Optional[LatchFile]
    cytaimage: typing.Optional[LatchFile]

generated_parameters = {
    'input': NextflowParameter(
        # type=LatchFile,
        type=typing.List[Sample],
        samplesheet=True,
        samplesheet_type='csv',
        default=None,
        display_name='Input/output options',
        description='Path to comma-separated file containing information about the samples in the experiment.',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        display_name="outdir",
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        display_name="Email",
        description='Email address for completion summary.',
    ),
    'multiqc_title': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        display_name="MultiQC Title",
        description='MultiQC report title. Printed as page header, used for filename if not otherwise specified.',
    ),
    'spaceranger_probeset': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        display_name='spaceranger_probeset',
        description='Location of Space Ranger probeset file.',
    ),
    'spaceranger_reference': NextflowParameter(
        type=typing.Optional[str],
        default='https://cf.10xgenomics.com/supp/spatial-exp/refdata-gex-GRCh38-2020-A.tar.gz',
        display_name="spaceranger_reference",
        description='Location of Space Ranger reference directory. May be packed as `tar.gz` file.',
    ),
    'spaceranger_save_reference': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        display_name='spaceranger_save_reference',
        description='Save the extracted tar archive of the Space Ranger reference.',
    ),
    'save_untar_output': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        display_name='save_untar_output',
        description='Save extracted tar archives of input data.',
    ),
    'visium_hd': NextflowParameter(
        type=bool,
        default=False,
        display_name="Visium HD",
        description='Visium HD Data',
    ),
    'qc_min_counts': NextflowParameter(
        type=typing.Optional[int],
        default=500,
        display_name='qc_min_counts',
        description='The minimum number of UMIs needed in a spot for that spot to pass the filtering.',
    ),
    'qc_min_genes': NextflowParameter(
        type=typing.Optional[int],
        default=250,
        section_title=None,
        display_name='qc_min_genes',
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
        default=20.0,
        display_name='qc_mito_threshold',
        description='The maximum proportion of mitochondrial content that a spot is allowed to have to pass the filtering.',
    ),
    'qc_ribo_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=0.0,
        display_name='qc_ribo_threshold',
        description='The minimum proportion of ribosomal content that a spot is needs to have to pass the filtering (no filtering is done by default).',
    ),
    'qc_hb_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=100.0,
        display_name='qc_hb_threshold',
        description='The maximum proportion of haemoglobin content that a spot is allowed to have to pass the filtering (no filtering is done by default).',
    ),
    'cluster_n_hvgs': NextflowParameter(
        type=typing.Optional[int],
        default=2000,
        display_name='cluster_n_hvgs',
        description='The number of top highly variable genes to use for the analyses.',
    ),
    'cluster_resolution': NextflowParameter(
        type=typing.Optional[float],
        default=1.0,
        display_name='cluster_resolution',
        description='The resolution for the clustering of the spots.',
    ),
    'svg_autocorr_method': NextflowParameter(
        type=typing.Optional[str],
        default='moran',
        display_name='svg_autocorr_method',
        description='The method to use for spatially variable gene autocorrelation.',
    ),
    'n_top_svgs': NextflowParameter(
        type=typing.Optional[int],
        default=14,
        display_name='n_top_svgs',
        description='The number of top spatially variable genes to plot.',
    ),
    'multiqc_methods_description': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        display_name='multiqc_methods_description',
        description='Custom MultiQC yaml file containing HTML including a methods description.',
    ),
}

