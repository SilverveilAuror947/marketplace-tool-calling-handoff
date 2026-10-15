from types import SimpleNamespace

from src.marketplace_service import MarketplaceRequest, SellerAsset, BuyerUpdate, process_marketplace_request


def test_available_asset_becomes_handoff():
    call = SimpleNamespace(id="c1", function=SimpleNamespace(name="handoff_order", arguments='{"order_id":"o1","sku":"s1","note":"packed"}'))
    message = SimpleNamespace(tool_calls=[call], content=None)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **_: SimpleNamespace(choices=[SimpleNamespace(message=message)]))))
    request = MarketplaceRequest(order_id="o1", asset=SellerAsset(sku="s1", title="Cup"), buyer=BuyerUpdate(buyer_id="b1", message="Ready"))
    result = process_marketplace_request(request, client)
    assert result.status == "ready_for_handoff"
    assert result.order_id == "o1"
