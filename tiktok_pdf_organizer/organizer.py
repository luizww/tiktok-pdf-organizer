"""Pareamento de páginas de etiquetas e DANFEs pelo mesmo tracking."""

from dataclasses import dataclass
from pathlib import Path

import fitz
from pypdf import PdfReader, PdfWriter

from .tracking import extract_trackings


class PdfMappingError(ValueError):
    """Erro quando o conteúdo de um PDF não permite pareamento seguro."""


@dataclass(frozen=True)
class PdfIndex:
    """Índice de páginas por tracking e páginas sem código reconhecido."""

    pages_by_tracking: dict[str, int]
    pages_without_tracking: tuple[int, ...]


@dataclass(frozen=True)
class OrganizationResult:
    """Resumo do processamento dos dois documentos."""

    pairs: int
    unmatched_labels: tuple[str, ...]
    unmatched_danfes: tuple[str, ...]
    label_pages_without_tracking: tuple[int, ...]
    danfe_pages_without_tracking: tuple[int, ...]


def _validate_pdf(path: str | Path, description: str) -> Path:
    pdf_path = Path(path).expanduser()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"{description} não encontrado: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"{description} precisa ser um arquivo PDF.")
    return pdf_path


def index_pdf(path: str | Path, description: str) -> PdfIndex:
    """Mapeia cada tracking para uma única página do PDF."""

    pdf_path = _validate_pdf(path, description)
    pages_by_tracking: dict[str, int] = {}
    pages_without_tracking: list[int] = []

    with fitz.open(pdf_path) as document:
        if document.needs_pass:
            raise PdfMappingError(f"{description} está protegido por senha.")

        for page_index, page in enumerate(document):
            page_number = page_index + 1
            trackings = extract_trackings(page.get_text("text"))

            if not trackings:
                pages_without_tracking.append(page_number)
                continue

            if len(trackings) > 1:
                codes = ", ".join(trackings)
                raise PdfMappingError(
                    f"A página {page_number} de {description} contém mais de "
                    f"um tracking reconhecido: {codes}."
                )

            tracking = trackings[0]
            if tracking in pages_by_tracking:
                previous_page = pages_by_tracking[tracking] + 1
                raise PdfMappingError(
                    f"O tracking {tracking} aparece repetido em {description}: "
                    f"páginas {previous_page} e {page_number}."
                )

            pages_by_tracking[tracking] = page_index

    return PdfIndex(
        pages_by_tracking=pages_by_tracking,
        pages_without_tracking=tuple(pages_without_tracking),
    )


def organize_pdfs(
    labels_pdf: str | Path,
    danfes_pdf: str | Path,
    output_pdf: str | Path,
) -> OrganizationResult:
    """Gera um PDF alternando etiqueta e DANFE com o mesmo tracking.

    A ordem das etiquetas é preservada. A ordem original dos DANFEs não
    interfere no resultado porque cada página é localizada pelo tracking.
    """

    labels_path = _validate_pdf(labels_pdf, "PDF de etiquetas")
    danfes_path = _validate_pdf(danfes_pdf, "PDF de DANFEs")
    output_path = Path(output_pdf).expanduser()

    if output_path.resolve() in {labels_path.resolve(), danfes_path.resolve()}:
        raise ValueError("O arquivo final não pode substituir um PDF de entrada.")

    labels_index = index_pdf(labels_path, "PDF de etiquetas")
    danfes_index = index_pdf(danfes_path, "PDF de DANFEs")

    matching_trackings = tuple(
        tracking
        for tracking in labels_index.pages_by_tracking
        if tracking in danfes_index.pages_by_tracking
    )

    if not matching_trackings:
        raise PdfMappingError(
            "Nenhum tracking igual foi encontrado entre as etiquetas e os DANFEs."
        )

    labels_reader = PdfReader(labels_path)
    danfes_reader = PdfReader(danfes_path)
    writer = PdfWriter()

    for tracking in matching_trackings:
        writer.add_page(
            labels_reader.pages[labels_index.pages_by_tracking[tracking]]
        )
        writer.add_page(
            danfes_reader.pages[danfes_index.pages_by_tracking[tracking]]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output_file:
        writer.write(output_file)

    unmatched_labels = tuple(
        tracking
        for tracking in labels_index.pages_by_tracking
        if tracking not in danfes_index.pages_by_tracking
    )
    unmatched_danfes = tuple(
        tracking
        for tracking in danfes_index.pages_by_tracking
        if tracking not in labels_index.pages_by_tracking
    )

    return OrganizationResult(
        pairs=len(matching_trackings),
        unmatched_labels=unmatched_labels,
        unmatched_danfes=unmatched_danfes,
        label_pages_without_tracking=labels_index.pages_without_tracking,
        danfe_pages_without_tracking=danfes_index.pages_without_tracking,
    )
