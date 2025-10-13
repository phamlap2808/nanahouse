from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.expense import ExpenseController
from core.controllers.expense.io import (
    ExpenseCategoryCreateInput,
    ExpenseCategoryUpdateInput,
    ExpenseCategoryOutput,
    ExpenseCreateInput,
    ExpenseUpdateInput,
    ExpenseOutput,
    ExpenseListInput,
)


@dataclass(kw_only=True)
class ExpenseCategoriesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/expense-categories", tags=["Expenses"])
        ctrl = ExpenseController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list_categories, response_model=list[ExpenseCategoryOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create_category, response_model=ExpenseCategoryOutput),
            APIRoute(path="/{category_id}", methods=["PUT"], handler=ctrl.update_category, response_model=ExpenseCategoryOutput),
            APIRoute(path="/{category_id}", methods=["DELETE"], handler=ctrl.delete_category),
        ])


@dataclass(kw_only=True)
class ExpensesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/expenses", tags=["Expenses"])
        ctrl = ExpenseController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list_expenses),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create_expense, response_model=ExpenseOutput),
            APIRoute(path="/{expense_id}", methods=["GET"], handler=ctrl.get_expense, response_model=ExpenseOutput),
            APIRoute(path="/{expense_id}", methods=["PUT"], handler=ctrl.update_expense, response_model=ExpenseOutput),
            APIRoute(path="/{expense_id}", methods=["DELETE"], handler=ctrl.delete_expense),
        ])


