import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

# Nastavení Streamlitu
st.set_option('deprecation.showPyplotGlobalUse', False)

def fetch_financial_data(start_date, end_date):
    end_date_plus_one = end_date + timedelta(days=1)

    sp500_data = yf.download("^GSPC", start=start_date, end=end_date_plus_one)
    czk_usd_rate = yf.download("CZK=X", start=start_date, end=end_date_plus_one)
    return sp500_data, czk_usd_rate

def calculate_investment_months(start_date, end_date):
    total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

    # Přidáme jeden měsíc, protože počítáme úvodní i konečný měsíc jako plné
    total_months += 1

    return total_months


def calculate_sp500_returns(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date):
    investment_duration_months = calculate_investment_months(start_date, end_date)
    
    # Získání posledního dostupného směnného kurzu
    last_exchange_rate = czk_usd_rate['Close'].iloc[-1]
    
    # Výpočet měsíční investice v USD
    monthly_investment_usd = monthly_investment_czk / last_exchange_rate

    total_investment_usd = monthly_investment_usd * investment_duration_months
    total_investment_czk = monthly_investment_czk * investment_duration_months

    # Výpočet konečné hodnoty investice v USD
    monthly_returns = (sp500_data['Close'].pct_change() + 1).resample('M').prod()
    
    # Inicializace proměnné pro ukládání akumulované hodnoty
    accumulated_value_usd = 0

    # Seznam pro ukládání hodnot investice pro každý měsíc
    investment_values_czk = []

    # Akumulace hodnoty investice pro každý měsíc
    for monthly_return in monthly_returns:
        # Přidání měsíční investice do akumulované hodnoty
        accumulated_value_usd += monthly_investment_usd
        # Aplikování měsíčního výnosu na akumulovanou hodnotu
        accumulated_value_usd *= monthly_return
        # Převod akumulované hodnoty zpět do CZK a uložení do seznamu
        investment_values_czk.append(accumulated_value_usd * last_exchange_rate)

    # Výpočet konečné hodnoty investice v CZK
    final_value_czk = investment_values_czk[-1]
    profit_loss_czk = final_value_czk - total_investment_czk

    profit_loss_percentage = (profit_loss_czk / total_investment_czk) * 100

    return final_value_czk, profit_loss_czk, profit_loss_percentage, total_investment_czk, investment_duration_months


# def plot_sp500_data(sp500_data, start_date, end_date):
#    fig, ax = plt.subplots(figsize=(10, 6))
#    ax.plot(sp500_data.index, sp500_data['Close'], label='S&P 500', color='blue')

#    ax.set_xlabel('Datum', fontweight='bold')
#    ax.set_ylabel('Cena S&P 500 (USD)', fontweight='bold')
#    ax.set_title('Historie ceny S&P 500', fontweight='bold', pad=10)

#    ax.legend()
#    st.pyplot(fig)
import matplotlib.ticker as ticker
def thousands_separator(x, pos):
    """Pomocná funkce pro formátování s mezerou jako oddělovačem tisíců."""
    return f'{x:,.0f}'.replace(',', ' ')

def plot_investment_growth(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date):
    # Získání počtu měsíců investice
    investment_duration_months = calculate_investment_months(start_date, end_date)
    # Získání posledního směnného kurzu pro převod
    last_exchange_rate = czk_usd_rate['Close'].iloc[-1]
    
    # Výpočet měsíční investice v USD
    monthly_investment_usd = monthly_investment_czk / last_exchange_rate

    # Získání měsíčních výnosů S&P 500
    monthly_returns = (sp500_data['Close'].pct_change() + 1).resample('M').prod()

    # Inicializace proměnné pro ukládání akumulované hodnoty
    accumulated_value_usd = 0

    # Seznam pro ukládání hodnot investice pro každý měsíc
    investment_values_czk = []

    # Akumulace hodnoty investice pro každý měsíc
    for monthly_return in monthly_returns:
        # Přidání měsíční investice do akumulované hodnoty
        accumulated_value_usd += monthly_investment_usd
        # Aplikování měsíčního výnosu na akumulovanou hodnotu
        accumulated_value_usd *= monthly_return
        # Převod akumulované hodnoty zpět do CZK a uložení do seznamu
        investment_values_czk.append(accumulated_value_usd * last_exchange_rate)

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

     # Výpočet hodnoty penzijního spoření pro každý měsíc
    state_contribution = {
        300: 90,
        500: 130,
        1000: 230,
        1500: 230,
        1700: 230,
        2000: 230
    }
    monthly_state_contribution = state_contribution.get(monthly_investment_czk, 0)
    pension_values_czk = []
    accumulated_pension_value = 0
    for _ in range(investment_duration_months):
        accumulated_pension_value += monthly_investment_czk + monthly_state_contribution
        pension_values_czk.append(accumulated_pension_value)

    # Vytvoření grafu hodnoty investice
    fig, ax = plt.subplots(figsize=(10, 6))
    investment_dates = pd.date_range(start_date, periods=len(investment_values_czk), freq='M')

    # Vykreslení S&P 500 a penzijního spoření
    ax.plot(investment_dates, investment_values_czk, label='Hodnota investice S&P 500', color='green')
    ax.plot(investment_dates, pension_values_czk, label='Hodnota státního penzijního spoření', color='red')
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

