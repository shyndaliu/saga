# Saga Orchestration with FastAPI

This repository implements a Saga pattern for distributed transactions using FastAPI. The orchestration type was chosen, meaning everything is controlled by a central orchestrator (`SagaOrchestrator`), which creates and executes steps sequentially. Each step represents an independent operation with its own `do()` and `compensate()` methods to handle failures.

## Source Code

GitHub Repository: [saga](https://github.com/shyndaliu/saga)

## Overview

The implementation consists of:
- **Saga Orchestrator** (`SagaOrchestrator`): Controls and manages the execution of transaction steps.
- **Step Base Class** (`Step`): Defines the structure for steps, including `do()` and `compensate()` methods.
- **Step Implementations**:
  - `Payment`: Handles user payment and ensures sufficient balance.
  - `Inventory`: Checks and updates stock availability.
  - `Shipping`: Validates the shipping address and simulates order shipment.
- **Database Simulation**: Simple Python dictionaries simulate user balances, inventory, and orders.

## Transaction Flow

1. `Payment` step deducts the required amount from the user's balance.
2. `Inventory` step verifies and deducts items from stock.
3. `Shipping` step ensures a valid shipping address and finalizes the order.
4. If any step fails, a rollback is triggered via `compensate()` to revert the previous steps.

## API Endpoint

### Checkout Order

- **URL:** `/checkout/{order_id}`
- **Method:** `POST`
- **Description:** Executes the saga transaction for the given order ID.
- **Example Request:**
  ```sh
  curl -X POST "http://127.0.0.1:8000/checkout/order1"
  ```
- **Responses:**
  - `200 OK`: Order completed successfully.
  - `400 Bad Request`: Transaction failed, with appropriate error details.

## Error Handling

- If a step fails, `compensate()` is called on all previously executed steps in reverse order.
- Compensation logs are printed to indicate rollback operations.

## Running the Application

1. Clone the repository:
   ```sh
   git clone https://github.com/shyndaliu/saga.git
   cd saga
   ```
2. Install dependencies:
   ```sh
   pip install fastapi uvicorn
   ```
3. Start the server:
   ```sh
   uvicorn main:app --reload
   ```
4. Test the API using cURL or Postman.



