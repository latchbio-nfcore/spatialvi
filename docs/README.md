# nf-core/spatialvi

To learn more about input parameters, please look into the documentation on the nf-core website: [https://nf-co.re/spatialvi/usage](https://nf-co.re/spatialvi/usage). This page provides an overview of how the pipeline works, how to run it and a description of all of the different command-line flags.

## nf-core/spatialvi: Output

### Introduction

This document describes the output produced by the pipeline. Most of the output
is contained within HTML reports created with [Quarto](https://quarto.org/), but
there are also other files which you can either take and analyse further by
yourself or explore interactively with _e.g._ [TissUUmaps](https://tissuumaps.github.io/).

The directories listed below will be created in the results directory after the
pipeline has finished. Results for individual samples will be created in
subdirectories following the `<OUTDIR>/<SAMPLE>/` structure. All paths are
relative to the top-level results directory.

The pipeline is built using [Nextflow](https://www.nextflow.io/) and processes
data using the following steps:

- [Space Ranger](#space-ranger)
- [Data](#data)
- [Reports](#reports)
  - [Quality controls and normalisation](#quality-controls-and-normalisation)
  - [Clustering](#clustering)
  - [Differential expression](#differential-expression)
- [Workflow reporting](#workflow-reporting)
  - [Pipeline information](#pipeline-information) - Report metrics generated
    during the workflow execution

### Space Ranger

<details markdown="1">
<summary>Output files</summary>

- `<SAMPLE>/spaceranger/`
  - `outs/spatial/tissue_[hi/low]res_image.png`: High and low resolution images.
  - `outs/spatial/tissue_positions_list.csv`: Spot barcodes and their array
    positions.
  - `outs/spatial/scalefactors_json.json`: Scale conversion factors for the
    spots.
  - `outs/filtered_feature_bc_matrix/barcodes.tsv.gz`: List of barcode IDs.
  - `outs/filtered_feature_bc_matrix/features.tsv.gz`: List of feature IDs.
  - `outs/filtered_feature_bc_matrix/matrix.mtx.gz`: Matrix of UMIs, barcodes
    and features.

</details>

All files produced by Space Ranger are currently published as output of this
pipeline, regardless if they're being used downstream or not; you can find more
information about these files at the [10X website](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/overview).

### Data

<details markdown="1">
<summary>Output files</summary>

- `<SAMPLE>/data/`
  - `sdata_processed.zarr`: Processed data in SpatialData format.
  - `adata_processed.h5ad`: Processed data in AnnData format.
  - `spatially_variable_genes.csv`: List of spatially variable genes.

</details>

Data in `.zarr` and `.h5ad` formats as processed by the pipeline, which can be
used for further downstream analyses if desired; unprocessed data is also
present in these files. It can also be used by the [TissUUmaps](https://tissuumaps.github.io/)
browser-based tool for visualisation and exploration, allowing you to delve into
the data in an interactive way. The list of spatially variable genes are added
as a convenience if you want to explore them in _e.g._ Excel.

### Reports

Reports are only created for Visium data (not Visium HD).

<details markdown="1">
<summary>Output files</summary>

- `<SAMPLE>/reports/`
  - `_extensions/`: Quarto nf-core extension, common to all reports.

</details>

#### Quality controls and filtering

<details markdown="1">
<summary>Output files</summary>

- `<SAMPLE>/reports/`
  - `quality_controls.html`: Rendered HTML report.
  - `quality_controls.yml`: YAML file containing parameters used in the report.
  - `quality_controls.qmd`: Quarto document used for rendering the report.

</details>

Report containing analyses related to quality controls and filtering of spatial
data. Spots are filtered based on total counts, number of expressed genes as
well as presence in tissue; you can find more details in the report itself.

#### Clustering

<details markdown="1">
<summary>Output files</summary>

- `<SAMPLE>/reports/`
  - `clustering.html`: Rendered HTML report.
  - `clustering.yml`: YAML file containing parameters used in the report.
  - `clustering.qmd`: Quarto document used for rendering the report.

</details>

Report containing analyses related to normalisation, dimensionality reduction,
clustering and spatial visualisation. Leiden clustering is currently the only
option; you can find more details in the report itself.

#### Spatially variable genes

<details markdown="1">
<summary>Output files</summary>

- `<SAMPLE>/reports/`
  - `spatially_variable_genes.html`: Rendered HTML report.
  - `spatially_variable_genes.yml`: YAML file containing parameters used in the report.
  - `spatially_variable_genes.qmd`: Quarto document used for rendering the report.

</details>

Report containing analyses related to differential expression testing and
spatially varying genes. The [Moran 1](https://en.wikipedia.org/wiki/Moran%27s_I)
score is currently the only option for spatial testing; you can find more
details in the report itself.

### Workflow reporting

#### Pipeline information

<details markdown="1">
<summary>Output files</summary>

- `pipeline_info/`
  - Reports generated by Nextflow: `execution_report.html`, `execution_timeline.html`, `execution_trace.txt` and `pipeline_dag.dot`/`pipeline_dag.svg`.
  - Reports generated by the pipeline: `pipeline_report.html`, `pipeline_report.txt` and `software_versions.yml`. The `pipeline_report*` files will only be present if the `--email` / `--email_on_fail` parameter's are used when running the pipeline.
  - Reformatted samplesheet files used as input to the pipeline: `samplesheet.valid.csv`.
  - Parameters used by the pipeline run: `params.json`.
- `multiqc/`
  - Report generated by MultiQC: `multiqc_report.html`.
  - Data and plots generated by MultiQC: `multiqc_data/` and `multiqc_plots/`.

</details>

[Nextflow](https://www.nextflow.io/docs/latest/tracing.html) provides excellent
functionality for generating various reports relevant to the running and
execution of the pipeline. This will allow you to troubleshoot errors with the
running of the pipeline, and also provide you with other information such as
launch commands, run times and resource usage.
