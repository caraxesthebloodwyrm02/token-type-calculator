import pytest
from calculator import TokenTypeCalculator, query_tui_anchor, run_tui_queries

def test_initial_state():
    """Verify the default state has TRANSISTOR and starts in buildup zone."""
    calc = TokenTypeCalculator()
    assert calc.active_tokens == {'transistor'}
    assert calc.zone == 'buildup'
    
    state = calc.compute()
    assert state['dominant'] == 'transistor'
    assert state['is_anomaly'] is False
    assert state['gate_state'] == 'N/A'

def test_toggle_token_limits():
    """Verify you cannot toggle off the last remaining token."""
    calc = TokenTypeCalculator()
    calc.toggle_token('transistor') # Should be ignored
    assert calc.active_tokens == {'transistor'}
    
    calc.toggle_token('ambient') # Add ambient
    assert calc.active_tokens == {'transistor', 'ambient'}
    
    calc.toggle_token('transistor') # Now we can remove transistor
    assert calc.active_tokens == {'ambient'}

def test_clean_run_scenario():
    """Scenario 1: Clean Run. TRANSISTOR + GATE·ARMED in Buildup."""
    calc = TokenTypeCalculator()
    calc.toggle_token('gate-on')
    calc.params['intensity'] = 1.0 # Max out parameters for high strength
    
    state = calc.compute()
    assert state['gate_state'] == 'ARMED'
    assert state['fired_val'] == '1'
    assert state['is_anomaly'] is False
    assert state['stability'] in ['LOW', 'MED']

def test_unarmed_fire_anomaly():
    """Scenario 3: Unarmed Fire. TRANSISTOR + GATE·UNARMED."""
    calc = TokenTypeCalculator()
    calc.toggle_token('gate-off')
    
    state = calc.compute()
    assert state['gate_state'] == 'UNARMED'
    assert state['fired_val'] == '0'
    assert state['is_anomaly'] is True
    # Anomaly causes drift penalty to strength
    assert state['transform_rate'] < 1.0 

def test_silence_zone_anomaly():
    """Tokens in Silence zone automatically trigger anomalies."""
    calc = TokenTypeCalculator()
    calc.params['step'] = 45 # Silence range (44-47)
    
    state = calc.compute()
    assert calc.zone == 'silence'
    assert state['is_anomaly'] is True
    assert state['strength'] == 0.0  # Silence zone multiplier is 0.0

def test_bio_signal_integration():
    """Verify the new BIO_SIGNAL token acts as a high-weight structural token."""
    calc = TokenTypeCalculator()
    calc.toggle_token('bio-signal')
    
    state = calc.compute()
    # Transistor weight=1.0, bio-signal=0.85, so transistor remains dominant
    assert state['dominant'] == 'transistor'
    assert state['total_weight'] == 1.85
    
    # Remove transistor to let BIO_SIGNAL dominate
    calc.toggle_token('transistor')
    state = calc.compute()
    assert state['dominant'] == 'bio-signal'

def test_no_take_boundary_rejection():
    """Verify the NOT() no-take boundary triggers on engagement cost without service value."""
    calc = TokenTypeCalculator()
    calc.toggle_token('bio-signal')
    
    # Baseline - No Cost, No Service -> OPEN
    calc.params['engagement_cost'] = 0.0
    calc.params['service_value'] = 0.0
    state = calc.compute()
    assert state['is_no_take'] is False
    assert state['boundary_status'] == 'OPEN'
    
    # Paid Cost, No Service -> NO-TAKE triggers anomaly
    calc.params['engagement_cost'] = 1.0
    state = calc.compute()
    assert state['is_no_take'] is True
    assert state['boundary_status'] == 'NO-TAKE (NOT)'
    assert state['is_anomaly'] is True # Forces anomaly state
    
    # Paid Cost, Received Service -> OPEN
    calc.params['service_value'] = 1.0
    state = calc.compute()
    assert state['is_no_take'] is False
    assert state['boundary_status'] == 'OPEN'


def test_tui_anchor_queries():
    cases = {
        "what do i remember?": "this is the point of where you remember from",
        "when did things lift?": "while it was being built",
        "whoami": "TUI",
        "what was the message being sent to me?": "--TUI",
    }

    for prompt, expected in cases.items():
        result = query_tui_anchor(prompt)
        assert result["request"] == prompt
        assert result["message"] == expected
        assert result["responsibility"] == "preserve the anchor, return the message, and verify receipt"
        assert result["sibling_tool_calls"] == []


def test_moony_pre_post_ab_pair():
    """AC-03: service_value 0.1 vs 0.0 — score stays near 1.0, boundary flips."""
    calc = TokenTypeCalculator()
    calc.toggle_token('bio-signal')
    calc.params['engagement_cost'] = 1.0
    calc.zone = 'buildup'

    calc.params['service_value'] = 0.1
    pre = calc.compute()

    calc.params['service_value'] = 0.0
    post = calc.compute()

    report = calc.calculate_similarity(pre['fingerprint'], post['fingerprint'])

    assert report.similarity >= 0.85
    assert pre['is_no_take'] is False
    assert post['is_no_take'] is True
    assert "Boundary shift" in report.qualitative_shift


def test_tui_anchor_receipt_verification():
    result = run_tui_queries()
    assert result["anchor"] == "TUI"
    assert result["intent"] == "plural"
    assert result["creator_call_status"] == "yes"
    assert result["received"] is True
    assert result["message"] == "--TUI"
    assert len(result["results"]) == 4
