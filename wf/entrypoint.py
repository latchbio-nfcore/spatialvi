import os
import shutil
import subprocess
import typing
from pathlib import Path

import requests
import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch.ldata.path import LPath
from latch.resources.tasks import custom_task, nextflow_runtime_task
from latch.resources.workflow import workflow
from latch.types import metadata
from latch.types.directory import LatchDir
from latch.types.file import LatchFile
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.nextflow.workflow import get_flag
from latch_cli.services.register.utils import import_module_by_path
from latch_cli.utils import urljoins

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)


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
            "storage_gib": 100,
        },
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]


@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(
    pvc_name: str,
    input: LatchFile,
    outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})],
    email: typing.Optional[str],
    multiqc_title: typing.Optional[str],
    spaceranger_probeset: typing.Optional[LatchFile],
    spaceranger_save_reference: typing.Optional[bool],
    save_untar_output: typing.Optional[bool],
    multiqc_methods_description: typing.Optional[str],
    spaceranger_reference: typing.Optional[str],
    qc_min_counts: typing.Optional[int],
    qc_min_genes: typing.Optional[int],
    qc_min_spots: typing.Optional[int],
    qc_mito_threshold: typing.Optional[float],
    qc_ribo_threshold: typing.Optional[float],
    qc_hb_threshold: typing.Optional[float],
    cluster_n_hvgs: typing.Optional[int],
    cluster_resolution: typing.Optional[float],
    svg_autocorr_method: typing.Optional[str],
    n_top_svgs: typing.Optional[int],
) -> None:
    try:
        shared_dir = Path("/nf-workdir")

        ignore_list = [
            "latch",
            ".latch",
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

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            "docker",
            "-c",
            "latch.config",
            *get_flag("input", input),
            *get_flag("outdir", outdir),
            *get_flag("email", email),
            *get_flag("multiqc_title", multiqc_title),
            *get_flag("spaceranger_probeset", spaceranger_probeset),
            *get_flag("spaceranger_reference", spaceranger_reference),
            *get_flag("spaceranger_save_reference", spaceranger_save_reference),
            *get_flag("save_untar_output", save_untar_output),
            *get_flag("qc_min_counts", qc_min_counts),
            *get_flag("qc_min_genes", qc_min_genes),
            *get_flag("qc_min_spots", qc_min_spots),
            *get_flag("qc_mito_threshold", qc_mito_threshold),
            *get_flag("qc_ribo_threshold", qc_ribo_threshold),
            *get_flag("qc_hb_threshold", qc_hb_threshold),
            *get_flag("cluster_n_hvgs", cluster_n_hvgs),
            *get_flag("cluster_resolution", cluster_resolution),
            *get_flag("svg_autocorr_method", svg_autocorr_method),
            *get_flag("n_top_svgs", n_top_svgs),
            *get_flag("multiqc_methods_description", multiqc_methods_description),
        ]

        print("Launching Nextflow Runtime")
        print(" ".join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
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
                remote = LPath(
                    urljoins(
                        "latch:///your_log_dir/nf_nf_core_spatialvi",
                        name,
                        "nextflow.log",
                    )
                )
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)


@workflow(metadata._nextflow_metadata)
def nf_nf_core_spatialvi(
    input: LatchFile,
    outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})],
    email: typing.Optional[str],
    multiqc_title: typing.Optional[str],
    spaceranger_probeset: typing.Optional[LatchFile],
    spaceranger_save_reference: typing.Optional[bool],
    save_untar_output: typing.Optional[bool],
    multiqc_methods_description: typing.Optional[str],
    spaceranger_reference: typing.Optional[
        str
    ] = "https://cf.10xgenomics.com/supp/spatial-exp/refdata-gex-GRCh38-2020-A.tar.gz",
    qc_min_counts: typing.Optional[int] = 500,
    qc_min_genes: typing.Optional[int] = 250,
    qc_min_spots: typing.Optional[int] = 1,
    qc_mito_threshold: typing.Optional[float] = 20.0,
    qc_ribo_threshold: typing.Optional[float] = 0.0,
    qc_hb_threshold: typing.Optional[float] = 100.0,
    cluster_n_hvgs: typing.Optional[int] = 2000,
    cluster_resolution: typing.Optional[float] = 1.0,
    svg_autocorr_method: typing.Optional[str] = "moran",
    n_top_svgs: typing.Optional[int] = 14,
) -> None:
    """
    nf-core/spatialvi

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(
        pvc_name=pvc_name,
        input=input,
        outdir=outdir,
        email=email,
        multiqc_title=multiqc_title,
        spaceranger_probeset=spaceranger_probeset,
        spaceranger_reference=spaceranger_reference,
        spaceranger_save_reference=spaceranger_save_reference,
        save_untar_output=save_untar_output,
        qc_min_counts=qc_min_counts,
        qc_min_genes=qc_min_genes,
        qc_min_spots=qc_min_spots,
        qc_mito_threshold=qc_mito_threshold,
        qc_ribo_threshold=qc_ribo_threshold,
        qc_hb_threshold=qc_hb_threshold,
        cluster_n_hvgs=cluster_n_hvgs,
        cluster_resolution=cluster_resolution,
        svg_autocorr_method=svg_autocorr_method,
        n_top_svgs=n_top_svgs,
        multiqc_methods_description=multiqc_methods_description,
    )
