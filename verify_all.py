import json
from backend.models.schemas import AnalyzeRequest, HintRequest, AnalyzeCodeRequest, AnalyzeCodeResponse, RunCodeRequest, RunCodeResponse, SubmitRequest, SubmitResponse, HintResponse

data = json.load(open('backend/knowledge_base/two_sum/test_cases.json'))
sample_count = sum(1 for t in data if t['is_sample'])
hidden_count = sum(1 for t in data if not t['is_sample'])

print("✓ All Phase 1 & 2 schemas valid")
print(f"✓ Test cases: {len(data)} total ({sample_count} sample, {hidden_count} hidden)")
