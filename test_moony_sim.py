from calculator import TokenTypeCalculator, SCENARIO_LIBRARY
from main import run_moony_scenario

calc = run_moony_scenario()
state = calc.compute()
fp = state['fingerprint']
print(f"Moony FP: {fp}")

search_res = calc.semantic_search(fp)
print(f"Closest match: {search_res['scenario']}")
print(f"Similarity: {search_res['report'].similarity}")
