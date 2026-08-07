from __future__ import annotations

from io import StringIO

from bs4 import BeautifulSoup


def parse_html_tables(html: str) -> list[list[dict[str, str]]]:
    soup = BeautifulSoup(html, "html.parser")
    output: list[list[dict[str, str]]] = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        first = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(" ", strip=True) or f"column_{i + 1}" for i, cell in enumerate(first)]
        parsed: list[dict[str, str]] = []
        for row in rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
            if not cells:
                continue
            cells.extend([""] * (len(headers) - len(cells)))
            parsed.append(dict(zip(headers, cells[:len(headers)], strict=True)))
        if parsed:
            output.append(parsed)
    return output


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    return "\n".join(line.strip() for line in StringIO(soup.get_text("\n")).readlines() if line.strip())
