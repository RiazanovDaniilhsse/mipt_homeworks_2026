#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

AMOUNT_KEY: str = "amount"
DATE_KEY: str = "date"
CATEGORY_KEY: str = "category"

EXPENSE_CATEGORIES: dict[str, tuple[str, ...]] = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

DAYS_IN_MONTH: tuple[int, ...] = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

FEBRUARY: int = 2
FEBRUARY_IN_LEAP_YEAR: int = 29
MIN_MONTH: int = 1
MAX_MONTH: int = 12
MIN_DAY: int = 1
DATE_PARTS_COUNT: int = 3
INCOME_ARGS_COUNT: int = 3
COST_ARGS_COUNT: int = 4
STATS_ARGS_COUNT: int = 2
COST_CATEGORIES_ARGS_COUNT: int = 2
CATEGORY_SEPARATOR: str = "::"

EMPTY_DICT: dict[str, Any] = {}

financial_transactions_storage: list[dict[str, Any]] = []

# Type aliases
DateRecord = tuple[int, int, int]
IncomeRecord = tuple[float, DateRecord]
ExpenseRecord = tuple[str, float, DateRecord]


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY and is_leap_year(year):
        return FEBRUARY_IN_LEAP_YEAR
    return DAYS_IN_MONTH[month - 1]


def validate_date(day: int, month: int, year: int) -> bool:
    if month < MIN_MONTH or month > MAX_MONTH:
        return False
    if day < MIN_DAY or day > get_days_in_month(month, year):
        return False
    return year >= 1


def extract_date(maybe_dt: str) -> DateRecord | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None
    for part in parts:
        if not part.isdigit():
            return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if validate_date(day, month, year):
        return (day, month, year)
    return None


def parse_amount(amount_str: str) -> float | None:
    normalized = amount_str.replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None


def save_invalid_transaction() -> None:
    financial_transactions_storage.append(EMPTY_DICT)


def is_valid_category(category_name: str) -> bool:
    """Check if category exists."""
    if CATEGORY_SEPARATOR not in category_name:
        return False

    common_cat, specific_cat = category_name.split(CATEGORY_SEPARATOR, 1)
    if common_cat not in EXPENSE_CATEGORIES:
        return False

    return specific_cat in EXPENSE_CATEGORIES[common_cat]


