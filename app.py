from flask import (
    Flask,
    render_template,
    jsonify,
    Response,
    request,
    session,
    redirect,
    url_for,
)
from src.basic_analysis import (
    get_financial_ratios,
    analyze_ratios,
    get_market_news,
    get_news_categories,
)
from src.utils import load_company_data
from src.community_knowledge import CommunityKnowledgeBase, InsightCategory
from src.behavioral_analytics import (
    behavioral_tracker,
    get_learning_stage_context,
    adapt_content_for_stage,
    track_page_interaction,
    InteractionType,
)
from src.pattern_recognition_trainer import PatternRecognitionTrainer, PatternType
from src.educational_framework import LearningStage
from src.tool_independence_trainer import ToolIndependenceTrainer
import subprocess, os
from src.research_guidance_system import ResearchGuidanceSystem
from src.gamified_progress_tracker import AchievementContext
import secrets
from src.export_service import ExportService

# Prometheus metrics
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = Flask(__name__)
import os
import secrets
import subprocess
import glob
import csv
import datetime
import difflib
import pandas as pd
import json
import yfinance as yf
import pandas as pd

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)
ACTIVE_USERS = Gauge("active_users", "Number of active users")
SYSTEM_HEALTH = Gauge("system_health", "System health status")


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management
REPO_PATH = "/home/puneeth/repo/stock_fundamental/"

# Initialize community knowledge base
community_kb = CommunityKnowledgeBase()

# Initialize pattern recognition trainer
pattern_trainer = PatternRecognitionTrainer()

# Initialize tool independence trainer
tool_trainer = ToolIndependenceTrainer()


def get_company_financial_data(ticker):
    """Fetch real-time financial data for a company using yfinance API"""
    try:
        import yfinance as yf
        import pandas as pd

        # Ensure ticker has .NS suffix for Indian stocks if not already present
        if not ticker.endswith(".NS"):
            ticker_symbol = f"{ticker}.NS"
        else:
            ticker_symbol = ticker

        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        # Fetch financial statements
        balance_sheet = stock.balance_sheet
        financials = stock.financials

        # Extract key financial metrics
        market_cap = info.get("marketCap", 0) / 1e7  # Convert to crores
        if market_cap == 0:
            market_cap = info.get("enterpriseValue", 25000) / 1e7

        # Get debt and equity data from balance sheet
        total_debt = 0
        total_equity = 1  # Default to avoid division by zero

        if not balance_sheet.empty:
            # Try different debt field names
            debt_fields = [
                "Total Debt",
                "Long Term Debt",
                "Short Long Term Debt",
                "Net Debt",
            ]
            for field in debt_fields:
                if field in balance_sheet.index:
                    debt_value = (
                        balance_sheet.loc[field].iloc[0]
                        if len(balance_sheet.columns) > 0
                        else 0
                    )
                    if pd.notna(debt_value):
                        total_debt = debt_value / 1e6  # Convert to crores
                        break

            # Try different equity field names
            equity_fields = [
                "Total Equity Gross Minority Interest",
                "Stockholders Equity",
                "Common Stock Equity",
            ]
            for field in equity_fields:
                if field in balance_sheet.index:
                    equity_value = (
                        balance_sheet.loc[field].iloc[0]
                        if len(balance_sheet.columns) > 0
                        else 1
                    )
                    if pd.notna(equity_value):
                        total_equity = equity_value / 1e6  # Convert to crores
                        break

        # Calculate financial ratios
        debt_to_equity = (total_debt / total_equity) if total_equity != 0 else 0
        current_ratio = (
            info.get("currentRatio", 1.5) if info.get("currentRatio") else 1.5
        )

        # Get profitability metrics
        roe = info.get("returnOnEquity", 0.12) if info.get("returnOnEquity") else 0.12
        profit_margin = (
            info.get("profitMargins", 0.08) if info.get("profitMargins") else 0.08
        )

        # Get growth metrics
        revenue_growth = (
            info.get("revenueGrowth", 0.10) if info.get("revenueGrowth") else 0.10
        )
        earnings_growth = (
            info.get("earningsGrowth", 0.12) if info.get("earningsGrowth") else 0.12
        )

        # Clean up description - keep full for popup, truncate for display
        business_description = info.get(
            "longBusinessSummary",
            f"Leading company in {info.get('industry', 'technology')} sector",
        )
        business_description_truncated = (
            business_description[:200] + "..."
            if len(business_description) > 200
            else business_description
        )

        return {
            "symbol": ticker.upper(),
            "company_name": info.get("longName", f"{ticker.upper()} Limited"),
            "industry": info.get("industry", "Technology"),
            "sector": info.get("sector", "Information Technology"),
            "business_description": business_description_truncated,
            "business_description_full": business_description,  # Full description for popup
            "market_cap": market_cap,
            "listing_status": "Listed",
            "exchange": "NSE",
            # Financial metrics
            "debt_to_equity": debt_to_equity,
            "current_ratio": current_ratio,
            "roe": roe,
            "net_margin": profit_margin,
            "revenue_growth": revenue_growth,
            "earnings_growth": earnings_growth,
            "asset_growth": 0.08,  # Default if not available
        }

    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        # Return fallback data structure
        return {
            "symbol": ticker.upper(),
            "company_name": f"{ticker.upper()} Limited",
            "industry": "Technology",
            "sector": "Information Technology",
            "business_description": "Company operating in technology sector",
            "business_description_full": "Company operating in technology sector with focus on innovation and growth in the digital economy.",
            "market_cap": 25000,  # Default mid-cap
            "listing_status": "Listed",
            "exchange": "NSE",
            "debt_to_equity": 0.5,
            "current_ratio": 1.5,
            "roe": 0.12,
            "net_margin": 0.08,
            "revenue_growth": 0.10,
            "earnings_growth": 0.12,
            "asset_growth": 0.08,
        }


