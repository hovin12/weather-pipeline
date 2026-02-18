import os
from src.db.connections import postgres_hook

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

DEFAULT_CITY = "Wrocław"
PAGE_TITLE = "Weather Report"  # Shown in browser tab and page header

HTML_OUTPUT_PATH = os.environ.get("HTML_OUTPUT_PATH", "/opt/airflow/data/html_output")

# ──────────────────────────────────────────────
# QUERIES
# ──────────────────────────────────────────────

MAIN_QUERY = """
    SELECT 
    run_ts AT TIME ZONE 'Europe/Paris',
    city,
    temp,
    perceived_temp,
    temp_min,
    temp_max,
    rain,
    snow,
    humidity,
    pressure,
    wind_speed,
    wind_deg,
    wind_gust,
    clouds,
    visibility,
    label,
    description,
    pressure_ground,
    timestamp,
    sunrise,
    sunset
    FROM weather
    WHERE run_ts >= ((SELECT MAX(run_ts) FROM weather) - INTERVAL '24 hours')
    ORDER BY run_ts DESC, city
"""

CITIES_QUERY = """
    SELECT DISTINCT city
    FROM cities
    ORDER BY city
"""


# ──────────────────────────────────────────────
# TASK CALLABLE
# ──────────────────────────────────────────────


def generate_html(**context):
    with postgres_hook().get_conn() as conn:
        cur = conn.cursor()
        cur.execute(MAIN_QUERY)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]  # column names from query

        cur.execute(CITIES_QUERY)
        cities = [row[0] for row in cur.fetchall()]

    # Find which column index holds the city value (matches "city" header)
    try:
        city_col_index = headers.index("city")
    except ValueError:
        raise ValueError("No column named 'city' found in MAIN_QUERY result.")

    os.makedirs(HTML_OUTPUT_PATH, exist_ok=True)

    html = _build_page(headers, rows, cities, city_col_index)

    output_file = os.path.join(HTML_OUTPUT_PATH, "index.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    # Make readable by nginx
    os.chmod(output_file, 0o644)  # rw-r--r--
    os.chmod(HTML_OUTPUT_PATH, 0o755)  # rwxr-xr-x

    print(f"[generate_html] Wrote {len(rows)} rows → {output_file}")


# ──────────────────────────────────────────────
# HTML BUILDER
# ──────────────────────────────────────────────


def _build_page(headers, rows, cities, city_col_index):
    generated_at = rows[0][0]  # run_ts

    # ── Table header ──
    headers_html = "".join(f"<th>{h}</th>" for h in headers)

    # ── Table rows — each <tr> carries data-city for JS filtering ──
    rows_html = ""
    for row in rows:
        city = row[city_col_index]
        cells = "".join(f"<td>{'' if cell is None else cell}</td>" for cell in row)
        rows_html += f'<tr data-city="{city}">{cells}</tr>\n'

    # ── Dropdown options ──
    options_html = '<option value="">All cities</option>\n'
    options_html += "\n".join(
        f'<option value="{c}"{"selected" if c == DEFAULT_CITY else ""}>{c}</option>'
        for c in cities
    )

    # JS-safe default city string (escape single quotes just in case)
    js_default_city = DEFAULT_CITY.replace("'", "\\'")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{PAGE_TITLE}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f5f7fa;
      color: #333;
      padding: 40px 24px;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    /* ── Header ── */
    header {{
      margin-bottom: 28px;
    }}

    h1 {{
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 4px;
    }}

    .meta {{
      font-size: 0.82rem;
      color: #999;
    }}

    /* ── Controls bar ── */
    .controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
    }}

    .controls label {{
      font-size: 0.875rem;
      font-weight: 500;
      color: #555;
    }}

    .controls select {{
      padding: 7px 10px;
      border: 1px solid #d0d5dd;
      border-radius: 6px;
      font-size: 0.875rem;
      background: #fff;
      cursor: pointer;
      min-width: 180px;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 10px center;
      padding-right: 28px;
    }}

    .controls select:focus {{
      outline: none;
      border-color: #4f7ef8;
      box-shadow: 0 0 0 3px rgba(79,126,248,0.15);
    }}

    .row-count {{
      margin-left: auto;
      font-size: 0.82rem;
      color: #999;
    }}

    /* ── Table card ── */
    .table-card {{
      background: #fff;
      border: 1px solid #e4e7ec;
      border-radius: 10px;
      overflow: hidden;
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
    }}

    thead th {{
      background: #f9fafb;
      padding: 11px 16px;
      text-align: left;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #666;
      border-bottom: 1px solid #e4e7ec;
      white-space: nowrap;
    }}

    tbody tr {{
      border-bottom: 1px solid #f0f2f5;
      transition: background 0.1s ease;
    }}

    tbody tr:last-child {{
      border-bottom: none;
    }}

    tbody tr:hover {{
      background: #f5f8ff;
    }}

    td {{
      padding: 10px 16px;
      white-space: nowrap;
    }}

    /* ── Hidden rows ── */
    tr.hidden {{
      display: none;
    }}

    /* ── Empty state ── */
    .empty-state {{
      display: none;
      padding: 48px 16px;
      text-align: center;
      color: #bbb;
      font-size: 0.9rem;
    }}
  </style>
</head>
<body>
  <div class="container">

    <header>
      <h1>{PAGE_TITLE}</h1>
      <p class="meta">Last updated: {generated_at}</p>
    </header>

    <div class="controls">
      <label for="city-filter">City</label>
      <select id="city-filter" onchange="filterByCity(this.value)">
        {options_html}
      </select>
      <span class="row-count" id="row-count"></span>
    </div>

    <div class="table-card">
      <table id="report-table">
        <thead>
          <tr>{headers_html}</tr>
        </thead>
        <tbody id="table-body">
          {rows_html}
        </tbody>
      </table>
      <div class="empty-state" id="empty-state">
        No rows found for the selected city.
      </div>
    </div>

  </div>

  <script>
    function filterByCity(city) {{
      const rows    = document.querySelectorAll('#table-body tr');
      let   visible = 0;

      rows.forEach(function(row) {{
        var match = !city || row.dataset.city === city;
        row.classList.toggle('hidden', !match);
        if (match) visible++;
      }});

      var total    = rows.length;
      var countEl  = document.getElementById('row-count');
      var emptyEl  = document.getElementById('empty-state');

      countEl.textContent = city
        ? visible + ' of ' + total + ' rows'
        : total + ' rows';

      emptyEl.style.display = (visible === 0) ? 'block' : 'none';
    }}

    // Apply default city on page load
    (function() {{
      var defaultCity = '{js_default_city}';
      var select = document.getElementById('city-filter');
      select.value = defaultCity;
      filterByCity(defaultCity);
    }})();
  </script>
</body>
</html>"""
