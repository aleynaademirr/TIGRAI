import sqlite3
db_path = "recommendation_system.db"
conn = sqlite3.connect(db_path)
movies_csv = "movies_metadata.csv"
movies_df = pd.read_csv(movies_csv, low_memory=False)
movies_df.to_sql("movies", conn, if_exists="replace", index=False)
print("Filmler başarıyla SQLite'a aktarıldı.")
shows_csv = "netflix_titles.csv"
shows_df = pd.read_csv(shows_csv)
shows_df.to_sql("shows", conn, if_exists="replace", index=False)
print("Diziler başarıyla SQLite'a aktarıldı.")
books_csv = "books.csv"
books_df = pd.read_csv(books_csv, on_bad_lines='skip', engine='python')
books_df.to_sql("books", conn, if_exists="replace", index=False)
print("Kitaplar başarıyla SQLite'a aktarıldı.")
conn.close()