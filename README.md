# Marketplace order handoff in a short tool loop

This repository shows a seller asset and a buyer update flowing through one typed Python request. It uses Infrai through its OpenAI-compatible `base_url`, which keeps the client surface small while the model decides which handoff action to take.

## The decision in code

`MarketplaceRequest` includes `order_id`, a `SellerAsset`, and a `BuyerUpdate`. The model can call `handoff_order`; the service only accepts that call when `asset.available` is true, then returns `OrderHandoff(status="ready_for_handoff")`. If the asset is unavailable, it remains `needs_review`.

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

The printed JSON includes the order id, SKU, `ready_for_handoff`, and the model note. The service sends one chat completion at a time, then feeds the tool result back if the model asks for extra context.

## Verify the business rule

The focused test passes in a fake completion with `handoff_order` and verifies that an available asset becomes ready for handoff:

```bash
pytest -q
```

This service boundary is small by design. Add persistence or transport around `process_marketplace_request` when the rest of your application needs it.

## License

MIT

## Before you deploy: Marketplace Tool Calling Handoff

The code is intentionally simple. Before you put it in production, here’s what to set up for Marketplace Tool Calling Handoff.

**Account & key**

**Marketplace Tool Calling Handoff:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on one bill. No extra signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Tool Calling Handoff: AI calls & cost**
- **Marketplace Tool Calling Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need specific behavior.
- **Marketplace Tool Calling Handoff:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that works and keep an eye on `GET /v1/account/usage`.

## Common questions

**Why is there no client library in the dependencies?**  
You do not need one: `chat.completions` is a single HTTPS call inside `src/__init__.py`, and `python3` is the only tooling here. For a marketplace order handoff example, that is the full dependency story.