"""Export service for generating multi-format export files.

Start with a small CSV-focused implementation usable by tests and a lightweight
Flask endpoint.
"""

from typing import List, Dict, Any
import csv
import io
import base64

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class ExportService:
    """Small export helper that converts lists of dicts into CSV text.

    This scaffold focuses on correctness and predictable output for tests.
    More formats (Excel/PDF) can be added later.
    """

    @staticmethod
    def generate_csv(rows: List[Dict[str, Any]]) -> str:
        """Return CSV text for the given rows (list of dicts).

        - If rows is empty, returns an empty string.
        - Uses the keys of the first row as header order.
        """
        if not rows:
            return ""

        output = io.StringIO()
        # Preserve header order from first row
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Normalize values to simple types
            safe_row = {k: ("" if v is None else v) for k, v in row.items()}
            writer.writerow(safe_row)

        return output.getvalue()

    @staticmethod
    def generate_excel_bytes(rows: List[Dict[str, Any]]) -> bytes:
        """Return XLSX file bytes for the given rows.

        Uses pandas to create an Excel workbook in-memory. If rows is empty,
        returns an empty bytes object.
        """
        if not rows:
            return b""

        df = pd.DataFrame(rows)
        buffer = io.BytesIO()
        # Prefer openpyxl engine; let pandas pick the default if not available
        try:
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Export")
        except Exception:
            # Fallback to default engine
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False, sheet_name="Export")

        return buffer.getvalue()

    @staticmethod
    def generate_pdf_bytes(rows: List[Dict[str, Any]], title: str = "Export") -> bytes:
        """Generate a simple PDF report (one page) containing a table and a small chart.

        Returns PDF bytes. If rows empty, returns a minimal PDF with a title.
        """
        buffer = io.BytesIO()
        # Create a PDF with matplotlib PdfPages
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 portrait
            ax.axis("off")

            # Title
            ax.set_title(title, fontsize=16, pad=20)

            if rows:
                # Build table data: header + rows (stringified)
                headers = list(rows[0].keys())
                table_data = [headers]
                for r in rows:
                    table_data.append([str(r.get(h, "")) for h in headers])

                # Draw table
                table = ax.table(cellText=table_data, loc="center", cellLoc="left")
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 1)

                # Create a tiny bar chart if numeric columns exist
                numeric_cols = []
                for h in headers:
                    try:
                        float(rows[0].get(h))
                        numeric_cols.append(h)
                    except Exception:
                        continue

                if numeric_cols:
                    # Create separate figure for chart
                    fig2, ax2 = plt.subplots(figsize=(6, 3))
                    # Use first numeric column for a simple chart
                    col = numeric_cols[0]
                    values = []
                    labels = []
                    for r in rows:
                        try:
                            values.append(float(r.get(col, 0)))
                            labels.append(str(r.get(list(rows[0].keys())[0], "")))
                        except Exception:
                            pass
                    if values:
                        ax2.bar(range(len(values)), values)
                        ax2.set_title(f"{col} (sample)")
                        pdf.savefig(fig2)
                        plt.close(fig2)

            pdf.savefig(fig)
            plt.close(fig)

        buffer.seek(0)
        return buffer.getvalue()