def get_all_categories() -> list[str]:
    return [
        f"{common_cat}{CATEGORY_SEPARATOR}{subcategory}"
        for common_cat, subcategories in EXPENSE_CATEGORIES.items()
        for subcategory in subcategories
    ]


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if amount <= 0:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            AMOUNT_KEY: amount,
            DATE_KEY: parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def validate_cost_input(category_name: str, amount: float, cost_date: str) -> tuple[bool, str, DateRecord | None]:
    if not is_valid_category(category_name):
        return False, NOT_EXISTS_CATEGORY, None

    if amount <= 0:
        return False, NONPOSITIVE_VALUE_MSG, None

    parsed_date = extract_date(cost_date)
    if parsed_date is None:
        return False, INCORRECT_DATE_MSG, None

    return True, OP_SUCCESS_MSG, parsed_date


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    is_valid, error_msg, parsed_date = validate_cost_input(category_name, amount, cost_date)
    if not is_valid:
        save_invalid_transaction()
        return error_msg

    financial_transactions_storage.append(
        {
            CATEGORY_KEY: category_name,
            AMOUNT_KEY: amount,
            DATE_KEY: parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = get_all_categories()
    return "\n".join(categories)


def is_earlier(date1: DateRecord, date2: DateRecord) -> bool:
    year1, month1, day1 = date1
    year2, month2, day2 = date2
    if year1 != year2:
        return year1 < year2
    if month1 != month2:
        return month1 < month2
    return day1 <= day2


def is_same_month(date1: DateRecord, date2: DateRecord) -> bool:
    if date1[1] != date2[1]:
        return False
    return date1[2] == date2[2]


def _is_valid_transaction(transaction: dict[str, Any]) -> bool:
    """Check if transaction has required fields."""
    if not transaction:
        return False
    amount = transaction.get(AMOUNT_KEY)
    date = transaction.get(DATE_KEY)
    return amount is not None and date is not None


def _collect_income_records() -> list[IncomeRecord]:
    """Helper function to collect income records."""
    incomes: list[IncomeRecord] = []
    for transaction in financial_transactions_storage:
        if not _is_valid_transaction(transaction):
            continue

        amount = transaction[AMOUNT_KEY]
        date = transaction[DATE_KEY]
        category = transaction.get(CATEGORY_KEY)

        if category is None:
            incomes.append((amount, date))
    return incomes


def _collect_expense_records() -> list[ExpenseRecord]:
    """Helper function to collect expense records."""
    expenses: list[ExpenseRecord] = []
    for transaction in financial_transactions_storage:
        if not _is_valid_transaction(transaction):
            continue

        amount = transaction[AMOUNT_KEY]
        date = transaction[DATE_KEY]
        category = transaction.get(CATEGORY_KEY)

        if category is not None:
            expenses.append((category, amount, date))
    return expenses


def split_transactions() -> tuple[list[IncomeRecord], list[ExpenseRecord]]:
    incomes = _collect_income_records()
    expenses = _collect_expense_records()
    return incomes, expenses


def calculate_income_stats(
    target_date: DateRecord,
    incomes: list[IncomeRecord],
) -> tuple[float, float]:
    total_capital = 0.0
    month_income = 0.0

    for amount, date in incomes:
        if not is_earlier(date, target_date):
            continue
        total_capital += amount
        if is_same_month(date, target_date):
            month_income += amount

    return total_capital, month_income


def calculate_expense_stats(
    target_date: DateRecord,
    expenses: list[ExpenseRecord],
) -> tuple[float, float, dict[str, float]]:
    total_capital = 0.0
    month_expense = 0.0
    expense_by_category: dict[str, float] = {}

    for category, amount, date in expenses:
        if not is_earlier(date, target_date):
            continue
        total_capital += amount
        if is_same_month(date, target_date):
            month_expense += amount
            expense_by_category[category] = expense_by_category.get(category, 0.0) + amount

    return total_capital, month_expense, expense_by_category


def build_statistics_string(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expense: float,
    expense_by_category: dict[str, float],
) -> str:
    month_result = month_income - month_expense
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    if month_result >= 0:
        lines.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {abs(month_result):.2f} rubles.")

    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expense:.2f} rubles")
    lines.append("Details (category: amount):")

    if expense_by_category:
        sorted_categories = sorted(expense_by_category.items())
        for idx, (category, amount) in enumerate(sorted_categories, 1):
            display_name = category.split(CATEGORY_SEPARATOR)[-1]
            if amount.is_integer():
                lines.append(f"{idx}. {display_name}: {int(amount)}")
            else:
                lines.append(f"{idx}. {display_name}: {amount}")

    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    target_date = extract_date(report_date)
    if target_date is None:
        return INCORRECT_DATE_MSG

    incomes, expenses = split_transactions()

    income_capital, month_income = calculate_income_stats(target_date, incomes)
    expense_capital, month_expense, expense_by_category = calculate_expense_stats(
        target_date,
        expenses,
    )

    total_capital = income_capital - expense_capital

    return build_statistics_string(
        report_date,
        total_capital,
        month_income,
        month_expense,
        expense_by_category,
    )


def handle_income(parts: list[str]) -> None:
    if len(parts) != INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = income_handler(amount, parts[2])
    print(result)


def handle_cost_categories() -> None:
    print(cost_categories_handler())


def handle_cost_with_args(parts: list[str]) -> None:
    amount = parse_amount(parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = cost_handler(parts[1], amount, parts[3])
    print(result)


def handle_cost(parts: list[str]) -> None:
    if len(parts) == COST_CATEGORIES_ARGS_COUNT and parts[1].lower() == "categories":
        handle_cost_categories()
    elif len(parts) == COST_ARGS_COUNT:
        handle_cost_with_args(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)


def handle_stats(parts: list[str]) -> None:
    if len(parts) != STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = stats_handler(parts[1])
    print(result)


def process_command(command: str, parts: list[str]) -> None:
    """Process a single command."""
    if command == "income":
        handle_income(parts)
    elif command == "cost":
        handle_cost(parts)
    elif command == "stats":
        handle_stats(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)


def get_user_input() -> str | None:
    """Get and clean user input."""
    try:
        return input().strip()
    except EOFError:
        return None


def process_user_input(user_input: str) -> None:
    """Process a single line of user input."""
    parts = user_input.split()
    if not parts:
        return
    command = parts[0]
    process_command(command, parts)


def main() -> None:
    """Main program loop."""
    while True:
        user_input = get_user_input()
        if user_input is None:
            break
        if user_input:
            process_user_input(user_input)


if __name__ == "__main__":
    main()
