doc_string = """
*******************************************************************************
Manual for BookDBTool
*******************************************************************************
{}*******************************************************************************
"""

doc_groups = {
    "ai": """
    chat(self, prompt: str) -> None
    clear_history(self) -> None
    show_history(self) -> None
    show_reply(self) -> None
""", "bc": """
    version(self)
    columns(self)
    tag_counts(self, tag=None, pagination=True)
    books_search(self, **query)
    tags_search(self, match_str, pagination=True, output=True)
    book(self, book_collection_id, pagination=True)
    books_read_by_year_with_summary(self, year=None, pagination=True)
    books_read_by_year(self, year=None, pagination=True)
    summary_books_read_by_year(self, year=None, show=True, pagination=True)
    year_rank(self, df=None, pages=True)
    add_books(self, n=1)
    add_books_by_isbn(self, book_isbn_list)
    add_read_books(self, book_collection_id_list)
    update_tag_value(self, tag_value, new_tag_value, pagination=True)
    add_tags(self, book_collection_id, tags=[])
""", "est": """
    version(self)
    new_book_estimate(self, book_id, total_readable_pages)
    list_book_estimates(self, book_id)
    add_page_date(self, record_id, page, date=None)
""", "isbn": """
    lookup(self, isbn=None)
"""
}

def pages(groups=["ai", "bc", "est", "isbn"]):
    groups_str = ""
    for group in groups:
        if group not in doc_groups:
            raise ValueError(f"Unknown group: {group}")
        else:
            groups_str += f'{group}...{doc_groups[group]}'
    print(doc_string.format(groups_str))