# ShortenedURL


## sample code

### fastapiの起動

```bash
uvicorn main:app --reload
```

### Powershell

```ps1
Invoke-RestMethod -Uri "http://localhost:8000/shorten" `
  -Method Post `
  -Body '{"url": "https://example.com"}' `
  -ContentType "application/json"
```

### Linux

```bash
curl -X POST http://localhost:8000/shorten \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```