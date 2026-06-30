import os
from datetime import datetime
import yfinance as yf
from fpdf import FPDF
import matplotlib.pyplot as plt

from config import REPORTS_DIR

def format_market_cap(value):
    """Convert market cap into a readable format."""
    if value is None:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f} T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f} B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f} M"
    return f"${value:,}"


def get_stock_analysis(ticker: str) -> dict:
    """
    Fetch financial information and generate a 6-month historical price chart image.
    
    Use this tool whenever the user asks about:
    - stock price / history / performance
    - charts / graphs / visual trends
    - company valuation, market cap, PE ratio, PB ratio
    """
    ticker = ticker.strip().upper()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return {"error": f"Unable to fetch data for '{ticker}'."}

        # --- CHART GENERATION ---
        hist = stock.history(period="6m")
        chart_path = ""
        if not hist.empty:
            plt.figure(figsize=(6, 3))
            plt.plot(hist.index, hist['Close'], color='#1f77b4', linewidth=2)
            plt.title(f"{ticker} - 6 Month Closing Price", fontsize=10, fontweight='bold')
            plt.xlabel("Date", fontsize=8)
            plt.ylabel("Price ($)", fontsize=8)
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.xticks(rotation=45, fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            
            # Save chart to unique path
            chart_filename = f"{ticker}_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            chart_path = os.path.join(REPORTS_DIR, chart_filename)
            plt.savefig(chart_path, dpi=150)
            plt.close()

        summary = info.get("longBusinessSummary") or ""
        summary = summary[:500]

        return {
            "Ticker": ticker,
            "Company": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Current Price": info.get("currentPrice", "N/A"),
            "Market Cap": format_market_cap(info.get("marketCap")),
            "P/E Ratio": info.get("trailingPE", "N/A"),
            "P/B Ratio": info.get("priceToBook", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Business Summary": summary,
            "Chart Path": chart_path
        }

    except Exception as e:
        return {"error": f"Failed to retrieve data for {ticker}: {str(e)}"}


def generate_pdf_report(report_text: str) -> str:
    """
    Save the provided financial report text as a PDF document.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "fin_intel Financial Analysis Report", ln=True, align="C")
        pdf.ln(8)

        # Body Text
        pdf.set_font("Arial", size=11)
        clean_text = report_text.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 8, clean_text)
        pdf.ln(10)

        # --- EMBED EXISTING CHARTS ---
        charts = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(".png")], reverse=True)
        if charts:
            latest_chart_path = os.path.join(REPORTS_DIR, charts[0])
            pdf.image(latest_chart_path, x=15, w=180)
            pdf.ln(5)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_report_{timestamp}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        pdf.output(filepath)

        # Clean up chart file after building PDF so it doesn't clutter
        if charts:
            try:
                os.remove(latest_chart_path)
            except:
                pass

        return f"SUCCESS: PDF report generated successfully.\nSaved at: {filepath}"

    except Exception as e:
        return f"Error while generating PDF: {str(e)}"

all_tools = [get_stock_analysis, generate_pdf_report]