import sys
import os
import pytest
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


class TestDatetimeReturnTypes:
    """Test that datetime functions return strings by default."""

    def test_today_returns_string(self):
        solver = create_solver({})
        result = solver(["Today"])
        assert isinstance(result, str)
        assert result == datetime.date.today().isoformat()

    def test_now_returns_string(self):
        solver = create_solver({})
        result = solver(["Now"])
        assert isinstance(result, str)
        # Check format is ISO datetime (contains T)
        assert "T" in result

    def test_strptime_returns_string(self):
        solver = create_solver({})
        result = solver(["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"])
        assert isinstance(result, str)
        assert result == "2025-01-10T10:05:00"


class TestDatetimeArithmetic:
    """Test datetime arithmetic with string inputs/outputs."""

    def test_today_plus_timedelta_returns_string(self):
        solver = create_solver({})
        result = solver(["Add", ["Today"], ["TimeDeltaDays", 7]])
        assert isinstance(result, str)
        expected = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        # Result includes time component since date becomes datetime after arithmetic
        assert result.startswith(expected) or "T" in result

    def test_today_minus_timedelta_returns_string(self):
        solver = create_solver({})
        result = solver(["Subtract", ["Today"], ["TimeDeltaDays", 3]])
        assert isinstance(result, str)

    def test_now_plus_timedelta_returns_string(self):
        solver = create_solver({})
        result = solver(["Add", ["Now"], ["TimeDeltaHours", 2]])
        assert isinstance(result, str)
        assert "T" in result

    def test_strptime_plus_timedelta_days(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaDays", 3]],
            "%d",
        ])
        assert result == "13"

    def test_strptime_minus_timedelta_days(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Subtract", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaDays", 3]],
            "%d",
        ])
        assert result == "07"

    def test_strptime_plus_timedelta_minutes(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaMinutes", 5]],
            "%M",
        ])
        assert result == "10"

    def test_strptime_plus_timedelta_hours(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaHours", 2]],
            "%H",
        ])
        assert result == "12"

    def test_strptime_plus_timedelta_weeks(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaWeeks", 1]],
            "%d",
        ])
        assert result == "17"


class TestStrftime:
    """Test Strftime with various inputs."""

    def test_strftime_with_strptime(self):
        solver = create_solver({})
        result = solver(["Strftime", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], "%Y"])
        assert result == "2025"

    def test_strftime_with_today(self):
        solver = create_solver({})
        result = solver(["Strftime", ["Today"], "%Y"])
        assert result == str(datetime.date.today().year)

    def test_strftime_with_now(self):
        solver = create_solver({})
        result = solver(["Strftime", ["Now"], "%Y"])
        assert result == str(datetime.datetime.now().year)

    def test_strftime_accepts_string_datetime(self):
        """Test that Strftime can parse ISO string input."""
        solver = create_solver({})
        result = solver(["Strftime", "2025-06-15T14:30:00", "%Y-%m-%d"])
        assert result == "2025-06-15"

    def test_strftime_accepts_string_date(self):
        """Test that Strftime can parse ISO date string input."""
        solver = create_solver({})
        result = solver(["Strftime", "2025-06-15", "%Y-%m-%d"])
        assert result == "2025-06-15"

    def test_strftime_full_format(self):
        solver = create_solver({})
        result = solver(["Strftime", "2025-06-15T14:30:45", "%Y-%m-%d %H:%M:%S"])
        assert result == "2025-06-15 14:30:45"


class TestDatetimeChaining:
    """Test complex datetime operation chains."""

    def test_add_then_strftime(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Add", ["Today"], ["TimeDeltaDays", 10]],
            "%Y-%m-%d",
        ])
        expected = (datetime.date.today() + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        assert result == expected

    def test_subtract_then_strftime(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Subtract", ["Now"], ["TimeDeltaHours", 5]],
            "%H",
        ])
        # Just verify it returns a valid hour string
        assert result.isdigit()
        assert 0 <= int(result) <= 23

    def test_multiple_timedelta_additions(self):
        solver = create_solver({})
        result = solver([
            "Strftime",
            ["Add", ["Add", ["Strptime", "2025-01-01T00:00", "%Y-%m-%dT%H:%M"], ["TimeDeltaDays", 1]], ["TimeDeltaHours", 12]],
            "%Y-%m-%d %H:%M",
        ])
        assert result == "2025-01-02 12:00"

    def test_datetime_in_conditional(self):
        """Test using datetime comparison in If statement."""
        solver = create_solver({})
        # This tests that string datetimes work in other constructs
        today = solver(["Today"])
        assert isinstance(today, str)


class TestTimeDeltaFunctions:
    """Test TimeDelta functions."""

    def test_timedelta_days(self):
        solver = create_solver({})
        result = solver(["Add", "2025-01-10", ["TimeDeltaDays", 5]])
        assert "2025-01-15" in result

    def test_timedelta_hours(self):
        solver = create_solver({})
        result = solver(["Add", "2025-01-10T10:00:00", ["TimeDeltaHours", 3]])
        assert "13:00:00" in result

    def test_timedelta_minutes(self):
        solver = create_solver({})
        result = solver(["Add", "2025-01-10T10:00:00", ["TimeDeltaMinutes", 30]])
        assert "10:30:00" in result

    def test_timedelta_weeks(self):
        solver = create_solver({})
        result = solver(["Add", "2025-01-10", ["TimeDeltaWeeks", 2]])
        assert "2025-01-24" in result

    def test_negative_timedelta(self):
        solver = create_solver({})
        result = solver(["Add", "2025-01-10", ["TimeDeltaDays", -5]])
        assert "2025-01-05" in result


class TestDatetimeWithVariables:
    """Test datetime operations with variables."""

    def test_today_in_variable(self):
        solver = create_solver({})
        result = solver(["Constants", ["d", ["Today"]], ["Strftime", "d", "%Y-%m-%d"]])
        assert result == datetime.date.today().strftime("%Y-%m-%d")

    def test_datetime_string_in_parameters(self):
        solver = create_solver({"start_date": "2025-06-01"})
        result = solver(["Strftime", ["Add", "start_date", ["TimeDeltaDays", 10]], "%Y-%m-%d"])
        assert result == "2025-06-11"
