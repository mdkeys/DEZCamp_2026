import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    import pandas

    conn = duckdb.connect('open_library_pipeline.duckdb', read_only=True)
    top_authors = conn.execute("""
        SELECT 
            value as author_name,
            COUNT(DISTINCT _dlt_parent_id) as book_count
        FROM open_library_data.books__author_name
        GROUP BY value
        ORDER BY book_count DESC
        LIMIT 10
    """).fetch_df()

    print(top_authors)
    return (top_authors,)


@app.cell
def _(top_authors):
    import plotly.express as px

    # Create an interactive bar chart
    fig = px.bar(
        top_authors,
        x='author_name',
        y='book_count',
        title='Top 10 Authors by Book Count (Harry Potter Search)',
        labels={'author_name': 'Author Name', 'book_count': 'Number of Books'},
        color='book_count',
        color_continuous_scale='viridis',
        text='book_count'
    )

    # Customize the layout
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False,
        hovermode='x unified'
    )

    # Position text labels outside the bars
    fig.update_traces(textposition='outside')

    # Display the chart
    fig.show()
    return


if __name__ == "__main__":
    app.run()
