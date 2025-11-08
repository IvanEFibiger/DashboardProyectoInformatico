# api/utils/date_range.py
from datetime import datetime, timedelta

def parse_from_to(args):
    """
    Lee query params 'from' y 'to' (YYYY-MM-DD o ISO).
    Devuelve tupla (from_dt_sql, to_dt_sql) para usar en BETWEEN inclusivo.
    Si no vienen, retorna (None, None).
    """
    f = args.get("from", "").strip() or None
    t = args.get("to", "").strip() or None
    from_dt_sql = to_dt_sql = None

    def _parse_any(s: str) -> datetime:
        if len(s) == 10:

            return datetime.strptime(s, "%Y-%m-%d")
        return datetime.fromisoformat(s)

    if f:
        d = _parse_any(f)
        from_dt_sql = d.strftime("%Y-%m-%d 00:00:00")

    if t:
        d = _parse_any(t)

        to_dt_sql = (d + timedelta(days=1) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")

    return from_dt_sql, to_dt_sql
