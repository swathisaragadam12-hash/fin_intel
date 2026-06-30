 Financial Intelligence AI Agent

A financial intelligence application that uses an agentic AI workflow to analyze publicly traded companies through natural language queries. The application retrieves real-time financial data, generates stock price visualizations, and creates downloadable PDF reports.

---

## Features

- Analyze companies using natural language queries
- AI-powered tool selection using Google Gemini
- Retrieve real-time stock market data
- Generate historical stock price charts
- Create downloadable PDF reports
- Interactive web interface built with Streamlit

---

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- LangGraph
- LangChain
- Yahoo Finance (yfinance)
- Pandas
- NumPy
- Matplotlib
- FPDF2

---

## Project Structure

```
fin_intel/
│── app.py
│── graph.py
│── tools.py
│── config.py
│── reports/
│── .gitignore
└── README.md
```

---

## How It Works

1. The user enters a financial query.
2. Gemini interprets the request and selects the required tools.
3. Financial data is retrieved from Yahoo Finance.
4. The application generates charts and financial insights.
5. A PDF report is created for download.

---

## Sample Queries

- Analyze Apple's financial performance.
- Show Microsoft's stock price trend.
- Generate a report for Tesla.
- Compare Apple and Google.

---
