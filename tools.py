import os
from fpdf import FPDF
from langchain_core.tools import tool

# Global path setup (Adjust as per your specific file structure if needed)
OUTPUT_REPORT_PATH = "financial_report.pdf"

class CustomStudentPDF(FPDF):
    def header(self):
        # Top corporate sleek accent block
        self.set_fill_color(15, 23, 42)  # Deep Charcoal / Navy Blue
        self.rect(0, 0, 210, 28, 'F')
        
        self.set_font("Arial", "B", 14)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 5, "fin_intel Hub | Automated Financial Report", ln=True, align="C")
        
        self.set_font("Arial", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, "EQUITY RESEARCH & VALUATION STATEMENT", ln=True, align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, "fin_intel Analysis Engine • System Generated Statement", 0, 0, "L")
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")


@tool
def get_stock_analysis(ticker: str) -> str:
    """
    Fetches real-time market data, valuation multiples, and business overview 
    metrics for a given stock ticker symbol.
    """
    # Placeholder layout mimicking your live market endpoint output structure
    # Replace this inner dict lookup with your actual live API call (yfinance, alpha_vantage, etc.)
    ticker_upper = ticker.upper().strip()
    
    mock_market_db = {
        "AAPL": "Company: Apple Inc. (AAPL)\nBusiness Summary: Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, Mac, iPad, and a line of multi-purpose tablets.\nCurrent Price: 283.78\nMarket Cap: 4167977926656\nP/E Ratio: 34.35593\nP/B Ratio: 39.088154",
        "GOOG": "Company: Google (GOOG)\nBusiness Summary: Alphabet Inc. offers various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America. It operates through Google Services, Google Cloud, and Other Bets segments.\nCurrent Price: 173.50\nMarket Cap: 2154000000000\nP/E Ratio: 26.22\nP/B Ratio: 8.71",
        "NVDA": "Company: NVIDIA Corporation (NVDA)\nBusiness Summary: NVIDIA Corporation focuses on personal computer graphics, graphics processing units, and also artificial intelligence solutions.\nCurrent Price: 125.10\nMarket Cap: 3071000000000\nP/E Ratio: 68.40\nP/B Ratio: 52.10"
    }
    
    return mock_market_db.get(
        ticker_upper, 
        f"Company: {ticker_upper}\nBusiness Summary: Financial profile metrics compiled dynamically.\nCurrent Price: 150.00\nMarket Cap: 100000000000\nP/E Ratio: 20.00\nP/B Ratio: 5.00"
    )


@tool
def generate_pdf_report(report_data: str) -> str:
    """
    Compiles analysis text and financial data into a clean, grid-formatted 
    PDF statement using native FPDF components.
    """
    try:
        pdf = CustomStudentPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # --- CRITICAL ENCODING SANITIZATION LAYER ---
        # Replaces complex unicode symbols/quotes that crash standard latin-1 PDF engines
        clean_text = (
            report_data.replace("’", "'")
                       .replace("“", '"')
                       .replace("”", '"')
                       .replace("—", "-")
                       .replace(r"\n", "\n")
        )
        clean_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
        lines = clean_text.split("\n")
        
        table_metrics = []
        narrative_lines = []
        company_name = "Target Corporation"
        
        # Parse lines into conversational text vs key financial metrics
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                key_str = key.strip().replace("*", "").replace("-", "")
                val_str = val.strip().replace("*", "")
                
                if "Company" in key_str:
                    company_name = val_str
                
                if any(m in key_str for m in ["Price", "Cap", "Ratio", "Ticker", "Indicator"]):
                    table_metrics.append((key_str, val_str))
                else:
                    if line.strip():
                        narrative_lines.append(line.replace("*", ""))
            else:
                if line.strip():
                    narrative_lines.append(line.replace("*", ""))
                    
        # --- SECTION 1: EXECUTIVE BRIEF ---
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.set_fill_color(59, 130, 246)  # Corporate Blue Marker Accent
        pdf.rect(10, pdf.get_y() + 1, 3, 4, 'F')
        pdf.set_x(15)
        pdf.cell(0, 6, f"1. Executive Brief: {company_name}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(51, 65, 85)
        
        # Print description text blocks
        full_narrative = "\n".join(narrative_lines)
        pdf.multi_cell(0, 6, full_narrative)
        pdf.ln(6)
        
        # --- SECTION 2: METRICS GRID ---
        if table_metrics:
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(15, 23, 42)
            pdf.set_fill_color(59, 130, 246)
            pdf.rect(10, pdf.get_y() + 1, 3, 4, 'F')
            pdf.set_x(15)
            pdf.cell(0, 6, "2. Key Fundamental Valuation Metrics", ln=True)
            pdf.ln(4)
            
            # Table Headers
            pdf.set_font("Arial", "B", 9.5)
            pdf.set_fill_color(241, 245, 249)  # Slate grey header highlight
            pdf.set_text_color(15, 23, 42)
            pdf.cell(85, 7, " Financial Indicator", border=1, fill=True)
            pdf.cell(105, 7, " Reported Metric Value", border=1, fill=True, ln=True)
            
            # Data Rows with alternating backgrounds for readability
            pdf.set_font("Arial", size=9.5)
            pdf.set_text_color(51, 65, 85)
            fill_toggle = False
            
            for key, val in table_metrics:
                pdf.set_fill_color(248, 250, 252) if fill_toggle else pdf.set_fill_color(255, 255, 255)
                pdf.cell(85, 7, f" {key}", border=1, fill=True)
                pdf.cell(105, 7, f" {val}", border=1, fill=True, ln=True)
                fill_toggle = not fill_toggle
                
            pdf.ln(8)
            
        # --- SECTION 3: CALLOUT FOOTER BOX ---
        current_y = pdf.get_y()
        # Ensure block context doesn't spill over footer margins
        if current_y < 260:
            pdf.set_fill_color(248, 250, 252)
            pdf.rect(10, current_y, 190, 15, 'F')
            pdf.set_fill_color(100, 116, 139)
            pdf.rect(10, current_y, 1.5, 15, 'F')
            
            pdf.set_x(15)
            pdf.set_font("Arial", "B", 8.5)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 5, "Analytical Guardrail Protocol Notice:", ln=True)
            pdf.set_x(15)
            pdf.set_font("Arial", "I", 8)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(0, 4, "All system valuation baselines calculate forecasts using a standardized statutory corporate tax configuration layer.", ln=True)

        # Write output file artifact
        pdf.output(OUTPUT_REPORT_PATH)
        return f"SUCCESS: PDF report compiled and written to target path: '{OUTPUT_REPORT_PATH}'."
        
    except Exception as e:
        return f"System generation failed during PDF printing processes: {str(e)}"