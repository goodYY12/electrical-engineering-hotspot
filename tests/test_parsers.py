from electrical_kaoyan.parsers.html import extract_visible_text, parse_html_tables


def test_html_table_parser():
    html = """<table><tr><th>专业代码</th><th>计划</th></tr>
    <tr><td>085801</td><td>37</td></tr></table>"""
    assert parse_html_tables(html) == [[{"专业代码": "085801", "计划": "37"}]]


def test_visible_text_ignores_scripts():
    assert extract_visible_text("<p>招生公告</p><script>bad()</script>") == "招生公告"
