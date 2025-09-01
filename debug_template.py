from flask import Flask, render_template_string
from src.tool_independence_trainer import ToolIndependenceTrainer
from src.educational_framework import LearningStage
from app import get_company_financial_data

# Test the template rendering
app = Flask(__name__)

# Get test data
company_data = get_company_financial_data("RELIANCE")
trainer = ToolIndependenceTrainer()
challenge = trainer.generate_stage_appropriate_challenge(
    "test_user", LearningStage.GUIDED_DISCOVERY, company_data
)

# Test template snippet
template = """
<div class="business-description-container">
  <h5 class="card-text text-primary text-center business-description-text"
      style="cursor: pointer;"
      data-full-description="{{ challenge.company_basic_info.get('business_description_full', value)|tojson|safe }}"
      onclick="showBusinessDescription(this)">
    {{ value }}
    <i class="fas fa-external-link-alt ml-2" style="font-size: 0.8em;"></i>
  </h5>
  <small class="text-muted text-center d-block">Click to read full description</small>
</div>
"""

with app.app_context():
    result = render_template_string(
        template,
        challenge=challenge,
        value=challenge.company_basic_info["business_description"],
    )

print("Rendered HTML:")
print(result)
print("\n" + "=" * 50 + "\n")

# Check the data attribute content
full_desc = challenge.company_basic_info.get("business_description_full", "")
print(f"Full description length: {len(full_desc)}")
print(f"Full description preview: {full_desc[:200]}...")