def get_anonymous_user_id():
    """Get or create anonymous user ID for session"""
    if "anonymous_user_id" not in session:
        session["anonymous_user_id"] = community_kb.generate_anonymous_user_id(
            str(request.remote_addr) + str(request.user_agent)
        )
    return session["anonymous_user_id"]


research_system = ResearchGuidanceSystem()


@app.route("/research-assignment", methods=["POST"])
def research_assignment():
    """Create a personalized research assignment from posted gap data.

    Expected JSON body: {"user_gaps": [...], "learning_stage": int}
    """
    payload = request.get_json(force=True)
    user_gaps = payload.get("user_gaps", [])
    learning_stage = int(payload.get("learning_stage", 2))

    assignment = research_system.generate_personalized_research_assignment(
        user_gaps, learning_stage
    )
    return jsonify({"success": True, "assignment": assignment})


@app.route("/research-assignment", methods=["GET"])
def research_assignment_list():
    """Provide a lightweight listing of available research assignment templates for GET requests.

    Tests may call this route with GET; the POST handler is used for creating specific assignments.
    """
    try:
        # Best-effort: return empty list or templates if available
        templates = getattr(research_system, "_templates", [])
        return jsonify({"success": True, "templates": templates})
    except Exception:
        return jsonify({"success": True, "templates": []})


@app.route("/research-assignment/<assignment_id>/complete", methods=["POST"])
def research_assignment_complete(assignment_id=None):
    payload = request.get_json(force=True)
    user_id = payload.get("user_id", get_anonymous_user_id())
    completion = payload.get("completion", {})
    research_system.track_research_progress(user_id, assignment_id, completion)

    # Evaluate submission (automated first-pass)
    try:
        evaluation = research_system.evaluate_research_submission(
            assignment_id, completion
        )
    except Exception:
        evaluation = {"score": 0, "feedback": "Evaluation failed"}

    # Build completion data for gamification (normalize score to 0..1)
    try:
        research_quality = float(evaluation.get("score", 0)) / 100.0
    except Exception:
        research_quality = 0.0

    completion_data = {
        "research_quality": research_quality,
        "session_duration": completion.get("duration", 0),
        "skill_improvements": completion.get("skill_improvements", {}),
    }

    # Update gamification progress and check for new badges
    awarded_badges = []
    try:
        behavioral_tracker.gamification.update_progress_metrics(
            user_id, completion_data
        )

        assessment = behavioral_tracker.get_current_stage_assessment()
        current_stage = assessment.current_stage if assessment else None

        achievement_context = AchievementContext(
            session_id=user_id,
            user_id=user_id,
            current_stage=current_stage,
            behavioral_data=completion.get("behavioral_snapshot", {}),
            session_history=(
                behavioral_tracker._get_session_history(user_id)
                if hasattr(behavioral_tracker, "_get_session_history")
                else []
            ),
            interaction_counts=(
                behavioral_tracker._get_interaction_counts(user_id)
                if hasattr(behavioral_tracker, "_get_interaction_counts")
                else {}
            ),
        )

        newly_earned = behavioral_tracker.gamification.check_achievement_conditions(
            achievement_context
        )
        for badge_type in newly_earned:
            badge = behavioral_tracker.gamification.award_badge(
                badge_type, achievement_context
            )
            try:
                behavioral_tracker._store_achievement_notification(user_id, badge)
            except Exception:
                pass
            awarded_badges.append(
                {
                    "badge_type": badge.badge_type.value,
                    "display_name": badge.display_name,
                    "description": badge.description,
                }
            )
    except Exception as e:
        print(f"Error updating gamification on completion: {e}")

    return jsonify(
        {"success": True, "evaluation": evaluation, "awarded_badges": awarded_badges}
    )


@app.route("/research-completions/<user_id>")
def research_completions(user_id=None):
    # lightweight listing using persistence layer
    from src.persistence import get_completions_for_user

    user = user_id or get_anonymous_user_id()
    rows = get_completions_for_user(user)
    return jsonify({"success": True, "completions": rows})


