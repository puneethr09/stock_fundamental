"""Export service for generating multi-format export files.

Start with a small CSV-focused implementation usable by tests and a lightweight
Flask endpoint.
"""

from typing import List, Dict, Any
import csv
import io


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
