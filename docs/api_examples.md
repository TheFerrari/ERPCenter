# API Examples

## Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

## List items
```bash
curl http://localhost:8001/items \
  -H 'Authorization: Bearer <TOKEN>'
```

## Create order
```bash
curl -X POST http://localhost:8001/orders \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"status":"draft"}'
```

## Fulfill order
```bash
curl -X POST http://localhost:8001/orders/1/fulfill \
  -H 'Authorization: Bearer <TOKEN>'
```

