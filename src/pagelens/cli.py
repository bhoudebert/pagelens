from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Never

import typer
from rich.console import Console
from rich.table import Table

from pagelens import __version__
from pagelens.adapters.embedding_ollama import OllamaMultimodalEmbedder
from pagelens.adapters.ollama import OllamaVerifier
from pagelens.adapters.pdf_pymupdf import PyMuPdfRegionExtractor
from pagelens.adapters.store_sqlite import SQLiteRegionStore
from pagelens.application.evaluate import compare_results, load_ground_truth
from pagelens.application.ingest import IngestDocuments, discover_pdfs
from pagelens.application.query import SearchCollection
from pagelens.config import Settings
from pagelens.domain.models import EvidenceMode, SearchResult

NIX_NOTE = (
    "Running through Nix? Put '--' after the flake reference so Nix passes options on to "
    "pagelens: nix run path:. -- query --help"
)

app = typer.Typer(
    no_args_is_help=True,
    help="Find visual and textual evidence in local PDF collections.",
    epilog=NIX_NOTE,
)
console = Console()
error_console = Console(stderr=True)

DataOption = Annotated[
    Path | None,
    typer.Option("--data-dir", help="Collection directory (default: .pagelens)."),
]


def _version_callback(value: bool) -> None:
    if value:
        console.print(__version__)
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    """Local multimodal search over PDF pages."""


@app.command("init")
def init_collection(data_dir: DataOption = None) -> None:
    """Create an empty local collection.

    \b
    Examples:
      pagelens init
      nix run path:. -- init --data-dir .pagelens-test
    """
    settings = Settings.from_env(data_dir)
    settings.ensure_directories()
    SQLiteRegionStore(settings.database_path).initialize()
    console.print(f"Initialized collection at [bold]{settings.data_dir.resolve()}[/bold]")


@app.command()
def status(data_dir: DataOption = None) -> None:
    """Show collection size and embedding compatibility.

    \b
    Examples:
      pagelens status
      nix run path:. -- status
    """
    settings = Settings.from_env(data_dir)
    stats = SQLiteRegionStore(settings.database_path).stats()
    console.print(f"Collection: {settings.data_dir.resolve()}")
    console.print(f"Documents: {stats.documents}")
    console.print(f"Pages: {stats.pages}")
    console.print(f"Regions: {stats.regions}")
    console.print(f"Embedding models: {', '.join(stats.embedding_models) or '(none)'}")


@app.command()
def ingest(
    path: Annotated[Path, typer.Argument(help="PDF file or directory searched recursively.")],
    data_dir: DataOption = None,
    model: Annotated[
        str | None,
        typer.Option(help="Ollama multimodal embedding model."),
    ] = None,
    ocr: Annotated[
        bool,
        typer.Option("--ocr/--no-ocr", help="OCR pages without native text."),
    ] = True,
) -> None:
    """Render and index PDFs using shared image/text embeddings.

    \b
    Examples:
      pagelens ingest ./manuals
      nix run path:. -- ingest testdata/manuals --no-ocr
    """
    settings = Settings.from_env(data_dir)
    settings.ensure_directories()
    try:
        sources = discover_pdfs(path)
    except (FileNotFoundError, ValueError) as error:
        _fail(str(error))
    if not sources:
        _fail(f"no PDFs found under {path}")

    selected_model = model or settings.embedding_model
    store = SQLiteRegionStore(settings.database_path)
    use_case = IngestDocuments(
        extractor=PyMuPdfRegionExtractor(
            dpi=settings.render_dpi,
            tile_size=settings.tile_size,
            overlap=settings.tile_overlap,
            enable_ocr=ocr,
        ),
        embedder=OllamaMultimodalEmbedder(settings.ollama_url, selected_model),
        store=store,
        preview_root=settings.preview_dir,
        progress=lambda document: console.print(
            f"Indexed [bold]{document.source_path.name}[/bold] ({document.page_count} pages)"
        ),
    )
    report = use_case.execute(sources)
    console.print(
        f"Done: {report.documents} document(s), {report.pages} page(s), {report.regions} region(s)."
    )