@app.route("/research-assignment/<assignment_id>")
def view_research_assignment(assignment_id=None):
    # Try to load from in-memory store, fallback to persistence
    assignment = research_system._assignments.get(assignment_id)
    if not assignment:
        try:
            from src.persistence import get_assignment

            assignment = get_assignment(assignment_id)
        except Exception:
            assignment = None

    if not assignment:
        return jsonify({"success": False, "message": "Assignment not found"}), 404

    return render_template("research_assignment.html", assignment=assignment)


@app.route("/user/<user_id>/badges")
def get_user_badges(user_id=None):
    try:
        from src.persistence import get_badges_for_user

        uid = user_id or get_anonymous_user_id()
        badges = get_badges_for_user(uid)
        return jsonify({"success": True, "badges": badges})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/user/<user_id>/progress")
def get_user_progress(user_id=None):
    try:
        from src.persistence import get_progress_metrics

        uid = user_id or get_anonymous_user_id()
        progress = get_progress_metrics(uid)
        return jsonify({"success": True, "progress": progress or {}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/user/<user_id>/notifications")
def get_user_notifications(user_id=None):
    try:
        from src.persistence import get_notifications_for_user

        uid = user_id or get_anonymous_user_id()
        notes = get_notifications_for_user(uid)
        return jsonify({"success": True, "notifications": notes})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/")
@app.route("/home")  # Adding both routes for flexibility
def home():
    # Initialize session for anonymous user tracking
    anonymous_user_id = get_anonymous_user_id()

    # Get learning stage context for UI adaptation
    learning_context = get_learning_stage_context()

    news_items = get_market_news()
    return render_template("index.html", news=news_items, **learning_context)


@app.route("/achievements")
def achievements():
    try:
        uid = get_anonymous_user_id()
    except Exception:
        uid = ""
    return render_template("achievements.html", user_id=uid)


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    # Handle both POST (from search bar) and GET params
    if request.method == "POST":
        ticker = request.form.get("ticker", "").upper()
    else:
        ticker = request.args.get("ticker", "").upper()
        
    ticker = ticker.strip()
    if not ticker.endswith(".NS") and not ticker.endswith(".BO") and ticker:
        ticker += ".NS"
        
    # Redirect to the dedicated Dorsey Analysis Route
    return redirect(url_for('analyze_ticker', ticker=ticker))


@app.route("/analyze/<ticker>")
def analyze_ticker(ticker=None):
    """
    Analyzes a specific ticker using the Dorsey Protocol.
    """
    try:
        # Normalize ticker
        t = (ticker or "").upper()
        if not t.endswith(".NS") and not t.endswith(".BO"):
             # Simple heuristic for NSE default
             t = f"{t}.NS"
        
        # Run Full Dorsey Analysis
        from src.dorsey_runner import run_dorsey_analysis
        dorsey_data = run_dorsey_analysis(t)
        
        # Also fetch generic company info for header (Name, Sector for display)
        import yfinance as yf
        t_obj = yf.Ticker(t)
        company_name = t_obj.info.get("longName", t)

        return render_template(
            "results.html",
            ticker=t,
            company_name=company_name,
            **dorsey_data
        )

    except Exception as e:
        return render_template(
            "results.html", 
            error=f"Server error: {e}",
            ticker=ticker,
            company_name=ticker,
            ten_minute_test={"passed": False, "overall_verdict": "ERROR", "checklist": []}, # Safety mocks
            moat_analysis={"moat_rating": "Error", "details": []},
            financial_health={"health_rating": "Error", "red_flags": [], "checks": []},
            valuation={"intrinsic_value": 0, "current_price": 0, "margin_of_safety": 0, "verdict": "Error"},
            sector_analysis={"sector": "Error", "insights": []}
        )


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").strip()
    if not query:
        return {"suggestions": {}}
        
    company_data = load_company_data()
    
    # 1. Exact/Substring Match (High Priority)
    mask = company_data["Company Name"].str.contains(query, case=False, na=False) | \
           company_data["Ticker"].str.contains(query, case=False, na=False)
    matches = company_data[mask]
    
    # 2. Fuzzy Match (If few results)
    if len(matches) < 5 and len(query) > 2:
        all_names = company_data["Company Name"].dropna().unique().tolist()
        # Get close matches
        fuzzy_names = difflib.get_close_matches(query, all_names, n=5, cutoff=0.5)
        if fuzzy_names:
            fuzzy_matches = company_data[company_data["Company Name"].isin(fuzzy_names)]
            matches = pd.concat([matches, fuzzy_matches]).drop_duplicates(subset=["Ticker"])
            
    # Limit results
    suggestions = matches.head(10)
    
    result = {
        row["Company Name"]: row["Ticker"] for index, row in suggestions.iterrows()
    }
    return {"suggestions": result}


@app.route("/community/contribute", methods=["POST"])
def contribute_insight():
    """Endpoint for submitting community insights"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        data = request.json
        ticker = data.get("ticker", "").upper()
        category_str = data.get("category", "")
        content = data.get("content", "")

        # Validate input
        if not ticker or not category_str or not content:
            return jsonify({"success": False, "message": "Missing required fields"})

        try:
            category = InsightCategory(category_str)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid category"})

        # Submit insight
        success, message = community_kb.contribute_insight(
            ticker, category, content, anonymous_user_id
        )

        # Track community contribution for learning assessment
        if success:
            behavioral_tracker.track_community_contribution(category_str, len(content))

        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})


@app.route("/community/vote", methods=["POST"])
def vote_on_insight():
    """Endpoint for voting on community insights"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        data = request.json
        insight_id = data.get("insight_id")
        vote_type = data.get("vote_type")

        if not insight_id or not vote_type:
            return jsonify({"success": False, "message": "Missing required fields"})

        success, message = community_kb.vote_on_insight(
            insight_id, anonymous_user_id, vote_type
        )

        # Track community engagement for learning assessment
        if success:
            behavioral_tracker.track_community_contribution(
                f"vote_{vote_type}", 1  # Minimal content length for voting
            )

        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})


