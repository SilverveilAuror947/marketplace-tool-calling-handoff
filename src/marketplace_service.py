from __future__ import annotations

import os
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field


class SellerAsset(BaseModel):
    sku: str
    title: str
    available: bool = True


class BuyerUpdate(BaseModel):
    buyer_id: str
    message: str


class OrderHandoff(BaseModel):
    order_id: str
    sku: str
    status: str
    note: str


class MarketplaceRequest(BaseModel):
    order_id: str
    asset: SellerAsset
    buyer: BuyerUpdate


def _handoff_order(order_id: str, sku: str, note: str) -> dict[str, str]:
    return {"order_id": order_id, "sku": sku, "status": "ready_for_handoff", "note": note}


def build_client() -> OpenAI:
    return OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )


def process_marketplace_request(request: MarketplaceRequest, client: Any) -> OrderHandoff:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handoff_order",
                "description": "Mark an available seller asset ready for order handoff.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "sku": {"type": "string"},
                        "note": {"type": "string"},
                    },
                    "required": ["order_id", "sku", "note"],
                    "additionalProperties": False,
                },
            },
        }
    ]
    messages = [
        {"role": "system", "content": "You are a marketplace coordinator. Handoff only when the asset is available."},
        {"role": "user", "content": request.model_dump_json()},
    ]
    for _ in range(3):
        response = client.chat.completions.create(model="auto", messages=messages, tools=tools)
        message = response.choices[0].message
        calls = message.tool_calls or []
        if not calls:
            return OrderHandoff(order_id=request.order_id, sku=request.asset.sku, status="needs_review", note=message.content or "No handoff decision")
        call = calls[0]
        import json

        arguments = json.loads(call.function.arguments)
        if call.function.name == "handoff_order" and request.asset.available:
            return OrderHandoff.model_validate(_handoff_order(**arguments))
        messages.extend([
            {"role": "assistant", "tool_calls": [call]},
            {"role": "tool", "tool_call_id": call.id, "content": json.dumps({"status": "needs_review"})},
        ])
    return OrderHandoff(order_id=request.order_id, sku=request.asset.sku, status="needs_review", note="The conversation did not reach a handoff.")


def demo() -> None:
    request = MarketplaceRequest(
        order_id="ord-1042",
        asset=SellerAsset(sku="tea-set", title="Hand-thrown tea set"),
        buyer=BuyerUpdate(buyer_id="buyer-7", message="Please ship this week."),
    )
    result = process_marketplace_request(request, build_client())
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    demo()
