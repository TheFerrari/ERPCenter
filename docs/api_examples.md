# API Examples

## Login
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"ChangeMe123!"}'
```

## List branches
```bash
curl http://localhost:8000/v1/branches \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Create order
```bash
curl -X POST http://localhost:8000/v1/orders \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"branch_id":1}'
```

## Add order line
```bash
curl -X POST http://localhost:8000/v1/orders/1/lines \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"item_id":1,"requested_qty":5}'
```

## Submit order
```bash
curl -X POST http://localhost:8000/v1/orders/1/submit \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Fulfill order
```bash
curl -X POST http://localhost:8000/v1/orders/1/fulfill \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