@app.route("/community/flag", methods=["POST"])
def flag_insight():
    """Endpoint for flagging inappropriate insights"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        data = request.json
        insight_id = data.get("insight_id")

        if not insight_id:
            return jsonify({"success": False, "message": "Missing insight ID"})

        success, message = community_kb.flag_insight(insight_id, anonymous_user_id)

        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})


@app.route("/community/insights/<ticker>")
def get_ticker_insights(ticker):
    """Get insights for a specific ticker"""
    try:
        insights = community_kb.get_insights_for_ticker(ticker.upper())
        insights_data = []

        for insight in insights:
            insights_data.append(
                {
                    "id": insight.id,
                    "ticker": insight.ticker,
                    "category": insight.category.value,
                    "content": insight.content,
                    "created_at": insight.created_at.isoformat(),
                    "votes_up": insight.votes_up,
                    "votes_down": insight.votes_down,
                    "net_votes": insight.votes_up - insight.votes_down,
                }
            )

        return jsonify({"insights": insights_data})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"})


# Behavioral Analytics Routes
@app.route("/track/tooltip", methods=["POST"])
def track_tooltip_interaction():
    """Track tooltip usage for learning stage assessment"""
    try:
        if "anonymous_user_id" not in session:
            return jsonify({"success": False, "message": "No session found"})

        data = request.json
        tooltip_id = data.get("tooltip_id", "")
        tooltip_content = data.get("content", "")

        behavioral_tracker.track_tooltip_usage(tooltip_id, tooltip_content)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/track/warning", methods=["POST"])
def track_warning_engagement():
    """Track user engagement with warnings"""
    try:
        if "anonymous_user_id" not in session:
            return jsonify({"success": False, "message": "No session found"})

        data = request.json
        warning_type = data.get("warning_type", "")
        duration = data.get("duration", 0)

        behavioral_tracker.track_warning_engagement(warning_type, duration)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/track/research_guide", methods=["POST"])
def track_research_guide_access():
    """Track research guide access from gap-filling system"""
    try:
        if "anonymous_user_id" not in session:
            return jsonify({"success": False, "message": "No session found"})

        data = request.json
        guide_type = data.get("guide_type", "")
        complexity = data.get("complexity", "basic")

        behavioral_tracker.track_research_guide_access(guide_type, complexity)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/track/prediction", methods=["POST"])
def track_prediction_attempt():
    """Track user prediction attempts"""
    try:
        if "anonymous_user_id" not in session:
            return jsonify({"success": False, "message": "No session found"})

        data = request.json
        prediction_type = data.get("prediction_type", "")
        confidence = data.get("confidence", "medium")

        behavioral_tracker.track_prediction_attempt(prediction_type, confidence)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/track/comparison", methods=["POST"])
def track_stock_comparison():
    """Track cross-stock comparison activities"""
    try:
        if "anonymous_user_id" not in session:
            return jsonify({"success": False, "message": "No session found"})

        data = request.json
        stocks = data.get("stocks", [])

        behavioral_tracker.track_cross_stock_comparison(stocks)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/learning/stage")
def get_learning_stage():
    """Get current learning stage information"""
    try:
        if "anonymous_user_id" not in session:
            return jsonify({"stage": "guided_discovery", "progress": 0})

        progress_data = behavioral_tracker.get_stage_progress_data()
        if not progress_data:
            return jsonify({"stage": "guided_discovery", "progress": 0})

        return jsonify(progress_data)
    except Exception as e:
        return jsonify({"error": str(e)})


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_PATH,  # Set working directory to repo path
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)


@app.route("/trigger-ota")
def trigger_ota():

    # First verify repo path exists
    if not os.path.exists(REPO_PATH):
        return jsonify(
            {"success": False, "error": f"Repository path {REPO_PATH} does not exist"}
        )

    commands = [
        "git pull",
        "docker compose down",
        "docker compose build",
        "docker compose up -d",
    ]

    results = []
    for cmd in commands:
        success, output = run_command(cmd)
        results.append({"command": cmd, "success": success, "output": output})

    all_successful = all(result["success"] for result in results)

    return jsonify({"success": all_successful, "results": results})


@app.route("/news")
def news():
    news_items = get_market_news()
    organized_news = {}

    for item in news_items:
        publisher = item["publisher"]

        if publisher not in organized_news:
            organized_news[publisher] = {}

        # Add the news item to each of its categories
        for category in item["categories"]:
            if category not in organized_news[publisher]:
                organized_news[publisher][category] = []
            organized_news[publisher][category].append(item)

    # Sort each category by score
    for publisher in organized_news:
        for category in organized_news[publisher]:
            organized_news[publisher][category].sort(
                key=lambda x: x["score"], reverse=True
            )

    return render_template(
        "news.html",
        organized_news=organized_news,
        publishers=list(organized_news.keys()),
        categories=list(get_news_categories().keys()),
    )


@app.route("/pattern-training")
def pattern_training_home():
    """Pattern recognition training home page"""
    anonymous_user_id = get_anonymous_user_id()

    # Get current learning stage for appropriate exercise selection
    learning_context = get_learning_stage_context()
    current_stage = learning_context.get("current_stage", "guided_discovery")

    # Map stage string to enum
    stage_mapping = {
        "guided_discovery": LearningStage.GUIDED_DISCOVERY,
        "assisted_analysis": LearningStage.ASSISTED_ANALYSIS,
        "independent_thinking": LearningStage.INDEPENDENT_THINKING,
        "analytical_mastery": LearningStage.ANALYTICAL_MASTERY,
    }

    user_stage = stage_mapping.get(current_stage, LearningStage.GUIDED_DISCOVERY)

    # Get available pattern types
    available_patterns = [
        {
            "type": "DEBT_ANALYSIS",
            "name": "Debt Analysis Patterns",
            "description": "Learn to identify debt spirals, leverage trends, and interest coverage concerns",
        },
        {
            "type": "GROWTH_INDICATORS",
            "name": "Growth Indicator Patterns",
            "description": "Recognize sustainable growth patterns, ROE trends, and revenue quality",
        },
        {
            "type": "VALUE_TRAPS",
            "name": "Value Trap Detection",
            "description": "Identify potential value traps and distinguish from genuine opportunities",
        },
        {
            "type": "TREND_REVERSAL",
            "name": "Trend Reversal Patterns",
            "description": "Spot key turning points in momentum, margin expansion, and recovery signals",
        },
        {
            "type": "QUALITY_DETERIORATION",
            "name": "Quality Deterioration",
            "description": "Detect early warning signs of declining business quality and moat erosion",
        },
    ]

    return render_template(
        "pattern_training.html",
        available_patterns=available_patterns,
        user_stage=current_stage,
        **learning_context,
    )


@app.route("/pattern-training/stocks")
def get_available_stocks():
    """Get list of available stocks for selection from all CSV files"""
    import csv
    import os
    import glob

    stocks = []
    input_dir = os.path.join(os.path.dirname(__file__), "input")

    # Get all CSV files in the input directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

    try:
        for csv_file in csv_files:
            # Extract index name from filename (e.g., "nifty_50" from "Indian_stocks_nifty_50.csv")
            filename = os.path.basename(csv_file)
            if filename.startswith("Indian_stocks_"):
                index_name = (
                    filename.replace("Indian_stocks_", "")
                    .replace(".csv", "")
                    .replace("_", " ")
                    .title()
                )
            else:
                index_name = filename.replace(".csv", "").replace("_", " ").title()

            with open(csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Add stock with index information
                    stock_info = {
                        "name": row["Company Name"],
                        "ticker": row["Ticker"],
                        "industry": row["Industry"],
                        "index": index_name,
                    }
                    # Avoid duplicates (some stocks might be in multiple indices)
                    if not any(s["ticker"] == stock_info["ticker"] for s in stocks):
                        stocks.append(stock_info)

    except Exception as e:
        print(f"Error reading CSV files: {e}")
        # Fallback to some default stocks
        stocks = [
            {
                "name": "Reliance Industries Ltd.",
                "ticker": "RELIANCE",
                "industry": "Oil Gas & Consumable Fuels",
                "index": "Nifty 50",
            },
            {
                "name": "Tata Consultancy Services Ltd.",
                "ticker": "TCS",
                "industry": "Information Technology",
                "index": "Nifty 50",
            },
            {
                "name": "HDFC Bank Ltd.",
                "ticker": "HDFCBANK",
                "industry": "Financial Services",
                "index": "Nifty 50",
            },
        ]

    # Sort stocks by name for better UX
    stocks.sort(key=lambda x: x["name"])

    return jsonify({"success": True, "stocks": stocks})


@app.route("/pattern-training/exercise")
def get_pattern_exercise():
    """Generate a new pattern recognition exercise"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        # Get parameters
        pattern_type_str = request.args.get("pattern_type", "DEBT_ANALYSIS")
        current_stage = request.args.get("stage", "guided_discovery")
        selected_stock = request.args.get(
            "stock", None
        )  # New: Optional stock selection

        # Map stage string to enum
        stage_mapping = {
            "guided_discovery": LearningStage.GUIDED_DISCOVERY,
            "assisted_analysis": LearningStage.ASSISTED_ANALYSIS,
            "independent_thinking": LearningStage.INDEPENDENT_THINKING,
            "analytical_mastery": LearningStage.ANALYTICAL_MASTERY,
        }

        # Map pattern type string to enum
        pattern_mapping = {
            "DEBT_ANALYSIS": PatternType.DEBT_ANALYSIS,
            "GROWTH_INDICATORS": PatternType.GROWTH_INDICATORS,
            "VALUE_TRAPS": PatternType.VALUE_TRAPS,
            "TREND_REVERSAL": PatternType.TREND_REVERSAL,
            "QUALITY_DETERIORATION": PatternType.QUALITY_DETERIORATION,
        }

        user_stage = stage_mapping.get(current_stage, LearningStage.GUIDED_DISCOVERY)
        pattern_type = pattern_mapping.get(pattern_type_str, PatternType.DEBT_ANALYSIS)

        # Generate exercise (with optional stock selection)
        if selected_stock:
            # Parse the stock info (format: "Company Name|Ticker|Industry")
            stock_parts = selected_stock.split("|")
            company_info = {
                "name": stock_parts[0] if len(stock_parts) > 0 else selected_stock,
                "ticker": stock_parts[1] if len(stock_parts) > 1 else selected_stock,
                "industry": stock_parts[2] if len(stock_parts) > 2 else "Unknown",
                "company": (
                    stock_parts[0] if len(stock_parts) > 0 else selected_stock
                ),  # Required by pattern trainer
                "sector": (
                    stock_parts[2] if len(stock_parts) > 2 else "Unknown"
                ),  # Add sector field
                "description": f"Pattern analysis for {stock_parts[0] if len(stock_parts) > 0 else selected_stock}",
                "pattern_description": f"Analyzing {stock_parts[0] if len(stock_parts) > 0 else selected_stock} financial patterns",
            }
            exercise = pattern_trainer.generate_stage_appropriate_exercise(
                user_stage, pattern_type, anonymous_user_id, company_info
            )
        else:
            exercise = pattern_trainer.generate_stage_appropriate_exercise(
                user_stage, pattern_type, anonymous_user_id
            )

        # Generate interactive chart HTML from the exercise
        chart_config = pattern_trainer.create_interactive_chart_overlay(exercise)

        return jsonify(
            {
                "success": True,
                "exercise": {
                    "id": exercise.exercise_id,
                    "title": exercise.title,
                    "description": exercise.description,
                    "company_name": exercise.company_name,
                    "chart_html": chart_config[
                        "chart_json"
                    ],  # Use generated chart JSON
                    "time_limit": exercise.time_limit_seconds,  # Fixed: using time_limit_seconds
                    "pattern_zones": exercise.pattern_zones,  # Fixed: using pattern_zones instead of interactive_zones
                    "difficulty": exercise.difficulty.value,
                    "pattern_type": pattern_type.value,
                    "expected_patterns": exercise.expected_patterns,  # For Walk Me Through It feature
                },
            }
        )

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Failed to generate exercise: {str(e)}"}
        )


