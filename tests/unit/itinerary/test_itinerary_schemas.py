from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.itinerary import ItineraryConditionsRequest


def _valid_payload(**overrides):
    payload = {
        "start_date": date(2026, 8, 10),
        "end_date": date(2026, 8, 13),
        "region": "제주도",
        "arrival_time": "LUNCH",
        "departure_time": "MORNING",
    }
    payload.update(overrides)
    return payload


class TestItineraryConditionsRequest:
    def test_valid_request_with_required_fields_only(self):
        req = ItineraryConditionsRequest(**_valid_payload())

        assert req.transportation is None
        assert req.purpose is None
        assert req.styles == []

    def test_valid_request_with_all_fields(self):
        req = ItineraryConditionsRequest(
            **_valid_payload(
                transportation="CAR",
                purpose="FAMILY",
                styles=["NATURE", "FOOD"],
            )
        )

        assert req.transportation == "CAR"
        assert req.purpose == "FAMILY"
        assert req.styles == ["NATURE", "FOOD"]

    def test_end_date_before_start_date_rejected(self):
        with pytest.raises(ValidationError):
            ItineraryConditionsRequest(
                **_valid_payload(
                    start_date=date(2026, 8, 13), end_date=date(2026, 8, 10)
                )
            )

    def test_trip_longer_than_14_days_rejected(self):
        with pytest.raises(ValidationError):
            ItineraryConditionsRequest(
                **_valid_payload(
                    start_date=date(2026, 8, 1), end_date=date(2026, 8, 20)
                )
            )

    def test_trip_of_exactly_14_days_accepted(self):
        req = ItineraryConditionsRequest(
            **_valid_payload(start_date=date(2026, 8, 1), end_date=date(2026, 8, 14))
        )

        assert req.start_date == date(2026, 8, 1)

    def test_same_day_arrival_after_departure_rejected(self):
        with pytest.raises(ValidationError):
            ItineraryConditionsRequest(
                **_valid_payload(
                    start_date=date(2026, 8, 10),
                    end_date=date(2026, 8, 10),
                    arrival_time="EVENING",
                    departure_time="MORNING",
                )
            )

    def test_same_day_arrival_before_departure_accepted(self):
        req = ItineraryConditionsRequest(
            **_valid_payload(
                start_date=date(2026, 8, 10),
                end_date=date(2026, 8, 10),
                arrival_time="MORNING",
                departure_time="EVENING",
            )
        )

        assert req.start_date == req.end_date

    def test_invalid_style_rejected(self):
        with pytest.raises(ValidationError):
            ItineraryConditionsRequest(**_valid_payload(styles=["UNKNOWN"]))

    def test_missing_required_field_rejected(self):
        payload = _valid_payload()
        del payload["region"]

        with pytest.raises(ValidationError):
            ItineraryConditionsRequest(**payload)