@app.command()
def query(
    text: Annotated[str | None, typer.Argument(help="What to find.")] = None,
    image: Annotated[
        list[Path] | None,
        typer.Option("--image", "-i", help="Reference image; repeat for multiple views."),
    ] = None,
    data_dir: DataOption = None,
    model: Annotated[
        str | None,
        typer.Option(help="Embedding model used for this collection."),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=500)] = 20,
    verify: Annotated[
        bool, typer.Option("--verify", help="Verify candidates with the configured Ollama VLM.")
    ] = False,
    evidence: Annotated[
        EvidenceMode,
        typer.Option(
            "--evidence",
            help=(
                "Evidence allowed for confirmation: visual requires a depicted object; "
                "any also accepts text."
            ),
        ),
    ] = EvidenceMode.VISUAL,
    all_regions: Annotated[
        bool,
        typer.Option(
            "--all-regions",
            help="Show overlapping region candidates instead of one result per PDF page.",
        ),
    ] = False,
    include_rejected: Annotated[
        bool,
        typer.Option(
            "--include-rejected",
            help="Keep candidates rejected by the verifier in the output.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable JSON."),
    ] = False,
) -> None:
    """Search with text, reference images, or both.

    \b
    Examples:
      pagelens query "water pump"
      pagelens query --image part.jpg
      pagelens query "same pump" --image part.jpg --verify
      nix run path:. -- query "find me motorcycle" --verify

    \b
    With Nix, keep the '--' before query. Without it Nix itself rejects
    options such as --verify ("unrecognised flag").
    """
    settings = Settings.from_env(data_dir)
    selected_model = model or settings.embedding_model
    verifier = (
        OllamaVerifier(settings.ollama_url, settings.ollama_model, evidence_mode=evidence)
        if verify
        else None
    )
    use_case = SearchCollection(
        embedder=OllamaMultimodalEmbedder(settings.ollama_url, selected_model),
        store=SQLiteRegionStore(settings.database_path),
        verifier=verifier,
    )
    try:
        results = use_case.execute(
            text,
            image or [],
            limit,
            verify,
            group_by_page=not all_regions,
        )
        rejected_count = sum(
            result.verification is not None and result.verification.status == "rejected"
            for result in results
        )
        if verify and not include_rejected:
            results = [
                result
                for result in results
                if result.verification is None or result.verification.status != "rejected"
            ]
        results.sort(key=_display_rank, reverse=True)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        _fail(str(error))
    if json_output:
        console.print_json(json.dumps([_result_dict(result) for result in results]))
    else:
        _print_results(results)
        if verify and rejected_count and not include_rejected:
            console.print(
                f"Hidden {rejected_count} rejected candidate(s); "
                "use --include-rejected to inspect them."
            )