def calculate_pension_savings(monthly_investment_czk, start_date, end_date):
    state_contribution = {
        300: 90,
        500: 130,
        1000: 230,
        1500: 230,
        1700: 230,
        2000: 230
    }

    # Získání státního příspěvku na základě měsíčního vkladu
    monthly_state_contribution = state_contribution.get(monthly_investment_czk, 0)
    
    investment_duration_months = calculate_investment_months(start_date, end_date)

    # Výpočet celkové hodnoty penzijního spoření
    total_investment_czk = monthly_investment_czk * investment_duration_months
    total_state_contribution = monthly_state_contribution * investment_duration_months
    accumulated_value = total_investment_czk + total_state_contribution

    return accumulated_value, total_investment_czk, total_state_contribution


from datetime import date

def main():
    st.title("Jak si našetřit více na důchod?")
    large_font = "<h2 style='font-size:18px; color: black;'>Index S&P 500 nebo státní penzijní spoření? Podívejte se, jaký přístup by vám v minulých letech vydělal více peněz? 🚀</h2>"
    st.markdown(large_font, unsafe_allow_html=True)
    max_start_date = date.today() - timedelta(days=365)
    start_date = st.date_input("Začátek investičního období", datetime(2010, 1, 1),max_value=max_start_date)
    end_date = st.date_input("Konec investičního období", datetime.now())

    if start_date >= end_date:
        st.error("Začátek investičního období musí být dříve než konec.")
    else:
        investment_options = [2000, 1700, 1500, 1000, 500, 300]
        monthly_investment_czk = st.selectbox("Měsíčně investovaná částka (Kč):", options=investment_options)

        if st.button("Spočítejte potenciální výnos"):
            sp500_data, czk_usd_rate = fetch_financial_data(start_date, end_date)
            final_value_czk, profit_loss_czk, profit_loss_percentage, total_investment_czk, investment_duration_months = calculate_sp500_returns(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date)

            final_value_czk_pension = calculate_pension_savings(monthly_investment_czk, start_date, end_date)

            final_value_czk_pension, total_invested_czk_pension, _ = calculate_pension_savings(monthly_investment_czk, start_date, end_date)
            profit_loss_czk_pension = final_value_czk_pension - total_invested_czk_pension
            profit_loss_percentage_pension = (profit_loss_czk_pension / total_invested_czk_pension) * 100

            # plot_sp500_data(sp500_data, start_date, end_date)
            formatted_profit_loss_percentage = f"{profit_loss_percentage:+.0f} %"  # Přidání znaménka
            plot_investment_growth(sp500_data, czk_usd_rate, monthly_investment_czk, start_date, end_date)  # Přidání chybějícího argumentu 'end_date'
            st.success(f"Zhodnocení investice do S&P 500: {final_value_czk:,.0f} Kč ({formatted_profit_loss_percentage})".replace(',', ' '))


            final_value_czk_pension, _, _ = calculate_pension_savings(monthly_investment_czk, start_date, end_date)
            formatted_profit_loss_percentage_pension = f"{profit_loss_percentage_pension:+.0f} %"
            st.error(f"Zhodnocení stáního penzijního spoření: {final_value_czk_pension:,.0f} Kč ({formatted_profit_loss_percentage_pension})".replace(',', ' '))

            st.info(f"Celkově investovaná částka: {total_investment_czk:,.0f} Kč".replace(',', ' '))
            st.info(f"Celkový počet investičních měsíců: {investment_duration_months} měsíců")
            st.balloons()

if __name__ == "__main__":
    main()

