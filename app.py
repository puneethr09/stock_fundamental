from flask import Flask, render_template, jsonify, Response, request, session
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
import subprocess, os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management
REPO_PATH = "/home/puneeth/repo/stock_fundamental/"

# Initialize community knowledge base
community_kb = CommunityKnowledgeBase()

# Initialize pattern recognition trainer
pattern_trainer = PatternRecognitionTrainer()


def get_anonymous_user_id():
    """Get or create anonymous user ID for session"""
    if "anonymous_user_id" not in session:
        session["anonymous_user_id"] = community_kb.generate_anonymous_user_id(
            str(request.remote_addr) + str(request.user_agent)
        )
    return session["anonymous_user_id"]


@app.route("/")
@app.route("/home")  # Adding both routes for flexibility
def home():
    # Initialize session for anonymous user tracking
    anonymous_user_id = get_anonymous_user_id()

    # Get learning stage context for UI adaptation
    learning_context = get_learning_stage_context()

    news_items = get_market_news()
    return render_template("index.html", news=news_items, **learning_context)


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    # Initialize session for anonymous user tracking
    anonymous_user_id = get_anonymous_user_id()

    news_items = get_market_news()
    if request.method == "POST":
        ticker = request.form["ticker"].upper() + ".NS"
    else:
        ticker = request.args.get("ticker", "").upper() + ".NS"

    # Track analysis start
    behavioral_tracker.track_interaction_start(
        anonymous_user_id, InteractionType.ANALYSIS_COMPLETION
    )

    ratios_df = get_financial_ratios(ticker)
    if ratios_df is not None and not ratios_df.empty:
        # Pass ticker for gap analysis (remove .NS suffix)
        ticker_for_analysis = ticker.replace(".NS", "")
        warnings, explanations, plot_html, gaps, research_guides, confidence_score = (
            analyze_ratios(ratios_df, ticker_for_analysis)
        )
        company_name = ratios_df["Company"].iloc[0]
        display_df = ratios_df.drop(columns=["Company"])

        # Get community insights for this ticker
        community_insights = community_kb.get_insights_for_ticker(ticker_for_analysis)

        # Track successful analysis completion
        behavioral_tracker.track_analysis_completion(
            ticker_for_analysis, "comprehensive" if gaps else "basic"
        )

        # Get learning stage context for UI adaptation
        analysis_context = {
            "company_name": company_name,
            "ticker": ticker_for_analysis,
            "has_gaps": bool(gaps),
            "confidence_score": confidence_score,
        }
        learning_context = get_learning_stage_context()

        # Adapt content based on learning stage
        content_data = {
            "warnings": warnings,
            "explanations": explanations,
            "gaps": gaps,
            "research_guides": research_guides,
            "community_insights": community_insights,
        }
        adapted_content = adapt_content_for_stage(content_data, analysis_context)

        # Use adapted content instead of original to avoid keyword conflicts
        return render_template(
            "results.html",
            tables=[display_df.to_html(classes="data table-hover", index=False)],
            titles=display_df.columns.values,
            plot_html=plot_html,
            company_name=company_name,
            news=news_items,
            insight_categories=InsightCategory,
            ticker=ticker_for_analysis,
            confidence_score=confidence_score,
            zip=zip,
            **learning_context,
            **adapted_content,
        )
    else:
        return render_template(
            "results.html",
            error="No data available for the provided ticker.",
            plot_html=None,
            zip=zip,
            **get_learning_stage_context(),
        )


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").strip()
    company_data = load_company_data()
    suggestions = company_data[
        company_data["Company Name"].str.contains(query, case=False, na=False)
    ]
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
                    "accuracy": result.accuracy,
                    "feedback": result.feedback,
                    "missed_patterns": result.missed_patterns,
                    "recommendations": result.improvement_recommendations,
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
