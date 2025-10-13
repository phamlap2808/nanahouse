from typing import Optional, List
from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
import uuid
from core.services.notify import send_email, send_sms
from .io import (
    OrderCreateInput,
    OrderUpdateInput,
    OrderOutput,
    OrderListInput,
    PaymentCreateInput,
    PaymentUpdateInput,
    PaymentOutput
)

prisma = Prisma()


class OrderController:
    async def public_create_order(self, guest_token: str, data: OrderCreateInput) -> OrderOutput:
        """Create order from guest cart"""
        # find guest cart
        cart = await prisma.cart.find_unique(where={"guestToken": guest_token}, include={"items": {"include": {"product": True}}})
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Validate products and calculate totals (similar to create_order)
        subtotal = 0
        order_items_data = []
        for cart_item in cart.items:
            product = cart_item.product
            if product.status != "active":
                raise HTTPException(status_code=400, detail=f"Product '{product.name}' is no longer available")
            if product.trackStock and product.stock < cart_item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product '{product.name}'")
            item_total = cart_item.quantity * product.price
            subtotal += item_total
            order_items_data.append({
                "productId": product.id,
                "quantity": cart_item.quantity,
                "price": product.price,
                "name": product.name,
                "sku": product.sku
            })

        tax = subtotal * 0.1
        shipping = 50000 if subtotal < 500000 else 0
        total = subtotal + tax + shipping - data.discount

        # Generate order number
        import uuid
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Create order without userId (guest)
        order = await prisma.order.create(
            data={
                "orderNumber": order_number,
                "userId": 0,
                "subtotal": subtotal,
                "tax": tax,
                "shipping": shipping,
                "discount": data.discount,
                "total": total,
                "shippingName": data.shipping_name,
                "shippingPhone": data.shipping_phone,
                "shippingAddress": data.shipping_address,
                "shippingCity": data.shipping_city,
                "shippingState": data.shipping_state,
                "shippingZip": data.shipping_zip,
                "shippingCountry": data.shipping_country,
                "notes": data.notes,
                "items": {"create": order_items_data}
            },
            include={"items": True, "payments": True}
        )

        # Decrement stocks
        for cart_item in cart.items:
            if cart_item.product.trackStock:
                await prisma.product.update(where={"id": cart_item.product.id}, data={"stock": {"decrement": cart_item.quantity}})

        # Clear guest cart
        await prisma.cartitem.delete_many(where={"cartId": cart.id})

        return OrderOutput.from_prisma(order)
    async def create_order(self, data: OrderCreateInput, email: str = Depends(verify_auth)) -> OrderOutput:
        """Create order from cart"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's cart with items
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}}
        )
        
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Validate products and calculate totals
        subtotal = 0
        order_items_data = []
        
        for cart_item in cart.items:
            product = cart_item.product
            
            # Check if product is still active
            if product.status != "active":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Product '{product.name}' is no longer available"
                )
            
            # Check stock
            if product.trackStock and product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product '{product.name}'"
                )
            
            item_total = cart_item.quantity * product.price
            subtotal += item_total
            
            order_items_data.append({
                "productId": product.id,
                "quantity": cart_item.quantity,
                "price": product.price,
                "name": product.name,
                "sku": product.sku
            })

        # Calculate totals
        tax = subtotal * 0.1  # 10% tax
        shipping = 50000 if subtotal < 500000 else 0  # Free shipping over 500k
        total = subtotal + tax + shipping - data.discount

        # Generate order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Create order
        order = await prisma.order.create(
            data={
                "orderNumber": order_number,
                "userId": user.id,
                "subtotal": subtotal,
                "tax": tax,
                "shipping": shipping,
                "discount": data.discount,
                "total": total,
                "shippingName": data.shipping_name,
                "shippingPhone": data.shipping_phone,
                "shippingAddress": data.shipping_address,
                "shippingCity": data.shipping_city,
                "shippingState": data.shipping_state,
                "shippingZip": data.shipping_zip,
                "shippingCountry": data.shipping_country,
                "notes": data.notes,
                "items": {
                    "create": order_items_data
                }
            },
            include={"items": True, "payments": True}
        )

        # Notify user via email (order created)
        if user.email:
            send_email(
                to_email=user.email,
                subject=f"Đơn hàng {order_number} đã được tạo",
                html_body=f"<p>Cảm ơn bạn đã đặt hàng. Mã đơn: {order_number}</p>"
            )

        # Update product stock
        for cart_item in cart.items:
            if cart_item.product.trackStock:
                await prisma.product.update(
                    where={"id": cart_item.product.id},
                    data={"stock": {"decrement": cart_item.quantity}}
                )

        # Clear cart
        await prisma.cartitem.delete_many(where={"cartId": cart.id})

        return OrderOutput.from_prisma(order)

    async def get_order(self, order_id: int, email: str = Depends(verify_auth)) -> OrderOutput:
        """Get order by ID"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get order
        order = await prisma.order.find_first(
            where={
                "id": order_id,
                "userId": user.id
            },
            include={"items": True, "payments": True}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return OrderOutput.from_prisma(order)

    async def get_order_by_number(self, order_number: str, email: str = Depends(verify_auth)) -> OrderOutput:
        """Get order by order number"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get order
        order = await prisma.order.find_first(
            where={
                "orderNumber": order_number,
                "userId": user.id
            },
            include={"items": True, "payments": True}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return OrderOutput.from_prisma(order)

    async def list_orders(self, params: OrderListInput, email: str = Depends(verify_auth)) -> dict:
        """List user's orders"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build where clause
        where_clause = {"userId": user.id}
        if params.status:
            where_clause["status"] = params.status

        # Get orders
        skip = (params.page - 1) * params.limit
        orders = await prisma.order.find_many(
            where=where_clause,
            include={"items": True, "payments": True},
            order={"createdAt": "desc"},
            skip=skip,
            take=params.limit
        )

        total = await prisma.order.count(where=where_clause)

        return {
            "orders": [OrderOutput.from_prisma(order) for order in orders],
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "pages": (total + params.limit - 1) // params.limit
        }

    async def update_order(self, order_id: int, data: OrderUpdateInput, email: str = Depends(verify_auth)) -> OrderOutput:
        """Update order"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get order
        order = await prisma.order.find_first(
            where={
                "id": order_id,
                "userId": user.id
            }
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update order
        update_data = {}
        if data.status is not None:
            update_data["status"] = data.status
        if data.shipping_name is not None:
            update_data["shippingName"] = data.shipping_name
        if data.shipping_phone is not None:
            update_data["shippingPhone"] = data.shipping_phone
        if data.shipping_address is not None:
            update_data["shippingAddress"] = data.shipping_address
        if data.shipping_city is not None:
            update_data["shippingCity"] = data.shipping_city
        if data.shipping_state is not None:
            update_data["shippingState"] = data.shipping_state
        if data.shipping_zip is not None:
            update_data["shippingZip"] = data.shipping_zip
        if data.shipping_country is not None:
            update_data["shippingCountry"] = data.shipping_country
        if data.notes is not None:
            update_data["notes"] = data.notes

        updated_order = await prisma.order.update(
            where={"id": order_id},
            data=update_data,
            include={"items": True, "payments": True}
        )

        # Notifications on status/shipping updates
        if "status" in update_data:
            try:
                if user.email:
                    send_email(
                        to_email=user.email,
                        subject=f"Cập nhật trạng thái đơn {order.orderNumber}",
                        html_body=f"<p>Trạng thái mới: {update_data['status']}</p>"
                    )
                if updated_order.shippingPhone:
                    send_sms(updated_order.shippingPhone, f"Don {order.orderNumber}: {update_data['status']}")
            except Exception:
                pass

        return OrderOutput.from_prisma(updated_order)

    async def cancel_order(self, order_id: int, email: str = Depends(verify_auth)) -> OrderOutput:
        """Cancel order"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get order
        order = await prisma.order.find_first(
            where={
                "id": order_id,
                "userId": user.id
            },
            include={"items": True}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status in ["delivered", "cancelled"]:
            raise HTTPException(status_code=400, detail="Cannot cancel this order")

        # Update order status
        updated_order = await prisma.order.update(
            where={"id": order_id},
            data={"status": "cancelled"},
            include={"items": True, "payments": True}
        )

        # Restore stock
        for item in order.items:
            await prisma.product.update(
                where={"id": item.productId},
                data={"stock": {"increment": item.quantity}}
            )

        return OrderOutput.from_prisma(updated_order)

    # Payment methods
    async def create_payment(self, order_id: int, data: PaymentCreateInput, email: str = Depends(verify_auth)) -> PaymentOutput:
        """Create payment for order"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get order
        order = await prisma.order.find_first(
            where={
                "id": order_id,
                "userId": user.id
            }
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail="Cannot pay for cancelled order")

        # Create payment
        payment = await prisma.payment.create(
            data={
                "orderId": order_id,
                "amount": data.amount,
                "method": data.method,
                "gateway": data.gateway,
                "transactionId": data.transaction_id
            }
        )

        return PaymentOutput.from_prisma(payment)

    async def update_payment(self, payment_id: int, data: PaymentUpdateInput, email: str = Depends(verify_auth)) -> PaymentOutput:
        """Update payment status"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get payment
        payment = await prisma.payment.find_first(
            where={
                "id": payment_id,
                "order": {"userId": user.id}
            }
        )
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Update payment
        update_data = {"status": data.status}
        if data.transaction_id is not None:
            update_data["transactionId"] = data.transaction_id
        if data.gateway_data is not None:
            update_data["gatewayData"] = data.gateway_data
        
        if data.status == "completed":
            from datetime import datetime, timezone
            update_data["paidAt"] = datetime.now(timezone.utc)

        updated_payment = await prisma.payment.update(
            where={"id": payment_id},
            data=update_data
        )

        # Update order status if payment completed
        if data.status == "completed":
            await prisma.order.update(
                where={"id": payment.orderId},
                data={"status": "confirmed"}
            )
            # Notify payment completed
            try:
                if user.email:
                    send_email(
                        to_email=user.email,
                        subject=f"Thanh toán đơn {order.orderNumber} thành công",
                        html_body=f"<p>Đơn {order.orderNumber} đã được xác nhận thanh toán.</p>"
                    )
                ord_full = await prisma.order.find_unique(where={"id": payment.orderId})
                if ord_full and ord_full.shippingPhone:
                    send_sms(ord_full.shippingPhone, f"Don {ord_full.orderNumber} da thanh toan thanh cong")
            except Exception:
                pass

        return PaymentOutput.from_prisma(updated_payment)
