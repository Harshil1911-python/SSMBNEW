def register_filters(app):

    @app.template_filter("currency")
    def currency_filter(value):
        if value is None:
            return "-"
        try:
            return f"\u20b9{float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value)

    @app.template_filter("dateformat")
    def dateformat_filter(value, fmt="%d %b %Y"):
        """Usage: {{ value|dateformat }} or {{ value|dateformat('%d %b %Y %H:%M') }}"""
        if not value:
            return "-"
        try:
            return value.strftime(fmt)
        except Exception:
            return str(value)

    @app.template_filter("yesno")
    def yesno_filter(value):
        return "Yes" if value else "No"

    @app.template_filter("truncate_words")
    def truncate_words_filter(value, num=20):
        if not value:
            return ""
        words = str(value).split()
        if len(words) <= num:
            return value
        return " ".join(words[:num]) + "…"
