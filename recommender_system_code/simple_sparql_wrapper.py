from pathlib import Path

from rdflib import Graph


class SimpleDanceKG:
    """Tiny wrapper around a local Turtle knowledge graph with SPARQL queries."""

    def __init__(self, ttl_path=None):
        if ttl_path is None:
            base_dir = Path(__file__).resolve().parents[1]
            ttl_path = base_dir / "kg_code" / "dance_kg_merged_with_yt.ttl"

        self.ttl_path = Path(ttl_path)
        if not self.ttl_path.exists():
            raise FileNotFoundError(f"KG file not found: {self.ttl_path}")

        self.graph = Graph()
        self.graph.parse(self.ttl_path, format="turtle")

    def select(self, query):
        """Run a SELECT query and return a list of dict rows (string values)."""
        rows = []
        for row in self.graph.query(query):
            row_data = {}
            for var in row.labels:
                value = row[var]
                row_data[str(var)] = str(value) if value is not None else None
            rows.append(row_data)
        return rows

    def top_dance_styles(self, limit=5):
        """Convenience query: return dance styles from records."""
        query = f"""
        PREFIX dance: <http://example.org/dance/>
        PREFIX schema1: <http://schema.org/>

        SELECT DISTINCT ?styleName WHERE {{
          ?record a dance:DanceRecord ;
                  dance:hasDanceStyle ?style .
          ?style schema1:name ?styleName .
        }}
        ORDER BY ?styleName
        LIMIT {int(limit)}
        """
        return self.select(query)

    def dance_style_details(self, style_name, filters=None, limit=10):
        """Return records that match a dance style label, with optional dynamic filters.

        filters: list of (property, value) tuples, e.g.:
            [("dance:hardness", "beginner"), ("dance:origin", "Latin")]
        Each pair adds an OPTIONAL binding + FILTER clause to the query.
        Passing an empty list or None returns all records for the style.
        """
        safe_style = str(style_name).replace("'", "\\'")
        filters = filters or []

        # Build one OPTIONAL + FILTER block per (property, value) pair
        filter_blocks = ""
        for i, (prop, val) in enumerate(filters):
            var = f"filterVal{i}"
            safe_val = str(val).replace("'", "\\'")
            filter_blocks += (
                f"  OPTIONAL {{ ?record {prop} ?{var} . }}\n"
                f"  FILTER(!BOUND(?{var}) || LCASE(STR(?{var})) = LCASE('{safe_val}'))\n"
            )

        # SELECT all filter variables so callers can see the matched values
        extra_vars = " ".join(f"?filterVal{i}" for i in range(len(filters)))

        query = f"""
        PREFIX dance: <http://example.org/dance/>
        PREFIX schema1: <http://schema.org/>

        SELECT ?styleName ?record {extra_vars} WHERE {{
          ?record a dance:DanceRecord ;
                  dance:hasDanceStyle ?style .
          ?style schema1:name ?styleName .
          FILTER(LCASE(STR(?styleName)) = LCASE('{safe_style}'))
{filter_blocks}        }}
        LIMIT {int(limit)}
        """
        return self.select(query)
