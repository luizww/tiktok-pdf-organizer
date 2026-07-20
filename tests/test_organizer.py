import tempfile
import unittest
from pathlib import Path

import fitz
from pypdf import PdfReader

from tiktok_pdf_organizer.organizer import PdfMappingError, organize_pdfs


TRACKING_A = "3320000000001"
TRACKING_B = "3320000000002"
TRACKING_C = "3320000000003"
TRACKING_D = "3320000000004"


class OrganizerTests(unittest.TestCase):
    def _create_pdf(self, path: Path, pages: list[str]) -> None:
        with fitz.open() as document:
            for text in pages:
                page = document.new_page()
                page.insert_text((72, 72), text, fontsize=12)
            document.save(path)

    def test_pairs_exact_tracking_and_preserves_label_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            labels = directory / "labels.pdf"
            danfes = directory / "danfes.pdf"
            output = directory / "output.pdf"

            self._create_pdf(
                labels,
                [
                    f"ETIQUETA A tracking {TRACKING_A}",
                    f"ETIQUETA B tracking {TRACKING_B}",
                    f"ETIQUETA C tracking {TRACKING_C}",
                ],
            )
            # DANFEs propositalmente fora da ordem das etiquetas.
            self._create_pdf(
                danfes,
                [
                    f"DANFE B tracking {TRACKING_B}",
                    f"DANFE A tracking {TRACKING_A}",
                    f"DANFE D tracking {TRACKING_D}",
                ],
            )

            result = organize_pdfs(labels, danfes, output)
            output_texts = [
                page.extract_text().strip()
                for page in PdfReader(output).pages
            ]

            self.assertEqual(result.pairs, 2)
            self.assertEqual(result.unmatched_labels, (TRACKING_C,))
            self.assertEqual(result.unmatched_danfes, (TRACKING_D,))
            self.assertEqual(
                output_texts,
                [
                    f"ETIQUETA A tracking {TRACKING_A}",
                    f"DANFE A tracking {TRACKING_A}",
                    f"ETIQUETA B tracking {TRACKING_B}",
                    f"DANFE B tracking {TRACKING_B}",
                ],
            )

    def test_accepts_same_tracking_repeated_on_one_page(self) -> None:
        """Etiquetas reais podem imprimir o mesmo código mais de uma vez."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            labels = directory / "labels.pdf"
            danfes = directory / "danfes.pdf"
            output = directory / "output.pdf"

            self._create_pdf(
                labels,
                [f"TOPO {TRACKING_A}\nRODAPÉ {TRACKING_A}"],
            )
            self._create_pdf(
                danfes,
                [f"Tracking Number: {TRACKING_A}"],
            )

            result = organize_pdfs(labels, danfes, output)

            self.assertEqual(result.pairs, 1)
            self.assertEqual(len(PdfReader(output).pages), 2)

    def test_rejects_two_different_trackings_on_one_page(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            labels = directory / "labels.pdf"
            danfes = directory / "danfes.pdf"
            output = directory / "output.pdf"

            self._create_pdf(
                labels,
                [f"ETIQUETA {TRACKING_A} OUTRO PEDIDO {TRACKING_B}"],
            )
            self._create_pdf(danfes, [f"DANFE {TRACKING_A}"])

            with self.assertRaises(PdfMappingError):
                organize_pdfs(labels, danfes, output)

    def test_reports_pages_without_tracking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            labels = directory / "labels.pdf"
            danfes = directory / "danfes.pdf"
            output = directory / "output.pdf"

            self._create_pdf(labels, [f"ETIQUETA {TRACKING_A}", "SEM CODIGO"])
            self._create_pdf(danfes, ["SEM CODIGO", f"DANFE {TRACKING_A}"])

            result = organize_pdfs(labels, danfes, output)

            self.assertEqual(result.label_pages_without_tracking, (2,))
            self.assertEqual(result.danfe_pages_without_tracking, (1,))

    def test_rejects_duplicate_tracking_across_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            labels = directory / "labels.pdf"
            danfes = directory / "danfes.pdf"
            output = directory / "output.pdf"

            self._create_pdf(
                labels,
                [f"ETIQUETA 1 {TRACKING_A}", f"ETIQUETA 2 {TRACKING_A}"],
            )
            self._create_pdf(danfes, [f"DANFE {TRACKING_A}"])

            with self.assertRaises(PdfMappingError):
                organize_pdfs(labels, danfes, output)


if __name__ == "__main__":
    unittest.main()
