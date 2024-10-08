import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

# Nastavení Streamlitu
# st.set_option('deprecation.showPyplotGlobalUse', False)

@st.cache
def fetch_financial_data(start_date, end_date):
    try:
        end_date_plus_one = end_date + timedelta(days=1)

        sp500_data = yf.download("^GSPC", start=start_date, end=end_date_plus_one)
        czk_usd_rate = yf.download("CZK=X", start=start_date, end=end_date_plus_one)
        
        # Kontrola, zda byla data úspěšně načtena
        if sp500_data.empty or czk_usd_rate.empty:
            st.error("Nepodařilo se načíst finanční data. Zkuste prosím jiné datum nebo zkuste později.")
            return None, None

        return sp500_data, czk_usd_rate
    except Exception as e:
        st.error(f"Nastala chyba při načítání dat: {e}")
        return None, None


# Funkce pro kontrolu, zda je datum víkendem
def is_weekend(input_date):
    return input_date.weekday() >= 5

# start_date = datetime(2010, 1, 29)
# end_date = datetime(2024, 2, 29)

# data = fetch_financial_data(start_date, end_date)


def calculate_investment_months(start_date, end_date):
    total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

    # Přidáme jeden měsíc, protože počítáme úvodní i konečný měsíc jako plné
    total_months += 1

    return total_months

def plot_sp500_data(sp500_plot, start_date, end_date):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sp500_plot.index, sp500_plot['Close'], label='S&P 500', color='purple')

    ax.set_xlabel('Rok', fontweight='bold')
    ax.set_ylabel('Cena S&P 500 (USD)', fontweight='bold')
    ax.set_title('Historie ceny S&P 500', fontweight='bold', pad=10)

    ax.legend()
    st.pyplot(fig)


def calculate_sp500_returns(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date):
    investment_duration_months = calculate_investment_months(start_date, end_date)

    # Získání směnného kurzu pro začátek investice
    start_exchange_rate = czk_usd_rate['Close'].get(start_date, czk_usd_rate['Close'].iloc[0])

    # Výpočet měsíční investice v USD na začátku investice
    monthly_investment_usd = monthly_investment_czk / start_exchange_rate

    total_investment_czk = monthly_investment_czk * investment_duration_months

    monthly_returns = (sp500_data['Close'].pct_change() + 1).resample('M').prod()
    accumulated_value_usd = 0
    investment_values_czk = []

    # Pro každý měsíc v investičním období
    for month in range(investment_duration_months):
        # Přičtení měsíční investice
        accumulated_value_usd += monthly_investment_usd
        # Aplikace měsíčního výnosu
        accumulated_value_usd *= monthly_returns.iloc[month]

        # Získání kurzu pro daný měsíc
        month_date = start_date + pd.DateOffset(months=month)
        monthly_exchange_rate = czk_usd_rate['Close'].get(month_date, czk_usd_rate['Close'].iloc[month])

        # Převod hodnoty investice na CZK podle měsíčního kurzu
        investment_values_czk.append(accumulated_value_usd * monthly_exchange_rate)

    final_value_czk = investment_values_czk[-1]
    profit_loss_czk = final_value_czk - total_investment_czk
    profit_loss_percentage = (profit_loss_czk / total_investment_czk) * 100

    return final_value_czk, profit_loss_czk, profit_loss_percentage, total_investment_czk, investment_duration_months


def calculate_average_annual_return(final_value_czk, total_investment_czk, start_date, end_date):
    # Celkový počet let investice
    years = (end_date - start_date).days / 365.25

    # Výpočet CAGR
    cagr = (final_value_czk / total_investment_czk) ** (1 / years) - 1

    # Převod CAGR na procenta
    cagr_percentage = cagr * 100

    return cagr_percentage



import matplotlib.ticker as ticker
def thousands_separator(x, pos):
    """Pomocná funkce pro formátování s mezerou jako oddělovačem tisíců."""
    return f'{x:,.0f}'.replace(',', ' ')

