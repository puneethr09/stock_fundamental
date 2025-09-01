from app import get_company_financial_data

data = get_company_financial_data("RELIANCE")
print("business_description:", repr(data.get("business_description")))
print("business_description_full:", repr(data.get("business_description_full")))
print("Length of full:", len(data.get("business_description_full", "")))
