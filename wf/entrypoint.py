import csv
import os
import shutil
import subprocess
import typing
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import requests
import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch.ldata.path import LPath
from latch.resources.tasks import custom_task, nextflow_runtime_task
from latch.resources.workflow import workflow
from latch.types import metadata
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.nextflow.workflow import get_flag
from latch_cli.services.register.utils import import_module_by_path
from latch_cli.utils import urljoins

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata


@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "v2"
        },
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]


@dataclass
class Sample:
    sample: str
    fastq_dir: LatchDir
    image: LatchFile
    slide: str
    area: str
    manual_alignment: typing.Optional[LatchFile]
    slidefile: typing.Optional[LatchFile]
    cytaimage: typing.Optional[LatchFile]


def clean_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            cleaned_row = [field.strip().replace('\n', ' ') for field in row]
            writer.writerow(cleaned_row)

input_construct_samplesheet = metadata._nextflow_metadata.parameters['input'].samplesheet_constructor


@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, input: typing.List[Sample], outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], spaceranger_probeset: typing.Optional[LatchFile], spaceranger_save_reference: bool, save_untar_output: bool, multiqc_methods_description: typing.Optional[str], spaceranger_reference: typing.Optional[str], qc_min_counts: typing.Optional[int], qc_min_genes: typing.Optional[int], qc_min_spots: typing.Optional[int], qc_mito_threshold: typing.Optional[float], qc_ribo_threshold: typing.Optional[float], qc_hb_threshold: typing.Optional[float], cluster_n_hvgs: typing.Optional[int], cluster_resolution: typing.Optional[float], svg_autocorr_method: typing.Optional[str], n_top_svgs: typing.Optional[int], visium_hd: bool = False) -> None:
    try:
        shared_dir = Path("/nf-workdir")

        input_samplesheet = input_construct_samplesheet(input)

        clean_csv(input_samplesheet, "updated_samplesheet.csv")

        ignore_list = [
            "latch",
            ".latch",
            ".git",
            "nextflow",
            ".nextflow",
            "work",
            "results",
            "miniconda",
            "anaconda3",
            "mambaforge",
        ]

        shutil.copytree(
            Path("/root"),
            shared_dir,
            ignore=lambda src, names: ignore_list,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=True,
        )

        profile_list = []
        if False:
            profile_list.extend([p.value for p in execution_profiles])

        if len(profile_list) == 0:
            profile_list.append("standard")

        profiles = ','.join(profile_list)

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            profiles,
            "-c",
            "latch.config",
            "-resume",
        *get_flag('input', "updated_samplesheet.csv"),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('spaceranger_probeset', spaceranger_probeset),
                *get_flag('spaceranger_reference', spaceranger_reference),
                # *get_flag('spaceranger_save_reference', spaceranger_save_reference),
                # *get_flag('save_untar_output', save_untar_output),
                *get_flag('qc_min_counts', qc_min_counts),
                *get_flag('qc_min_genes', qc_min_genes),
                *get_flag('qc_min_spots', qc_min_spots),
                *get_flag('qc_mito_threshold', qc_mito_threshold),
                *get_flag('qc_ribo_threshold', qc_ribo_threshold),
                *get_flag('qc_hb_threshold', qc_hb_threshold),
                *get_flag('cluster_n_hvgs', cluster_n_hvgs),
                *get_flag('cluster_resolution', cluster_resolution),
                *get_flag('svg_autocorr_method', svg_autocorr_method),
                *get_flag('n_top_svgs', n_top_svgs),
                *get_flag('multiqc_methods_description', multiqc_methods_description),
                *get_flag('visium_hd', visium_hd)
        ]

        if spaceranger_save_reference:
            cmd.append("--spaceranger_save_reference")
        if save_untar_output:
            cmd.append("--save_untar_output")

        print("Launching Nextflow Runtime")
        print(' '.join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms1536M -Xmx6144M -XX:ActiveProcessorCount=4",
            "NXF_DISABLE_CHECK_LATEST": "true",
            "NXF_ENABLE_VIRTUAL_THREADS": "false",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(urljoins("latch:///nfcore_spatialvi_logs", name, "nextflow.log"))
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)



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