def plot_investment_growth(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date):
    investment_duration_months = calculate_investment_months(start_date, end_date)

    # Získání směnného kurzu pro začátek a konec investice
    start_exchange_rate = czk_usd_rate['Close'].get(start_date, czk_usd_rate['Close'].iloc[0])
    end_exchange_rate = czk_usd_rate['Close'].get(end_date, czk_usd_rate['Close'].iloc[-1])

    # Výpočet měsíční investice v USD na začátku investice
    monthly_investment_usd = monthly_investment_czk / start_exchange_rate

    monthly_returns = (sp500_data['Close'].pct_change() + 1).resample('M').prod()
    accumulated_value_usd = 0
    investment_values_czk = []

    for monthly_return in monthly_returns:
        accumulated_value_usd += monthly_investment_usd
        accumulated_value_usd *= monthly_return

        # Převod akumulované hodnoty zpět do CZK a uložení do seznamu
        investment_values_czk.append(accumulated_value_usd * end_exchange_rate)

    # Inicializace proměnné pro ukládání celkové vkládané částky
    total_invested_czk = 0

    # Seznam pro ukládání celkové vkládané částky pro každý měsíc
    invested_values_czk = []

    # Akumulace celkové vkládané částky pro každý měsíc
    for monthly_return in monthly_returns:
        # Přidání měsíční investice do celkové vkládané částky
        total_invested_czk += monthly_investment_czk
        # Převod celkové vkládané částky na seznam pro každý měsíc
        invested_values_czk.append(total_invested_czk)


    # Vytvoření grafu hodnoty investice
    fig, ax = plt.subplots(figsize=(10, 6))
    investment_dates = pd.date_range(start_date, periods=len(investment_values_czk), freq='M')

    # Vykreslení S&P 500 a penzijního spoření
    ax.plot(investment_dates, investment_values_czk, label='Hodnota investice S&P 500', color='purple')
    ax.plot(investment_dates, invested_values_czk, linestyle='dashed', color='blue', label='Vložená částka celkem')

    # Nastavení formátu popisků na ose Y
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(thousands_separator))

    ax.set_xlabel('Datum', fontweight='bold')
    ax.set_ylabel('Hodnota investice (Kč)', fontweight='bold')
    ax.set_title('Růst hodnoty investice v čase', fontweight='bold', pad=10)
    # Přidání horizontální mřížky
    ax.yaxis.grid(True, linestyle='--', linewidth=0.5)

    ax.legend()
    st.pyplot(fig)
    
from datetime import date, timedelta

def main():
    st.title("Jak si našetřit více na důchod?")
    large_font = """
    <h2 style='font-size:18px; color: black; line-height: 1.5;'>
    Jak by se vám peníze šetřené na důchod zhodnotily v burzovním indexu S&P 500? 
    Podívejte se, kolik byste vydělali, kdybyste začali pravidelně investovat před 10 nebo třeba 15 lety. 🚀
    </h2>
    """    
    st.markdown(large_font, unsafe_allow_html=True)
    max_start_date = date.today() - timedelta(days=365)
    start_date = st.date_input("Začátek investičního období", datetime(2010, 1, 4),max_value=max_start_date,min_value=datetime(2005, 1, 1))
    end_date = st.date_input("Konec investičního období", datetime.now(),max_value=datetime.now())

    # Minimální délka investičního období v letech
    minimalni_delka_v_rokoch = 1

    # Výpočet minimálního začátku investičního období
    min_zacatek_investice = end_date - timedelta(days=365 * minimalni_delka_v_rokoch)
    import pandas_market_calendars as mcal

    nyse = mcal.get_calendar('NYSE')
    prazdniny = nyse.holidays().holidays

    # Převod seznamu prázdnin na seznam dat
    seznam_prazdnin = [pd.to_datetime(d).date() for d in prazdniny]

    # Kontrola, zda je zvolený začátek investičního období dostatečně vzdálený od konce
    if start_date >= min_zacatek_investice:
        st.error(f"Konec investičního období musí být od jeho začátku vzdálený minimálně {minimalni_delka_v_rokoch} rok.")
    elif start_date >= end_date:
        st.error("Začátek investičního období musí být dříve než konec.")
    elif start_date.weekday() >= 5 or start_date in seznam_prazdnin:
        st.error("Zvolený začátek investice připadá na víkend nebo burzovní prázdniny. Prosím, vyberte pracovní den.")
    elif end_date.weekday() >= 5 or end_date in seznam_prazdnin:
        st.error("Zvolený konec investice připadá na víkend nebo burzovní prázdniny. Prosím, vyberte pracovní den.")
    else:
        monthly_investment_czk = st.slider("Měsíčně investovaná částka (Kč):", min_value=2000, max_value=20000, step=1000, value=10000,format="%.0f Kč")

        if st.button("Spočítejte potenciální výnos"):
            sp500_data, czk_usd_rate = fetch_financial_data(start_date, end_date)
            final_value_czk, profit_loss_czk, profit_loss_percentage, total_investment_czk, investment_duration_months = calculate_sp500_returns(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date)

            # plot_sp500_data(sp500_data, start_date, end_date)
            formatted_profit_loss_percentage = f"{profit_loss_percentage:+.0f} %"  # Přidání znaménka
            plot_investment_growth(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date)  # Přidání chybějícího argumentu 'end_date'
            st.success(f"Zhodnocení investice do S&P 500: {final_value_czk:,.0f} Kč ({formatted_profit_loss_percentage})".replace(',', ' '))
            # Volání funkce po výpočtu zisku/ztráty
            cagr_percentage = calculate_average_annual_return(final_value_czk, total_investment_czk, start_date, end_date)
            # Zobrazení průměrného ročního výnosu uživateli
            st.success(f"Průměrný roční výnos: {cagr_percentage:.2f} %")

            st.info(f"Celkově investovaná částka: {total_investment_czk:,.0f} Kč".replace(',', ' '))
            st.info(f"Celkový počet investičních měsíců: {investment_duration_months} měsíců")
            st.balloons()
        else:
            st.write("")
            sp500_plot = yf.download("^GSPC", start=start_date, end=end_date)
            plot_sp500_data(sp500_plot, start_date, end_date)

if __name__ == "__main__":
    main()

