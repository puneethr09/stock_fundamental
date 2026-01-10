
import pandas as pd
import numpy as np

def calculate_piotroski_series(years, income_stmt, balance_sheet, cash_flow):
    """
    Calculates Piotroski F-Score for each year available.
    Returns a list of scores corresponding to 'years'.
    """
    scores = []
    
    # Ensure dataframes are numeric
    income_stmt = income_stmt.apply(pd.to_numeric, errors='coerce').fillna(0)
    balance_sheet = balance_sheet.apply(pd.to_numeric, errors='coerce').fillna(0)
    cash_flow = cash_flow.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Helper to get value for a specific year
    # The financial statements key is the date. We need to match 'years' (integers) to the columns (Dates).
    # We'll map Year -> Date Column
    year_map = {}
    for col in income_stmt.columns:
        try:
            year_map[col.year] = col
        except:
            pass
            
    sorted_years = sorted([y for y in years if y in year_map])
    
    # Calculations
    for i, year in enumerate(years):
        if year not in year_map:
            scores.append(0)
            continue
            
        date_col = year_map[year]
        
        # Check if we have previous year data
        prev_year = year - 1
        has_prev = prev_year in year_map
        prev_date_col = year_map[prev_year] if has_prev else None
        
        score = 0
        try:
            # Data Extraction
            ni = income_stmt.loc['Net Income', date_col] if 'Net Income' in income_stmt.index else 0
            assets = balance_sheet.loc['Total Assets', date_col] if 'Total Assets' in balance_sheet.index else 1
            avg_assets = assets # Simplified if prev missing
            if has_prev:
                assets_prev = balance_sheet.loc['Total Assets', prev_date_col] if 'Total Assets' in balance_sheet.index else 1
                avg_assets = (assets + assets_prev) / 2
                
            ocf = cash_flow.loc['Operating Cash Flow', date_col] if 'Operating Cash Flow' in cash_flow.index else 0
            
            lt_debt = balance_sheet.loc['Total Debt', date_col] if 'Total Debt' in balance_sheet.index else 0 # Use Total Debt proxy
            # Or strict Long Term Debt
            
            curr_assets = balance_sheet.loc['Current Assets', date_col] if 'Current Assets' in balance_sheet.index else 0
            curr_liab = balance_sheet.loc['Current Liabilities', date_col] if 'Current Liabilities' in balance_sheet.index else 1
            
            shares = income_stmt.loc['Basic Average Shares', date_col] if 'Basic Average Shares' in income_stmt.index else 0
            
            gross_profit = income_stmt.loc['Gross Profit', date_col] if 'Gross Profit' in income_stmt.index else 0
            revenue = income_stmt.loc['Total Revenue', date_col] if 'Total Revenue' in income_stmt.index else 1
            
            # 1. ROA > 0
            roa = ni / avg_assets if avg_assets else 0
            if roa > 0: score += 1
            
            # 2. CFO > 0
            if ocf > 0: score += 1
            
            # 3. dROA > 0
            if has_prev:
                # Recalculate prev ROA
                ni_prev = income_stmt.loc['Net Income', prev_date_col]
                assets_prev_start = balance_sheet.loc['Total Assets', year_map.get(year-2)] if (year-2) in year_map else assets_prev
                avg_assets_prev = (assets_prev + assets_prev_start)/2
                roa_prev = ni_prev / avg_assets_prev if avg_assets_prev else 0
                if roa > roa_prev: score += 1
                
            # 4. Accrual (CFO > NI)
            if ocf > ni: score += 1
            
            # 5. dLeverage < 0 (Long term debt ratio)
            if has_prev:
                lt_debt_prev = balance_sheet.loc['Total Debt', prev_date_col] if 'Total Debt' in balance_sheet.index else 0
                lev = lt_debt / avg_assets
                lev_prev = lt_debt_prev / avg_assets_prev
                if lev < lev_prev: score += 1
                
            # 6. dCurrentRatio > 0
            curr_ratio = curr_assets / curr_liab if curr_liab else 0
            if has_prev:
                curr_assets_prev = balance_sheet.loc['Current Assets', prev_date_col]
                curr_liab_prev = balance_sheet.loc['Current Liabilities', prev_date_col]
                curr_ratio_prev = curr_assets_prev / curr_liab_prev if curr_liab_prev else 0
                if curr_ratio > curr_ratio_prev: score += 1
                
            # 7. No Dilution
            if has_prev:
                shares_prev = income_stmt.loc['Basic Average Shares', prev_date_col] if 'Basic Average Shares' in income_stmt.index else 0
                if shares <= shares_prev: score += 1
                
            # 8. dGrossMargin > 0
            gm = gross_profit / revenue if revenue else 0
            if has_prev:
                gp_prev = income_stmt.loc['Gross Profit', prev_date_col]
                rev_prev = income_stmt.loc['Total Revenue', prev_date_col]
                gm_prev = gp_prev / rev_prev if rev_prev else 0
                if gm > gm_prev: score += 1
                
            # 9. dAssetTurnover > 0
            turnover = revenue / avg_assets if avg_assets else 0
            if has_prev:
                rev_prev = income_stmt.loc['Total Revenue', prev_date_col]
                turnover_prev = rev_prev / avg_assets_prev if avg_assets_prev else 0
                if turnover > turnover_prev: score += 1
                
        except Exception as e:
            # print(f"F-Score Calc Error inputs: {year} {e}")
            pass
            
        scores.append(score)
        
    return scores

def calculate_graham_number_series(eps_series, bvps_series):
    """
    Vectorized Graham Number calculation.
    """
    # Graham Number = Sqrt(22.5 * EPS * BVPS)
    # Filter negatives
    gn = np.sqrt(22.5 * eps_series * bvps_series)
    return gn.fillna(0)

def get_valuation_status(current_price, graham_number):
    if not graham_number or graham_number <= 0:
        return "N/A"
    if current_price < graham_number:
        discount = ((graham_number - current_price) / graham_number) * 100
        return f"Undervalued ({discount:.0f}%)"
    else:
        premium = ((current_price - graham_number) / graham_number) * 100
        return f"Overvalued ({premium:.0f}%)"