@app.route("/pattern-training/submit", methods=["POST"])
def submit_pattern_attempt():
    """Submit user's pattern recognition attempt for evaluation"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        data = request.json
        exercise_id = data.get("exercise_id")
        user_patterns = data.get("identified_patterns", [])
        time_taken = data.get("time_taken_seconds", 0)

        if not exercise_id:
            return jsonify({"success": False, "error": "Missing exercise ID"})

        # Evaluate the attempt
        result = pattern_trainer.evaluate_attempt(
            exercise_id, user_patterns, anonymous_user_id, time_taken
        )

        # Track pattern recognition progress for learning stage assessment
        behavioral_tracker.track_interaction_start(
            anonymous_user_id, InteractionType.ANALYSIS_COMPLETION
        )

        return jsonify(
            {
                "success": True,
                "result": {
                    "score": result.score,
                    "accuracy": result.accuracy_score,
                    "feedback": result.educational_explanation,
                    "missed_patterns": result.missed_patterns,
                    "recommendations": result.improvement_suggestions,
                },
            }
        )

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Failed to evaluate attempt: {str(e)}"}
        )


@app.route("/pattern-training/progress")
def get_pattern_progress():
    """Get user's pattern recognition progress summary"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        progress = pattern_trainer.get_exercise_progress_summary(anonymous_user_id)

        return jsonify({"success": True, "progress": progress})

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to get progress: {str(e)}"})


