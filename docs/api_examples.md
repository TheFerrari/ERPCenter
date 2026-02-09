# API Examples

> All examples assume `BASE_URL=http://localhost:8000` and a valid `ACCESS_TOKEN`.

## Login
```bash
curl -s -X POST "$BASE_URL/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"ChangeMe123!"}'
```

## Refresh token
```bash
curl -s -X POST "$BASE_URL/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN"}'
```

## Create a branch
```bash
curl -s -X POST "$BASE_URL/v1/branches" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"East","location":"NY","timezone":"America/New_York"}'
```

## Create an item
```bash
curl -s -X POST "$BASE_URL/v1/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sku":"SKU-200","name":"Motor","description":"Industrial motor","unit":"each","min_stock_level":2}'
```

## Adjust stock (Manager/Admin)
```bash
curl -s -X PATCH "$BASE_URL/v1/stock" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch_id":1,"item_id":1,"quantity":10}'
```

## Create and fulfill an order
```bash
curl -s -X POST "$BASE_URL/v1/orders" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch_id":1}'

curl -s -X POST "$BASE_URL/v1/orders/1/lines" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"item_id":1,"requested_qty":3}'

curl -s -X POST "$BASE_URL/v1/orders/1/submit" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

curl -s -X POST "$BASE_URL/v1/orders/1/fulfill" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```