@app.command()
def evaluate(
    ground_truth: Annotated[
        Path,
        typer.Argument(help="Page-level ground-truth JSON file."),
    ] = Path("testdata/ground-truth.json"),
    data_dir: DataOption = None,
    model: Annotated[
        str | None,
        typer.Option(help="Embedding model used for this collection."),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=500)] = 20,
    verify: Annotated[
        bool,
        typer.Option(
            "--verify/--no-verify",
            help="Evaluate confirmed VLM decisions instead of retrieval recall only.",
        ),
    ] = False,
    scenario_ids: Annotated[
        list[str] | None,
        typer.Option("--scenario", help="Scenario ID to run; repeat to select several."),
    ] = None,
) -> None:
    """Compare indexed search results with page-level ground truth.

    \b
    Examples:
      pagelens evaluate testdata/ground-truth.json
      nix run path:. -- evaluate testdata/ground-truth.json --verify --scenario motorcycle-visual
    """
    settings = Settings.from_env(data_dir)
    selected_model = model or settings.embedding_model
    try:
        truth = load_ground_truth(ground_truth)
        requested = set(scenario_ids or [])
        scenarios = [
            scenario for scenario in truth.queries if not requested or scenario.id in requested
        ]
        unknown = requested - {scenario.id for scenario in truth.queries}
        if unknown:
            raise ValueError(f"unknown scenario(s): {', '.join(sorted(unknown))}")

        table = Table(title="Ground-truth verification" if verify else "Ground-truth retrieval")
        table.add_column("Scenario")
        table.add_column("Evidence")
        table.add_column("Recall", justify="right")
        table.add_column("Result")
        table.add_column("Problems")
        passed = True
        for scenario in scenarios:
            verifier = (
                OllamaVerifier(
                    settings.ollama_url,
                    settings.ollama_model,
                    evidence_mode=scenario.evidence,
                )
                if verify
                else None
            )
            results = SearchCollection(
                embedder=OllamaMultimodalEmbedder(settings.ollama_url, selected_model),
                store=SQLiteRegionStore(settings.database_path),
                verifier=verifier,
            ).execute(scenario.text, [], limit, verify)
            outcome = compare_results(scenario, results, verified=verify)
            passed = passed and outcome.passed
            problems = []
            if outcome.missing:
                problems.append(f"missing: {_format_page_keys(outcome.missing)}")
            if outcome.forbidden:
                problems.append(f"wrongly confirmed: {_format_page_keys(outcome.forbidden)}")
            table.add_row(
                scenario.id,
                scenario.evidence.value,
                f"{len(outcome.matched)}/{len(scenario.relevant)}",
                "PASS" if outcome.passed else "FAIL",
                "; ".join(problems) or "-",
            )
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        _fail(str(error))

    console.print(table)
    if not verify:
        console.print(
            "Retrieval mode checks recall only. Re-run with --verify to test confirmations "
            "and forbidden matches."
        )
    if not passed:
        raise typer.Exit(code=1)


def _result_dict(result: SearchResult) -> dict[str, object]:
    payload: dict[str, object] = {
        "pdf": str(result.source_path),
        "page": result.page,
        "bbox": result.bbox.model_dump(),
        "score": round(result.score, 6),
        "visual_score": round(result.visual_score, 6),
        "lexical_rank": result.lexical_rank,
        "preview": str(result.preview_path),
        "text": result.text,
    }
    if result.verification:
        payload["verification"] = result.verification.model_dump()
    return payload


def _print_results(results: list[SearchResult]) -> None:
    if not results:
        console.print("No compatible indexed regions found.")
        return
    table = Table(title=f"{len(results)} result(s)")
    table.add_column("Relevance", justify="right")
    table.add_column("PDF")
    table.add_column("Page (1-based)", justify="right")
    table.add_column("Result")
    table.add_column("Evidence")
    table.add_column("Preview")
    for result in results:
        verification = result.verification.status if result.verification else "candidate"
        evidence = _evidence_summary(result)
        table.add_row(
            f"{result.score:.3f}",
            result.source_path.name,
            str(result.page),
            verification,
            evidence,
            result.preview_path.name,
        )
    console.print(table)
    console.print("Scores rank candidates; use --verify for object confirmation and metadata.")


def _evidence_summary(result: SearchResult) -> str:
    if result.verification:
        fields = [
            result.verification.object_type,
            result.verification.manufacturer,
            result.verification.model,
            result.verification.reference,
        ]
        supported = [field for field in fields if field]
        if supported:
            return " · ".join(supported)
        if result.verification.evidence:
            return result.verification.evidence[0][:60]
    compact_text = " ".join(result.text.split())
    return compact_text[:60] or "visual match"


def _display_rank(result: SearchResult) -> tuple[int, float]:
    status_rank = {
        None: 1,
        "rejected": 0,
        "uncertain": 2,
        "confirmed": 3,
    }
    status = result.verification.status if result.verification else None
    return status_rank[status], result.score


def _format_page_keys(keys: frozenset[tuple[str, int]]) -> str:
    return ", ".join(f"{pdf}:p{page}" for pdf, page in sorted(keys))


def _fail(message: str) -> Never:
    error_console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
