from plotly.subplots import make_subplots
import os
import matplotlib.pyplot as plt
import pandas as pd
from src.utils import normalize_financial_data

def plot_financial_ratios(ratios_df, company_name):
    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)

    fig, axes = plt.subplots(3, 2, figsize=(16, 12))

    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROE"], marker="o", label="ROE")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROA"], marker="o", label="ROA")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROIC"], marker="o", label="ROIC")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROI"], marker="o", label="ROI")
    axes[0, 0].set_title(f"Return Ratios for {company_name}")
    axes[0, 0].set_xlabel("Year")
    axes[0, 0].set_ylabel("Percentage")
    axes[0, 0].legend()
    axes[0, 0].grid()

    axes[0, 1].plot(
        ratios_df["Year"], ratios_df["Quick Ratio"], marker="o", label="Quick Ratio"
    )
    axes[0, 1].plot(
        ratios_df["Year"], ratios_df["Current Ratio"], marker="o", label="Current Ratio"
    )
    axes[0, 1].set_title(f"Liquidity Ratios for {company_name}")
    axes[0, 1].set_xlabel("Year")
    axes[0, 1].set_ylabel("Ratio")
    axes[0, 1].legend()
    axes[0, 1].grid()

    axes[1, 0].plot(
        ratios_df["Year"], ratios_df["P/E Ratio"], marker="o", label="P/E Ratio"
    )
    axes[1, 0].plot(
        ratios_df["Year"], ratios_df["EBIT Margin"], marker="o", label="EBIT Margin"
    )
    axes[1, 0].set_title(f"Market and Profitability Metrics for {company_name}")
    axes[1, 0].set_xlabel("Year")
    axes[1, 0].set_ylabel("Ratio")
    axes[1, 0].legend()
    axes[1, 0].grid()

    axes[1, 1].plot(
        ratios_df["Year"],
        ratios_df["Debt to Equity"],
        marker="o",
        label="Debt to Equity",
    )
    axes[1, 1].set_title(f"Leverage Ratio for {company_name}")
    axes[1, 1].set_xlabel("Year")
    axes[1, 1].set_ylabel("Ratio")
    axes[1, 1].legend()
    axes[1, 1].grid()

    axes[2, 0].plot(
        ratios_df["Year"],
        ratios_df["Operating Margin"],
        marker="o",
        label="Operating Margin",
    )
    axes[2, 0].plot(
        ratios_df["Year"],
        ratios_df["Net Profit Margin"],
        marker="o",
        label="Net Profit Margin",
    )
    axes[2, 0].set_title(f"Margin Analysis for {company_name}")
    axes[2, 0].set_xlabel("Year")
    axes[2, 0].set_ylabel("Percentage")
    axes[2, 0].legend()
    axes[2, 0].grid()

    axes[2, 1].plot(
        ratios_df["Year"],
        ratios_df["Asset Turnover"],
        marker="o",
        label="Asset Turnover",
    )
    axes[2, 1].plot(
        ratios_df["Year"],
        ratios_df["Interest Coverage"],
        marker="o",
        label="Interest Coverage",
    )
    axes[2, 1].set_title(f"Efficiency Metrics for {company_name}")
    axes[2, 1].set_xlabel("Year")
    axes[2, 1].set_ylabel("Ratio")
    axes[2, 1].legend()
    axes[2, 1].grid()

    plt.tight_layout()
    plt.savefig(os.path.join(static_folder, f"{company_name}_all_ratios.png"))
    plt.close()

    normalized_df = normalize_financial_data(ratios_df)
    plt.figure(figsize=(14, 8))
    for column in normalized_df.columns[1:-1]:
        plt.plot(normalized_df["Year"], normalized_df[column], marker="o", label=column)
    plt.title(f"Normalized Financial Ratios for {company_name}")
    plt.xlabel("Year")
    plt.ylabel("Z-Score Normalized Value")
    plt.xticks(rotation=45)
    plt.ylim(-2, 2)
    plt.grid(which="both", linestyle="--", linewidth=0.5)
    plt.minorticks_on()
    plt.grid(which="minor", linestyle=":", linewidth="0.5", color="gray")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(static_folder, f"{company_name}_normalized_ratios.png"))
    plt.close()

    return [
        f"{company_name}_normalized_ratios.png",
        f"{company_name}_all_ratios.png",
    ]


