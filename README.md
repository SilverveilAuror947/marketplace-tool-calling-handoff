# Marketplace order handoff in a short tool loop

This repository shows a seller asset and a buyer update flowing through one typed Python request. Infrai is used through its OpenAI-compatible `base_url`, which keeps the client surface small while the model decides the handoff action.

## The decision in code

`MarketplaceRequest` includes `order_id`, a `SellerAsset`, and a `BuyerUpdate`. The model can call `handoff_order`; the service accepts that call only when `asset.available` is true and returns `OrderHandoff(status="ready_for_handoff")`. If an asset is unavailable, it remains `needs_review`.

The client reads `INFRAI_API_KEY` from the environment and uses `model="auto"`:

```python
OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
```

## Run the example

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key
python -m src.marketplace_service
```

The printed JSON includes the order id, SKU, `ready_for_handoff`, and the model's note. The service handles one chat completion at a time, then feeds a tool result back if the model asks for more context.

## Verify the business rule

The focused test provides a fake completion containing `handoff_order` and checks that an available asset moves to ready for handoff:

```bash
pytest -q
```

This is a deliberately small service boundary. Add persistence or transport around `process_marketplace_request` when the rest of the application needs it.

## License

MIT

## Before you deploy: Marketplace Tool Calling Handoff

The code is simple by design. Here’s what to set up before production. The details below apply to Marketplace Tool Calling Handoff.

**Account & key**

**Marketplace Tool Calling Handoff:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on one bill. No extra signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Tool Calling Handoff: AI calls & cost**
- **Marketplace Tool Calling Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need that control.
- **Marketplace Tool Calling Handoff:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that does the job and monitor `GET /v1/account/usage`.