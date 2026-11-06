"""Decision-branch test cases for PES1UG24CS308."""

import pytest

from coffee_shop_order import check_espresso_machine, process_order_batch


@pytest.mark.parametrize(
    ("orders", "tax_rate"), [({}, 0.05), ([], -0.01)]
)
def test_both_invalid_input_decisions(orders, tax_rate):
    with pytest.raises(ValueError):
        process_order_batch(orders, tax_rate)


def test_paid_and_unpaid_orders_and_default_size():
    result = process_order_batch(
        [{"paid": False}, {"paid": True, "customizations": []}], 0
    )
    assert result == {"total": 4.5, "status": "COMPLETED"}


@pytest.mark.parametrize(
    ("size", "expected"),
    [("small", 3.0), ("medium", 4.5), ("large", 6.0), ("unknown", 0.0)],
)
def test_each_size_decision(size, expected):
    result = process_order_batch([{"paid": True, "size": size}], 0)
    assert result["total"] == expected


@pytest.mark.parametrize(
    ("customizations", "strict", "member", "expected", "status"),
    [
        ([{"type": "syrup", "cost": -0.5}], False, False, 4.5, "COMPLETED"),
        ([{"type": "syrup", "cost": 1.0}], False, False, 5.5, "COMPLETED"),
        ([{"type": "syrup", "cost": 2.0}], True, False, 6.0, "COMPLETED"),
        ([{"type": "milk", "cost": 0.5}], False, True, 4.5, "COMPLETED"),
        ([{"type": "allergen_alert"}], False, False, 4.5, "COMPLETED"),
        ([{"type": "allergen_alert"}], True, False, 0.0, "NO_SALE"),
    ],
)
def test_customization_and_allergy_decisions(
    customizations, strict, member, expected, status
):
    order = {
        "paid": True,
        "strict_allergy": strict,
        "is_member": member,
        "customizations": customizations,
    }
    assert process_order_batch([order], 0) == {"total": expected, "status": status}


def test_audit_threshold_true_and_false_and_normal_sale():
    audited = {
        "paid": True,
        "customizations": [{"type": "allergen_alert"} for _ in range(5)],
    }
    normal = {"paid": True}
    assert process_order_batch([audited], 0)["status"] == "AUDIT_REJECTED"
    assert process_order_batch([normal], 0)["status"] == "COMPLETED"
    assert process_order_batch([], 0)["status"] == "NO_SALE"


def test_espresso_data_empty_cycles_normal_reset_and_shutdown():
    assert check_espresso_machine([]) == "NO_DATA"
    assert check_espresso_machine([[], [97, 95, 97]]) == "OPTIMAL"
    assert check_espresso_machine([[96.1, 97]]) == "SHUTDOWN"