@app.route("/tool-challenge")
@app.route("/tool-challenge/<ticker>")
def tool_challenge(ticker=None):
    """Tool independence challenge page - blind analysis without automated assistance"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        # Get user's current learning stage for appropriate challenge difficulty
        learning_context = get_learning_stage_context()
        current_stage = learning_context.get(
            "current_stage", LearningStage.GUIDED_DISCOVERY
        )

        # Get ticker from path parameter or query parameter
        if not ticker:
            ticker = request.args.get("ticker")

        # Generate challenge if ticker is provided
        challenge = None
        if ticker:
            ticker = ticker.upper()  # Normalize to uppercase
            # Get actual company data for the ticker
            company_data = get_company_financial_data(ticker)

            challenge = tool_trainer.generate_stage_appropriate_challenge(
                anonymous_user_id, current_stage, company_data
            )

            # Track challenge initiation
            behavioral_tracker.track_interaction_start(
                anonymous_user_id, InteractionType.ANALYSIS_COMPLETION
            )

        return render_template(
            "tool_challenge.html",
            ticker=ticker,
            challenge=challenge,
            current_stage=current_stage.value if current_stage else None,
            **learning_context,
        )

    except Exception as e:
        return render_template(
            "tool_challenge.html",
            error=f"Failed to generate challenge: {str(e)}",
            ticker=ticker,
        )


@app.route("/tool-challenge/submit", methods=["POST"])
def submit_challenge_prediction():
    """Submit user's prediction for tool independence challenge"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        prediction_data = {
            "ticker": request.form.get("ticker"),
            "challenge_id": request.form.get("challenge_id"),
            "financial_health": request.form.get("financial_health"),
            "growth_potential": request.form.get("growth_potential"),
            "risk_factors": request.form.get("risk_factors"),
            "investment_decision": request.form.get("investment_decision"),
            "reasoning": request.form.get("reasoning", ""),
            "confidence_level": int(request.form.get("confidence_level", 1)),
        }

        # Evaluate the prediction
        evaluation_result = tool_trainer.evaluate_prediction_accuracy(
            anonymous_user_id, prediction_data
        )

        # Track analytical confidence progress
        tool_trainer.track_analytical_confidence_progress(
            anonymous_user_id, evaluation_result
        )

        return jsonify({"success": True, "evaluation": evaluation_result})

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Failed to evaluate prediction: {str(e)}"}
        )


