from flask import Flask, render_template, request, url_for
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

# Cargar los datos
df = pd.read_csv("co2_emissions_kt_by_country.csv")

def top_countries_by_co2(df, n_years=5, top_n=10):
    recent_years = df['year'].unique()[-n_years:]
    recent_data = df[df['year'].isin(recent_years)]
    total_emissions = recent_data.groupby('country_name')['value'].sum().reset_index()
    top_countries = total_emissions.nlargest(top_n, 'value')
    return top_countries

def emissions_over_years(df, country):
    country_data = df[df['country_name'] == country]
    return country_data

@app.route('/', methods=['GET', 'POST'])
def index():
    top_countries = top_countries_by_co2(df, n_years=5, top_n=10)

    # Obtener la lista completa de países
    all_countries = df['country_name'].unique()

    # Graficar los top países
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_countries)))

    plt.figure(figsize=(12, 6))
    for i, row in enumerate(top_countries.itertuples(index=False)):
        plt.bar(row.country_name, row.value, color=colors[i], label=row.country_name)

    plt.title('Top 10 Países con Mayor Emisión de CO2 en los Últimos 5 Años')
    plt.xlabel('País')
    plt.ylabel('Emisiones de CO2 (kt)')
    plt.grid(axis='y')

    # Guardar la figura
    plt.savefig('static/top_graph.png')
    plt.close()  # Cerrar la figura para liberar memoria

    graph_url = url_for('static', filename='top_graph.png')

    # Manejar selección de país
    if request.method == 'POST':
        selected_country = request.form['country']
        country_data = emissions_over_years(df, selected_country)

        # Graficar las emisiones a lo largo de los años
        plt.figure(figsize=(12, 6))
        plt.plot(country_data['year'], country_data['value'], marker='o')
        plt.title(f'Emisiones de CO2 en {selected_country} a lo largo de los años')
        plt.xlabel('Año')
        plt.ylabel('Emisiones de CO2 (kt)')
        plt.grid()

        # Guardar la figura
        plt.savefig('static/country_graph.png')
        plt.close()  # Cerrar la figura para liberar memoria

        return render_template('index.html', 
                               top_countries=top_countries.to_dict(orient='records'), 
                               all_countries=all_countries, 
                               graph_url=url_for('static', filename='country_graph.png'), 
                               selected_country=selected_country, 
                               top_graph_url=graph_url)

    return render_template('index.html', 
                           top_countries=top_countries.to_dict(orient='records'), 
                           all_countries=all_countries, 
                           top_graph_url=graph_url)

if __name__ == '__main__':
    app.run(debug=True)
