from src.tool_independence_trainer import ToolIndependenceTrainer
from src.educational_framework import LearningStage
from app import get_company_financial_data

# Get company data
company_data = get_company_financial_data("RELIANCE")
print("Company data keys:", list(company_data.keys()))
print("Has business_description_full:", "business_description_full" in company_data)

# Create trainer and generate challenge
trainer = ToolIndependenceTrainer()
challenge = trainer.generate_stage_appropriate_challenge(
    "test_session", LearningStage.GUIDED_DISCOVERY, company_data
)

print("Challenge company_basic_info keys:", list(challenge.company_basic_info.keys()))
print(
    "Has business_description_full in challenge:",
    "business_description_full" in challenge.company_basic_info,
)

if "business_description_full" in challenge.company_basic_info:
    print(
        "Full description length:",
        len(challenge.company_basic_info["business_description_full"]),
    )
    print(
        "Truncated length:",
        len(challenge.company_basic_info.get("business_description", "")),
    )