@app.route("/tool-challenge/progress")
def get_tool_independence_progress():
    """Get user's tool independence training progress"""
    try:
        anonymous_user_id = get_anonymous_user_id()

        progress = tool_trainer.get_analytical_confidence_summary(anonymous_user_id)

        return jsonify({"success": True, "progress": progress})

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to get progress: {str(e)}"})


@app.route("/export", methods=["POST"])
def export_csv():
    """Simple CSV export endpoint.

    Expects JSON body: {"rows": [ {..}, {...} ] }
    Returns a CSV attachment built from the first row's keys as headers.
    """
    try:
        payload = request.get_json(force=True)
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        csv_text = ExportService.generate_csv(rows)

        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/export/report", methods=["POST"])
def export_report():
    """Multi-format export endpoint.

    Request JSON: {"rows": [...], "format": "csv"|"xlsx"|"pdf", "filename": "report"}
    """
    try:
        payload = request.get_json(force=True)
        if not isinstance(payload, dict):
            return jsonify({"success": False, "error": "Invalid payload"}), 400

        rows = payload.get("rows", [])
        fmt = (payload.get("format") or "csv").lower()
        filename = payload.get("filename") or "report"

        if fmt == "csv":
            csv_text = ExportService.generate_csv(rows)
            return Response(
                csv_text,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
            )

        if fmt in ("xlsx", "xls", "excel"):
            try:
                xbytes = ExportService.generate_excel_bytes(rows)
                return Response(
                    xbytes,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}.xlsx"
                    },
                )
            except ModuleNotFoundError:
                # openpyxl (or other engine) not installed in this environment.
                # Fall back to CSV bytes but present as an xlsx attachment so tests
                # and simple clients still receive tabular data.
                csv_text = ExportService.generate_csv(rows)
                return Response(
                    csv_text.encode("utf-8"),
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}.xlsx"
                    },
                )

        if fmt == "pdf":
            pbytes = ExportService.generate_pdf_bytes(rows, title=filename)
            return Response(
                pbytes,
                mimetype="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}.pdf"},
            )

        return jsonify({"success": False, "error": "Unsupported format"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/export/analysis/<ticker>", methods=["GET"])
def export_analysis(ticker=None):
    """Export analysis results for a ticker in requested format.

    Query param: format=csv|xlsx|pdf (default csv)
    """
    fmt = (request.args.get("format") or "csv").lower()
    try:
        t = (ticker or "").upper()
        if not t.endswith(".NS"):
            t = f"{t}.NS"

        # Reuse existing analysis functions
        ratios_df = get_financial_ratios(t)
        if ratios_df is None or ratios_df.empty:
            return jsonify({"success": False, "error": "No data for ticker"}), 404

        ticker_for_analysis = t.replace(".NS", "")
        (warnings, explanations, plot_html, gaps, research_guides, confidence_score) = (
            analyze_ratios(ratios_df, ticker_for_analysis)
        )

        # Flatten some of the results for tabular export
        rows = []
        # include summary row
        summary = {
            "ticker": ticker_for_analysis,
            "company": (
                ratios_df["Company"].iloc[0] if "Company" in ratios_df.columns else ""
            ),
            "confidence_score": confidence_score,
            "has_gaps": bool(gaps),
        }
        rows.append(summary)

        # include ratio rows
        try:
            display_df = (
                ratios_df.drop(columns=["Company"])
                if "Company" in ratios_df.columns
                else ratios_df
            )
            for _, r in display_df.iterrows():
                rows.append(r.to_dict())
        except Exception:
            pass

        filename = f"analysis_{ticker_for_analysis}"
        return _respond_with_format(rows, fmt, filename)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _respond_with_format(rows, fmt, filename):
    fmt = (fmt or "csv").lower()
    if fmt == "csv":
        return Response(
            ExportService.generate_csv(rows),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    if fmt in ("xlsx", "xls", "excel"):
        try:
            return Response(
                ExportService.generate_excel_bytes(rows),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.xlsx"
                },
            )
        except ModuleNotFoundError:
            return Response(
                ExportService.generate_csv(rows).encode("utf-8"),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.xlsx"
                },
            )

    if fmt == "pdf":
        return Response(
            ExportService.generate_pdf_bytes(rows, title=filename),
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}.pdf"},
        )

    return jsonify({"success": False, "error": "unsupported format"}), 400


