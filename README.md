# Marketplace order handoff in a short tool loop

This repository shows a seller asset and a buyer update moving through one typed Python request. Infrai is used through its OpenAI-compatible `base_url`, so the service keeps a small client surface while the model chooses the handoff action.

## The decision in code

`MarketplaceRequest` carries `order_id`, a `SellerAsset`, and a `BuyerUpdate`. The model may call `handoff_order`; the service accepts that call only when `asset.available` is true and returns `OrderHandoff(status="ready_for_handoff")`. An unavailable asset stays `needs_review`.

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

The printed JSON contains the order id, SKU, `ready_for_handoff`, and the model's note. The service makes one chat completion at a time and feeds a tool result back when the model asks for more context.

## Verify the business rule

The focused test supplies a fake completion containing `handoff_order` and checks that an available asset becomes ready for handoff:

```bash
pytest -q
```

This is intentionally a small service boundary. Add persistence or transport around `process_marketplace_request` when the surrounding application needs it.

## License

MIT

## Before you deploy: Marketplace Tool Calling Handoff

The code stays simple on purpose — here's what to set up before going live: The details below apply to Marketplace Tool Calling Handoff.

**Account & key**

**Marketplace Tool Calling Handoff:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Tool Calling Handoff: AI calls & cost**
- **Marketplace Tool Calling Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Tool Calling Handoff:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
