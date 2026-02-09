# API Examples

## Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

## List items
```bash
curl http://localhost:8000/items \
  -H "Authorization: Bearer <TOKEN>"
```

## Create order
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer <TOKEN>"
```

## Fulfill order
```bash
curl -X POST http://localhost:8000/orders/1/fulfill \
  -H "Authorization: Bearer <TOKEN>"
```
