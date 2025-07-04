import pandas as pd
import numpy as np

# Učitavanje dataseta
try:
    df = pd.read_csv('online_store_data.csv')
except FileNotFoundError:
    print("Greška: Datoteka 'online_store_data.csv' nije pronađena.")
    print("Provjerite je li datoteka u istom direktoriju kao i skripta.")
    exit()

print("Dataset uspješno učitan.")
print("Prvih 5 redova:")
print(df.head())
print("\nInformacije o kolonama:")
print(df.info())
print("\nStatistički sažetak:")
print(df.describe())

# Pitanje 1: Kolika je razlika između najbolje i najlošije ocijenjenog televizora?
# Koristim opseg (range = max - min)

print("\n--- Pitanje 1: Razlika između najbolje i najlošije ocijenjenog televizora ---")
# Filtriranje proizvoda po kategoriji 'TVs'
tvs_df = df[df['category'] == 'TVs']

if not tvs_df.empty:
    # Pronalaženje minimalne i maksimalne ocjene (rating)
    min_rating_tvs = tvs_df['rating'].min()
    max_rating_tvs = tvs_df['rating'].max()
# Izračunavanje opsega
    range_tvs = max_rating_tvs - min_rating_tvs

    print(f"Minimalna ocjena za televizore: {min_rating_tvs}")
    print(f"Maksimalna ocjena za televizore: {max_rating_tvs}")
    print(f"Razlika između najbolje i najlošije ocijenjenog televizora (opseg): {range_tvs:.2f}")
else:
    print("Nema pronađenih proizvoda u kategoriji 'TVs'.")

# Izračunati interkvartilni opseg (IQR)

print("\n--- Pitanje 2: Cjenovni rang najprodavanijih pametnih telefona (IQR) ---")
# Filtriranje proizvoda po kategoriji 'Smartphones'
smartphones_df = df[df['category'] == 'Smartphones']

if not smartphones_df.empty:
    # Nema direktne veze između prodaje i IQR cijene, IQR je za cijelu distribuciju cijena smartfona.
    Q1_price = smartphones_df['price'].quantile(0.25)
    Q3_price = smartphones_df['price'].quantile(0.75)
    IQR_price = Q3_price - Q1_price

    print(f"Prvi kvartil cijena pametnih telefona (Q1): {Q1_price:.2f}")
    print(f"Treći kvartil cijena pametnih telefona (Q3): {Q3_price:.2f}")
    print(f"Interkvartilni opseg (IQR) cijena pametnih telefona: {IQR_price:.2f}")
    print(f"To znači da se 50% srednjih cijena pametnih telefona kreće u rasponu od {Q1_price:.2f} do {Q3_price:.2f}.")
# Da bismo vidjeli gdje se nalaze najprodavaniji:
    most_sold_smartphone = smartphones_df.loc[smartphones_df['quantity_sold'].idxmax()]
    print(f"\nNajprodavaniji pametni telefon: {most_sold_smartphone['product_name']} (Cijena: {most_sold_smartphone['price']:.2f}, Prodano: {most_sold_smartphone['quantity_sold']})")
    if Q1_price <= most_sold_smartphone['price'] <= Q3_price:
        print(f"Najprodavaniji pametni telefon se nalazi unutar interkvartilnog opsega cijena.")
    else:
        print(f"Najprodavaniji pametni telefon se NE nalazi unutar interkvartilnog opsega cijena.")


else:
    print("Nema pronađenih proizvoda u kategoriji 'Smartphones'.")
# Pitanje 3: Kojih 5 brendova imaju najujednačenije ocjene?
# Izračunati standardnu devijaciju ocjena

print("\n--- Pitanje 3: 5 brendova sa najujednačenijim ocjenama ---")
# Grupiranje po brendu i izračunavanje standardne devijacije ocjena
brand_std_dev = df.groupby('brand')['rating'].std().reset_index()

# Sortiranje po standardnoj devijaciji (uzlazno - manja SD znači ujednačenije ocjene)
# Ukloni brendove koji imaju samo jednu ocjenu (SD bi bila NaN)
brand_std_dev = brand_std_dev.dropna()
brand_std_dev_sorted = brand_std_dev.sort_values(by='rating', ascending=True)
# Uzimanje top 5 brendova
top_5_uniform_brands = brand_std_dev_sorted.head(5)

if not top_5_uniform_brands.empty:
    print("5 brendova sa najujednačenijim ocjenama (najmanja standardna devijacija):")
    for index, row in top_5_uniform_brands.iterrows():
        print(f"- Brend: {row['brand']}, Standardna devijacija ocjena: {row['rating']:.2f}")
else:
    print("Nema dovoljno podataka za analizu standardne devijacije ocjena po brendu.")
# pitanje 4 Kvantilima (kvartila) podeliti proizvode prema broju ocjena

print("\n--- Pitanje 4: Ovisnost broja ocjena o broju prodanih jedinica ---")

# Podjela proizvoda prema broju ocjena (num_ratings) na 4 kvartila
df['num_ratings'] = pd.to_numeric(df['num_ratings'], errors='coerce')
df_cleaned = df.dropna(subset=['num_ratings'])

if not df_cleaned.empty:
   df_cleaned['rating_quartile'] = pd.qcut(df_cleaned['num_ratings'], q=4, labels=['1st quartile', '2nd quartile', '3rd quartile', '4th quartile'])

   avg_quantity_by_rating_quartile = df_cleaned.groupby('rating_quartile')['quantity_sold'].mean().reset_index()

   print("Prosječan broj prodanih jedinica po kvartilu broja ocjena:")
   for index, row in avg_quantity_by_rating_quartile.iterrows():
       print(f"- Kvartil broja ocjena: {row['rating_quartile']}, Prosječan broj prodanih jedinica: {row['quantity_sold']:.2f}")

   if len(avg_quantity_by_rating_quartile) > 1:
       first_quartile_avg = avg_quantity_by_rating_quartile.loc[avg_quantity_by_rating_quartile['rating_quartile'] == '1st quartile', 'quantity_sold'].iloc[0]
       fourth_quartile_avg = avg_quantity_by_rating_quartile.loc[avg_quantity_by_rating_quartile['rating_quartile'] == '4th quartile', 'quantity_sold'].iloc[0]

       if fourth_quartile_avg > first_quartile_avg:
           print("\nZaključak: Veći broj recenzija (num_ratings) u prosjeku korelira s većim brojem prodanih jedinica (quantity_sold).")
           print("To sugerira da više prodatih komada znači i veći broj recenzija, ili da proizvodi sa više recenzija bolje prodaju.")
       elif fourth_quartile_avg < first_quartile_avg:
           print("\nZaključak: Manji broj recenzija (num_ratings) u prosjeku korelira s većim brojem prodanih jedinica (quantity_sold).")
           print("Ovo je neočekivano, ili se trend ne poklapa direktno na svim kvartilima.")
       else:
           print("\nZaključak: Nema jasne korelacije između broja recenzija i broja prodanih jedinica na temelju prosjeka kvartila.")
   else:
       print("\nNema dovoljno kvartila za analizu trenda.")
else:
    print("Nema dovoljno podataka za analizu ovisnosti broja ocjena o broju prodanih jedinica nakon čišćenja.")