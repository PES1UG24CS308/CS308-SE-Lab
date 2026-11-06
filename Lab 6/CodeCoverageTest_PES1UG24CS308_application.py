"""Line-coverage test cases for PES1UG24CS308."""

import pytest

from coffee_shop_order import check_espresso_machine, process_order_batch


def test_rejects_invalid_orders_and_negative_tax():
    with pytest.raises(ValueError):
        process_order_batch({}, 0.05)
    with pytest.raises(ValueError):
        process_order_batch([], -0.01)


def test_unpaid_orders_are_skipped_and_empty_batch_has_no_sale():
    result = process_order_batch([{"paid": False, "size": "small"}], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


@pytest.mark.parametrize(
    ("size", "base"), [("small", 3.0), ("medium", 4.5), ("large", 6.0)]
)
def test_each_drink_size_is_priced(size, base):
    result = process_order_batch([{"paid": True, "size": size}], 0)
    assert result == {"total": base, "status": "COMPLETED"}


def test_unknown_size_is_rejected():
    result = process_order_batch([{"paid": True, "size": "jumbo"}], 0.2)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_customizations_syrup_cap_other_cost_and_member_discount():
    order = {
        "paid": True,
        "size": "medium",
        "is_member": True,
        "customizations": [
            {"type": "syrup", "cost": 1.0},
            {"type": "syrup", "cost": 2.0},
            {"type": "oat_milk", "cost": 0.5},
        ],
    }
    assert process_order_batch([order], 0.1) == {
        "total": 7.43,
        "status": "COMPLETED",
    }


def test_negative_customization_cost_is_rejected():
    order = {"paid": True, "customizations": [{"type": "syrup", "cost": -1}]}
    assert process_order_batch([order], 0) == {
        "total": 4.5,
        "status": "COMPLETED",
    }


def test_allergen_alert_rejects_item_for_strict_allergy_order():
    order = {
        "paid": True,
        "strict_allergy": True,
        "customizations": [{"type": "allergen_alert", "cost": 0}],
    }
    assert process_order_batch([order], 0) == {"total": 0.0, "status": "NO_SALE"}


def test_many_rejected_customizations_trigger_audit_status():
    order = {
        "paid": True,
        "customizations": [{"type": "allergen_alert"} for _ in range(5)],
    }
    assert process_order_batch([order], 0.05) == {
        "total": 4.73,
        "status": "AUDIT_REJECTED",
    }


def test_espresso_monitor_no_data_and_normal_cycles():
    assert check_espresso_machine([]) == "NO_DATA"
    assert check_espresso_machine([[94, 97, 95], [96]]) == "OPTIMAL"


def test_espresso_monitor_shuts_down_after_two_consecutive_hot_readings():
    assert check_espresso_machine([[97, 97]]) == "SHUTDOWN"