import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_plotly_visualization(ratios_df, company_name):
    # Define a set of dark colors
    dark_colors = ["blue", "red", "green", "darkorange"]

    # Assign dark colors to each metric, repeating if necessary
    color_mapping = {
        "ROE": dark_colors[0],
        "ROA": dark_colors[1],
        "ROIC": dark_colors[2],
        "ROI": dark_colors[3],
        "Quick Ratio": dark_colors[1],
        "Current Ratio": dark_colors[0],
        "P/E Ratio": dark_colors[1],
        "P/B Ratio": dark_colors[2],
        "EBIT Margin": dark_colors[0],
        "Debt to Equity": dark_colors[0],
        "Operating Margin": dark_colors[0],
        "Net Profit Margin": dark_colors[1],
        "Asset Turnover": dark_colors[1],
        "Interest Coverage": dark_colors[0],  # Repeat colors if needed
    }

    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            f"Return Ratios {{<span style='color:{color_mapping['ROE']}'>ROE</span>, "
            f"<span style='color:{color_mapping['ROA']}'>ROA</span>, "
            f"<span style='color:{color_mapping['ROIC']}'>ROIC</span>, "
            f"<span style='color:{color_mapping['ROI']}'>ROI</span>}}",
            f"Liquidity Ratios {{<span style='color:{color_mapping['Current Ratio']}'>Current Ratio</span>, "
            f"<span style='color:{color_mapping['Quick Ratio']}'>Quick Ratio</span>}}",
            f"Market & Profitability {{<span style='color:{color_mapping['EBIT Margin']}'>EBIT Margin</span>, "
            f"<span style='color:{color_mapping['P/E Ratio']}'>P/E Ratio</span>, "
            f"<span style='color:{color_mapping['P/B Ratio']}'>P/B Ratio</span>}}",
            f"Leverage Ratio {{<span style='color:{color_mapping['Debt to Equity']}'>Debt to Equity</span>}}",
            f"Margin Analysis {{<span style='color:{color_mapping['Operating Margin']}'>Operating Margin</span>, "
            f"<span style='color:{color_mapping['Net Profit Margin']}'>Net Profit Margin</span>}}",
            f"Efficiency Metrics {{<span style='color:{color_mapping['Interest Coverage']}'>Interest Coverage</span>, "
            f"<span style='color:{color_mapping['Asset Turnover']}'>Asset Turnover</span>}}",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Return Ratios (1,1)
    for metric in ["ROE", "ROA", "ROIC", "ROI"]:
        if metric in ratios_df.columns:
            color = color_mapping.get(metric, "black")  # Default to black if not found
            fig.add_trace(
                go.Scatter(
                    x=ratios_df["Year"],
                    y=ratios_df[metric],
                    mode="lines+markers",
                    name=metric,
                    hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                    line=dict(color=color, width=2),
                ),
                row=1,
                col=1,
            )

    # Liquidity Ratios (1,2)
    for metric in ["Quick Ratio", "Current Ratio"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=1,
            col=2,
        )

    # Market & Profitability (2,1)
    for metric in ["P/E Ratio", "P/B Ratio", "EBIT Margin"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=2,
            col=1,
        )

    # Leverage Ratio (2,2)
    color = color_mapping.get("Debt to Equity", "black")
    fig.add_trace(
        go.Scatter(
            x=ratios_df["Year"],
            y=ratios_df["Debt to Equity"],
            name="Debt to Equity",
            hovertemplate="Debt to Equity: %{y}<extra></extra>",
            line=dict(color=color, width=2),
        ),
        row=2,
        col=2,
    )

    # Margin Analysis (3,1)
    for metric in ["Operating Margin", "Net Profit Margin"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=3,
            col=1,
        )

    # Efficiency Metrics (3,2)
    for metric in ["Asset Turnover", "Interest Coverage"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=3,
            col=2,
        )

    fig.update_layout(
        height=1200,
        width=1600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        legend=dict(
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=1.15,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
        margin=dict(l=50, r=150, t=80, b=50),
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgrey",
        automargin=True,
        tickformat="d",
        dtick=1,
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgrey", automargin=True)

    return fig.to_html(full_html=False, include_plotlyjs=True)