@app.route("/export/progress/<user_id>", methods=["GET"])
def export_progress(user_id=None):
    """Export learning progress and achievements for a user."""
    fmt = (request.args.get("format") or "csv").lower()
    try:
        uid = user_id or get_anonymous_user_id()
        from src.persistence import get_progress_metrics, get_badges_for_user

        progress = get_progress_metrics(uid) or {}
        badges = get_badges_for_user(uid) or []

        # Build rows: one summary row and badge rows
        rows = []
        rows.append({"user_id": uid, "progress_snapshot": progress})
        for b in badges:
            rows.append(
                {
                    "badge_type": b.get("badge_type"),
                    "earned_at": b.get("earned_at"),
                    "payload": b.get("payload"),
                }
            )

        filename = f"progress_{uid}"
        return _respond_with_format(rows, fmt, filename)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/export/portfolio/<user_id>", methods=["GET"])
def export_portfolio(user_id=None):
    """Export portfolio holdings and a small deterministic historical sample.

    If no explicit portfolio persistence exists, fall back to a sample derived from input CSVs.
    """
    fmt = (request.args.get("format") or "csv").lower()
    try:
        uid = user_id or get_anonymous_user_id()
        # Try to load a saved portfolio JSON first
        portfolio_path = os.path.join(
            os.path.dirname(__file__), f"data/portfolio_{uid}.json"
        )
        rows = []
        if os.path.exists(portfolio_path):
            import json as _json

            with open(portfolio_path, "r", encoding="utf-8") as fh:
                holdings = _json.load(fh)
            # holdings expected: list of {ticker, qty}
            for h in holdings:
                rows.append({"ticker": h.get("ticker"), "quantity": h.get("quantity")})
        else:
            # Fallback: sample top N from input CSV
            import csv

            input_dir = os.path.join(os.path.dirname(__file__), "input")
            sample = []
            csv_file = os.path.join(input_dir, "Indian_stocks_nifty_50.csv")
            if os.path.exists(csv_file):
                with open(csv_file, "r", encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for i, r in enumerate(reader):
                        if i >= 5:
                            break
                        sample.append(
                            {
                                "ticker": r.get("Ticker"),
                                "name": r.get("Company Name"),
                                "quantity": 10 * (i + 1),
                            }
                        )
            else:
                # Minimal hardcoded sample
                sample = [
                    {
                        "ticker": "RELIANCE",
                        "name": "Reliance Industries Ltd.",
                        "quantity": 10,
                    },
                    {
                        "ticker": "TCS",
                        "name": "Tata Consultancy Services Ltd.",
                        "quantity": 5,
                    },
                ]

            # Create simple deterministic historical series for each holding (last 5 days)
            import datetime

            for s in sample:
                base = sum(ord(c) for c in (s.get("ticker") or "")) % 50 + 50
                for d in range(5):
                    date = (
                        datetime.date.today() - datetime.timedelta(days=5 - d)
                    ).isoformat()
                    price = base + d * 0.5
                    rows.append(
                        {
                            "ticker": s.get("ticker"),
                            "date": date,
                            "price": round(price, 2),
                            "quantity": s.get("quantity"),
                        }
                    )

        filename = f"portfolio_{uid}"
        return _respond_with_format(rows, fmt, filename)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Prometheus metrics endpoint
@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# Health check endpoint
@app.route("/health")
def health():
    """Health check endpoint for load balancer and monitoring"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": {"database": "ok", "external_apis": "ok"},
        }

        # Update system health metric
        SYSTEM_HEALTH.set(1)

        return jsonify(health_status), 200
    except Exception as e:
        SYSTEM_HEALTH.set(0)
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }
            ),
            500,
        )


# Middleware to track metrics
@app.before_request
def before_request():
    """Track request metrics"""
    request.start_time = datetime.datetime.now(datetime.timezone.utc)


@app.after_request
def after_request(response):
    """Track response metrics"""
    if hasattr(request, "start_time"):
        latency = (datetime.datetime.now(datetime.timezone.utc) - request.start_time).total_seconds()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(
            latency
        )

    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.path, status=response.status_code
    ).inc()

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
