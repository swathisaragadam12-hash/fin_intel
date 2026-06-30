import os
from datetime import datetime

import yfinance as yf
from fpdf import FPDF

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
    Fetch financial information for a stock ticker.

    Use this tool whenever the user asks about:
    - stock price
    - company valuation
    - market cap
    - PE ratio
    - PB ratio
    - company overview
    """

    ticker = ticker.strip().upper()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return {
                "error": f"Unable to fetch data for '{ticker}'."
            }

        summary = info.get("longBusinessSummary") or ""
        summary = summary[:500]

        result = {
            "Ticker": ticker,
            "Company": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Current Price": info.get("currentPrice", "N/A"),
            "Market Cap": format_market_cap(info.get("marketCap")),
            "P/E Ratio": info.get("trailingPE", "N/A"),
            "P/B Ratio": info.get("priceToBook", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Business Summary": summary
        }

        return result

    except Exception as e:
        return {
            "error": f"Failed to retrieve data for {ticker}: {str(e)}"
        }


def generate_pdf_report(report_text: str) -> str:
    """
    Save the provided financial report as a PDF.

    Input:
        report_text -> Complete report in plain text.

    Output:
        Returns the file path after saving the report.
    """

    try:

        pdf = FPDF()
        pdf.add_page()

        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Arial", "B", 16)
        pdf.cell(
            0,
            10,
            "fin_intel Financial Analysis Report",
            ln=True,
            align="C"
        )

        pdf.ln(8)

        pdf.set_font("Arial", size=11)

        clean_text = report_text.encode(
            "latin-1",
            "replace"
        ).decode("latin-1")

        pdf.multi_cell(
            0,
            8,
            clean_text
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"financial_report_{timestamp}.pdf"

        filepath = os.path.join(
            REPORTS_DIR,
            filename
        )

        pdf.output(filepath)

        return f"SUCCESS: PDF report generated successfully.\nSaved at: {filepath}"

    except Exception as e:
        return f"Error while generating PDF: {str(e)}"


all_tools = [
    get_stock_analysis,
    generate_pdf_report
]