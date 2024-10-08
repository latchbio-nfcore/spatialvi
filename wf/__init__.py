import csv
import os
import shutil
import subprocess
import typing
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

import requests
import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch import map_task
from latch.ldata.path import LPath
from latch.resources.launch_plan import LaunchPlan
from latch.resources.tasks import custom_task, nextflow_runtime_task
from latch.resources.workflow import workflow
from latch.types import metadata
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.nextflow.workflow import get_flag
from latch_cli.services.register.utils import import_module_by_path
from latch_cli.utils import urljoins

from wf.entrypoint import Sample, initialize, nextflow_runtime

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)

@workflow(metadata._nextflow_metadata)
def nf_nf_core_spatialvi(input: typing.List[Sample], outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], spaceranger_probeset: typing.Optional[LatchFile], spaceranger_save_reference: bool, save_untar_output: bool, multiqc_methods_description: typing.Optional[str], spaceranger_reference: typing.Optional[str] = 'https://cf.10xgenomics.com/supp/spatial-exp/refdata-gex-GRCh38-2020-A.tar.gz', qc_min_counts: typing.Optional[int] = 500, qc_min_genes: typing.Optional[int] = 250, qc_min_spots: typing.Optional[int] = 1, qc_mito_threshold: typing.Optional[float] = 20.0, qc_ribo_threshold: typing.Optional[float] = 0.0, qc_hb_threshold: typing.Optional[float] = 100.0, cluster_n_hvgs: typing.Optional[int] = 2000, cluster_resolution: typing.Optional[float] = 1.0, svg_autocorr_method: typing.Optional[str] = 'moran', visium_hd: bool = False, n_top_svgs: typing.Optional[int] = 14) -> None:
    """
    nf-core/spatialvi

    <html>
    <p align="center">
    <img src="https://user-images.githubusercontent.com/31255434/182289305-4cc620e3-86ae-480f-9b61-6ca83283caa5.jpg" alt="Latch Verified" width="100">
    </p>

    <p align="center">
    <strong>
    Latch Verified
    </strong>

   [![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/spatialvi/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.XXXXXXX-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.XXXXXXX)

    **nfcore/spatialvi** is a bioinformatics analysis pipeline for Visium spatial transcriptomics data from 10x Genomics. It can process and analyse spatial data either directly from raw data by running [Space Ranger](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/what-is-space-ranger) or data already processed by Space Ranger.

    This workflow is hosted on Latch Workflows, using a native Nextflow integration, with a graphical interface for accessible analysis by scientists. There is also an integration with Latch Registry so that batched workflows can be launched from “graphical sample sheets” or tables associating raw sequencing files with metadata.

    The managed computing infrastructure scales to hundreds of samples, with clear logging and error-reporting. Data provenance links versioned and containerized workflow code to input and output files.

    </p>

    ## Pipeline summary

    By default, the pipeline currently performs the following:
    0. Raw data processing with Space Ranger (optional)
    1. Quality controls and filtering
    2. Normalisation
    3. Dimensionality reduction and clustering (_not currently supported for Visium HD data_)
    4. Differential gene expression testing (_not currently supported for Visium HD data_)

    ## Pipeline output

    To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/spatialvi/results) tab on the nf-core website pipeline page.
    For more details about the output files and reports, please refer to the
    [output documentation](https://nf-co.re/spatialvi/output).

    ## Credits

    nf-core/spatialvi was originally developed by the Jackson
    Laboratory<sup>1</sup>, up to the [0.1.0](https://github.com/nf-core/spatialvi/releases/tag/0.1.0)
    tag. It was further developed in a collaboration between the [National
    Bioinformatics Infrastructure Sweden](https://nbis.se/) and [National Genomics
    Infrastructure](https://ngisweden.scilifelab.se/) within [SciLifeLab](https://scilifelab.se/);
    it is currently developed and maintained by [Erik Fasterius](https://github.com/fasterius)
    and [Christophe Avenel](https://github.com/cavenel).

    Many thanks to others who have helped out along the way too, especially [Gregor
    Sturm](https://github.com/grst)!

    _<sup>1</sup> Supported by grants from the US National Institutes of Health
    [U24CA224067](https://reporter.nih.gov/project-details/10261367) and
    [U54AG075941](https://reporter.nih.gov/project-details/10376627). Original
    authors [Dr. Sergii Domanskyi](https://github.com/sdomanskyi), Prof. Jeffrey
    Chuang and Dr. Anuj Srivastava._

    ## Contributions and Support

    If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

    For further information or help, don't hesitate to get in touch on the [Slack `#spatialvi` channel](https://nfcore.slack.com/channels/spatialvi) (you can join with [this invite](https://nf-co.re/join/slack)).

    ## Citations

    <!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi and badge at the top of this file. -->
    <!-- If you use nf-core/spatialvi for your analysis, please cite it using the following doi: [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX) -->

    An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

    You can cite the `nf-core` publication as follows:

    > **The nf-core framework for community-curated bioinformatics pipelines.**
    >
    > Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
    >
    > _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).


    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, input=input, outdir=outdir, email=email, multiqc_title=multiqc_title, spaceranger_probeset=spaceranger_probeset, spaceranger_reference=spaceranger_reference, spaceranger_save_reference=spaceranger_save_reference, save_untar_output=save_untar_output, qc_min_counts=qc_min_counts, qc_min_genes=qc_min_genes, qc_min_spots=qc_min_spots, qc_mito_threshold=qc_mito_threshold, qc_ribo_threshold=qc_ribo_threshold, qc_hb_threshold=qc_hb_threshold, cluster_n_hvgs=cluster_n_hvgs, cluster_resolution=cluster_resolution, svg_autocorr_method=svg_autocorr_method, n_top_svgs=n_top_svgs, multiqc_methods_description=multiqc_methods_description, visium_hd=visium_hd)


LaunchPlan(
    nf_nf_core_spatialvi,
    "Test Data",
    {
        "input": [
            Sample(
                sample="Visium_FFPE_Human_Ovarian_Cancer",
                fastq_dir=LatchDir("s3://latch-public/test-data/35972/spatial_test_data/"),
                image=LatchFile("s3://latch-public/test-data/35972/Visium_FFPE_Human_Ovarian_Cancer_image.jpg"),
                slide="V10L13-020",
                area="D1",
                slidefile=LatchFile("s3://latch-public/test-data/35972/V10L13-020.gpr"),
                cytaimage=None,
                manual_alignment=None
            )],
        "outdir": LatchDir("latch:///spatialvi_outputs"),
        "spaceranger_probeset": LatchFile("s3://latch-public/test-data/35972/Visium_Human_Transcriptome_Probe_Set_v1.0_GRCh38-2020-A.csv"),
        "visium_hd": False,
        "spaceranger_reference": None,
    }
)
