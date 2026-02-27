import marimo

__generated_with = "0.8.0"
app = marimo.create_app()


@app.cell
def __():
    import marimo as mo
    import ibis
    import ibis.expr.types as ibis_types
    import plotly.express as px
    import pandas as pd
    
    return mo, ibis, ibis_types, px, pd


@app.cell
def __(ibis):
    # Connect to the dlt-managed DuckDB database
    con = ibis.duckdb.connect('open_library_pipeline.duckdb')
    
    # List available tables
    tables = con.list_tables(database='open_library_data')
    print(f"Available tables: {tables}")
    
    return con


@app.cell
def __(con):
    # Access the books and authors tables
    books_table = con.table('books', database='open_library_data')
    authors_table = con.table('books__author_name', database='open_library_data')
    
    return books_table, authors_table


@app.cell
def __(authors_table):
    # Get the top 10 authors by book count
    top_authors = (
        authors_table
        .group_by('value')
        .aggregate(book_count=authors_table.value.count())
        .order_by(ibis.desc('book_count'))
        .limit(10)
        .execute()
    )
    
    # Rename columns for clarity
    top_authors = top_authors.rename(columns={'value': 'author_name'})
    
    return top_authors


@app.cell
def __(top_authors, px):
    # Create a bar chart visualization
    fig = px.bar(
        top_authors,
        x='author_name',
        y='book_count',
        title='Top 10 Authors by Book Count (Harry Potter Search)',
        labels={'author_name': 'Author', 'book_count': 'Number of Books'},
        color='book_count',
        color_continuous_scale='viridis',
        text='book_count'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_traces(textposition='outside')
    
    return fig


@app.cell
def __(mo, fig, top_authors):
    # Display the chart
    mo.vstack([
        mo.md("# Top 10 Authors - Harry Potter Books"),
        mo.md(f"*Data from Open Library API search results*"),
        fig,
        mo.md("### Data Table"),
        mo.ui.table(top_authors)
    ])


if __name__ == "__main__":
    app.run()
