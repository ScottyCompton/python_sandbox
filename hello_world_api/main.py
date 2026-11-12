from fastapi import FastAPI, HTTPException, Query
import json
import os
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
import uuid
from urllib.parse import unquote
from typing import Annotated
import re

DATA_FILEPATH = str(Path(__file__).parent / "customers.json")

class CustomerCreatePayload(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip: str
    email: str
    phone: str
    hobbies: list[str]


class Customer(CustomerCreatePayload):
    id: str



class CustomerUpdatePayload(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    email: str | None = None
    phone: str | None = None
    hobbies: list[str] | None = None

@dataclass
class AppData:
    customers: list[Customer]

app = FastAPI()

with open(DATA_FILEPATH, "r", encoding="utf-8") as file:
    raw = json.load(file)
    app_data = AppData(customers=[Customer(**row) for row in raw["customers"]])


def save_data() -> None:
    """
    Saves the data after performing some operation to it
    """
    temp_filepath = f"{DATA_FILEPATH}.tmp"
    payload = {"customers": [c.model_dump() for c in app_data.customers]}
    with open(temp_filepath, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
    os.replace(temp_filepath, DATA_FILEPATH)

@app.get("/")
async def root():
    """
    Just shows I'm alive :->
    """
    return {"message": "Hello World!"}

@app.get("/customers/")
async def read_customers(
    name: Annotated[str | None, Query()] = None,
    email: Annotated[str | None, Query()] = None,
) -> list[Customer]:
    """
    Get all the customer records, optionally filtered by name and/or email.
    """
    customers = app_data.customers

    if name:
        needle = unquote(name).casefold()
        customers = [item for item in customers if needle in item.name.casefold()]

    if email:
        needle = unquote(email).casefold()
        customers = [item for item in customers if needle in item.email.casefold()]

    return customers


@app.get("/customers/{uuid}")
async def read_customer(uuid: str) -> Customer:
    """
    Get a single customer record
    """
    cust = next((item for item in app_data.customers if item.id == uuid), None)
    if cust is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return cust

@app.delete("/customers/{uuid}")
async def delete_customer(uuid: str) -> dict:
    """
    Delete a customer with the given uuid.  Returns deleted customer data or None if it was not found
    """
    index = next((i for i, item in enumerate(app_data.customers) if item.id == uuid), None)

    if index is None:
        raise HTTPException(status_code=404, detail=f"Customer record with id={uuid} was not found.")

    deleted_customer = app_data.customers.pop(index)
    save_data()
    return {"message": "Customer deleted", "customer": deleted_customer}

@app.put("/customers/{uuid}")
async def update_customer(uuid: str, payload: CustomerUpdatePayload) -> Customer:
    """
    Update a customer with the given uuid.  Returns updated customer data or None if it was not found
    """

    existing_customer = next((c for c in app_data.customers if c.id == uuid), None)

    if not existing_customer:
        raise HTTPException(status_code=404,  detail=f"Customer record with id={uuid} was not found.")


    updates = payload.model_dump(exclude_unset=True)
    merged_data = {**existing_customer.model_dump(), **updates}

    try:
        updated_customer = Customer.model_validate(merged_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    idx = app_data.customers.index(existing_customer)
    app_data.customers[idx] = updated_customer
    save_data()

    return updated_customer

@app.post("/customers/", status_code=201)
async def create_customer(payload: CustomerCreatePayload) -> Customer:
    """
    Create a new customer customer with the given data. 
    """

    new_uuid = f"{uuid.uuid4()}"
    cust_data = payload.model_dump(exclude_unset=True)
    new_customer = Customer(id=new_uuid, **cust_data)

    app_data.customers.append(new_customer)
    save_data()

    return new_customer



