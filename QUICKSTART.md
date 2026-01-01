# Quick Start Guide

## 5-Minute Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Database
```bash
docker-compose up -d
```

Wait a few seconds for the database to fully start.

### 3. Set Environment Variables
```bash
cp .env.example .env
```

Edit the `.env` file, at minimum set:
- `DATABASE_URL` (default configured, usually no need to modify)
- `NEXT_PUBLIC_MAPBOX_TOKEN` (Required! Get free token from https://www.mapbox.com/)

### 4. Initialize Database
```bash
npm run db:generate
npm run db:push
npm run db:seed
```

### 5. Start Development Server
```bash
npm run dev
```

Visit http://localhost:3000

## Common Issues

### Where to Get Mapbox Token?
1. Visit https://www.mapbox.com/
2. Register for a free account
3. Find "Access token" in Dashboard
4. Copy token to `NEXT_PUBLIC_MAPBOX_TOKEN` in `.env` file

### Database Connection Failed?
Make sure Docker container is running:
```bash
docker-compose ps
```

If container is not running, start it:
```bash
docker-compose up -d
```

### Port Already in Use?
If port 5432 is occupied, modify the port mapping in `docker-compose.yml`.

### Reset Database?
```bash
docker-compose down -v
docker-compose up -d
npm run db:push
npm run db:seed
```

## Next Steps

- Check `README.md` for complete documentation
- Explore code structure
- Customize coffee shop data (edit `prisma/seed.ts`)
