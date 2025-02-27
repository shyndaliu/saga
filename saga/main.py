from fastapi import FastAPI, HTTPException
import asyncio

app = FastAPI()

# Simulated Databases
UsersDB = {"user1": 100, "user2": 5}
InventoryDB = {"item1": 5, "item2": 3}
OrdersDB = {
    "order1": {"user": "user1", "items": {"item1": 2}, "address": "Some Street"},
    "order2": {"user": "user2", "items": {"item2": 1}, "address": ""},
}


# Step Base Class
class Step:
    def __init__(self, prev_step=None):
        self.prev_step = prev_step

    async def do(self, order_id: str):
        raise NotImplementedError

    async def compensate(self, order_id: str):
        if self.prev_step:
            await self.prev_step.compensate(order_id)
        raise NotImplementedError


# Step Implementations
class Payment(Step):
    async def do(self, order_id: str):
        order = OrdersDB.get(order_id)
        user_id = order["user"]
        total_cost = sum(order["items"].values()) * 10

        if UsersDB[user_id] < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        UsersDB[user_id] -= total_cost
        return total_cost

    async def compensate(self, order_id: str):
        order = OrdersDB.get(order_id)
        user_id = order["user"]
        refund_amount = sum(order["items"].values()) * 10
        UsersDB[user_id] += refund_amount
        print("Compensating payment 💸")
        if self.prev_step:
            await self.prev_step.compensate(order_id)


class Inventory(Step):
    async def do(self, order_id: str):
        order = OrdersDB.get(order_id)
        for item, qty in order["items"].items():
            if InventoryDB.get(item, 0) < qty:
                raise HTTPException(status_code=400, detail="Not enough stock")

        for item, qty in order["items"].items():
            InventoryDB[item] -= qty

    async def compensate(self, order_id: str):
        order = OrdersDB.get(order_id)
        print("Compensating inventory 📥")
        for item, qty in order["items"].items():
            InventoryDB[item] += qty
        if self.prev_step:
            await self.prev_step.compensate(order_id)


class Shipping(Step):
    async def do(self, order_id: str):
        order = OrdersDB.get(order_id)
        if not order.get("address"):
            raise HTTPException(status_code=400, detail="Invalid shipping address")
        print(f"Shipping order {order_id}")
        await asyncio.sleep(1)

    async def compensate(self, order_id: str):
        print(f"Canceling shipping for order {order_id}")
        if self.prev_step:
            await self.prev_step.compensate(order_id)


# Saga Orchestrator
class SagaOrchestrator:
    async def execute_saga(self, order_id: str):
        try:
            payment = Payment()
            inventory = Inventory(prev_step=payment)
            shipping = Shipping(prev_step=inventory)

            latest_step = payment
            await payment.do(order_id)
            latest_step = inventory
            await inventory.do(order_id)
            latest_step = shipping
            await shipping.do(order_id)

            return {"message": "Order Completed"}
        except HTTPException as e:
            await latest_step.compensate(order_id)
            return {"error": str(e.detail)}


orchestrator = SagaOrchestrator()


@app.post("/checkout/{order_id}")
async def checkout(order_id: str):
    return await orchestrator.execute_saga(order_id)
