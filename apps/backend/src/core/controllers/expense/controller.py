from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    ExpenseCategoryCreateInput,
    ExpenseCategoryUpdateInput,
    ExpenseCategoryOutput,
    ExpenseCreateInput,
    ExpenseUpdateInput,
    ExpenseOutput,
    ExpenseListInput,
)

prisma = Prisma()


class ExpenseController:
    # Categories
    async def create_category(self, data: ExpenseCategoryCreateInput, email: str = Depends(verify_auth)) -> ExpenseCategoryOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        cat = await prisma.expensecategory.create(
            data={
                "userId": user.id,
                "name": data.name,
                "color": data.color,
            }
        )
        return ExpenseCategoryOutput.from_prisma(cat)

    async def list_categories(self, email: str = Depends(verify_auth)) -> list[ExpenseCategoryOutput]:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        cats = await prisma.expensecategory.find_many(
            where={"userId": user.id},
            order={"createdAt": "asc"}
        )
        return [ExpenseCategoryOutput.from_prisma(c) for c in cats]

    async def update_category(self, category_id: int, data: ExpenseCategoryUpdateInput, email: str = Depends(verify_auth)) -> ExpenseCategoryOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        cat = await prisma.expensecategory.find_first(where={"id": category_id, "userId": user.id})
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.color is not None:
            update_data["color"] = data.color

        cat = await prisma.expensecategory.update(where={"id": category_id}, data=update_data)
        return ExpenseCategoryOutput.from_prisma(cat)

    async def delete_category(self, category_id: int, email: str = Depends(verify_auth)) -> dict:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        cat = await prisma.expensecategory.find_first(where={"id": category_id, "userId": user.id})
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

        await prisma.expense.delete_many(where={"categoryId": category_id, "userId": user.id})
        await prisma.expensecategory.delete(where={"id": category_id})
        return {"success": True}

    # Expenses
    async def create_expense(self, data: ExpenseCreateInput, email: str = Depends(verify_auth)) -> ExpenseOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # verify category
        cat = await prisma.expensecategory.find_first(where={"id": data.category_id, "userId": user.id})
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

        from datetime import datetime, timezone
        exp = await prisma.expense.create(
            data={
                "userId": user.id,
                "categoryId": data.category_id,
                "amount": data.amount,
                "currency": data.currency,
                "description": data.description,
                "occurredAt": data.occurred_at or datetime.now(timezone.utc),
            },
            include={"category": True}
        )
        return ExpenseOutput.from_prisma(exp)

    async def list_expenses(self, params: ExpenseListInput, email: str = Depends(verify_auth)) -> dict:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        where = {"userId": user.id}
        if params.category_id is not None:
            where["categoryId"] = params.category_id
        if params.date_from is not None or params.date_to is not None:
            date_filter = {}
            if params.date_from is not None:
                date_filter["gte"] = params.date_from
            if params.date_to is not None:
                date_filter["lte"] = params.date_to
            where["occurredAt"] = date_filter

        skip = (params.page - 1) * params.limit
        items = await prisma.expense.find_many(
            where=where,
            include={"category": True},
            order={"occurredAt": "desc"},
            skip=skip,
            take=params.limit
        )
        total = await prisma.expense.count(where=where)

        return {
            "items": [ExpenseOutput.from_prisma(i) for i in items],
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "pages": (total + params.limit - 1) // params.limit
        }

    async def get_expense(self, expense_id: int, email: str = Depends(verify_auth)) -> ExpenseOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        exp = await prisma.expense.find_first(
            where={"id": expense_id, "userId": user.id},
            include={"category": True}
        )
        if not exp:
            raise HTTPException(status_code=404, detail="Expense not found")
        return ExpenseOutput.from_prisma(exp)

    async def update_expense(self, expense_id: int, data: ExpenseUpdateInput, email: str = Depends(verify_auth)) -> ExpenseOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        exp = await prisma.expense.find_first(where={"id": expense_id, "userId": user.id})
        if not exp:
            raise HTTPException(status_code=404, detail="Expense not found")

        update_data = {}
        if data.category_id is not None:
            # verify new category belongs to user
            cat = await prisma.expensecategory.find_first(where={"id": data.category_id, "userId": user.id})
            if not cat:
                raise HTTPException(status_code=404, detail="Category not found")
            update_data["categoryId"] = data.category_id
        if data.amount is not None:
            update_data["amount"] = data.amount
        if data.currency is not None:
            update_data["currency"] = data.currency
        if data.description is not None:
            update_data["description"] = data.description
        if data.occurred_at is not None:
            update_data["occurredAt"] = data.occurred_at

        exp = await prisma.expense.update(
            where={"id": expense_id},
            data=update_data,
            include={"category": True}
        )
        return ExpenseOutput.from_prisma(exp)

    async def delete_expense(self, expense_id: int, email: str = Depends(verify_auth)) -> dict:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        exp = await prisma.expense.find_first(where={"id": expense_id, "userId": user.id})
        if not exp:
            raise HTTPException(status_code=404, detail="Expense not found")

        await prisma.expense.delete(where={"id": expense_id})
        return {"success": True}


