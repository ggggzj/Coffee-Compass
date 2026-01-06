# CoffeeCompass

A Yelp-like coffee shop discovery platform that helps users find the perfect coffee shop for studying, remote work, dates, or meetings.

## 🌐 Live Demo

**🔗 [Visit Live Site](https://coffee-compass-two.vercel.app)**

Deployed on Vercel: https://coffee-compass-two.vercel.app

## Features

-  **Interactive Map**: Display coffee shop locations using Mapbox GL JS
-  **Results List**: Scrollable coffee shop list on the left side
-  **Smart Filtering**: Filter by city, scene, and sort order
-  **Suitability Scoring**: Intelligent scene-based scoring system (0-100 points)
-  **Score Breakdown**: Detailed display of score calculation process
-  **Favorites**: Save favorite coffee shops using localStorage
-  **Real-time Sync**: Map and list update in real-time

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Data Fetching**: TanStack Query (React Query)
- **Backend**: Next.js Route Handlers
- **Validation**: Zod
- **Database**: PostgreSQL + Prisma ORM
- **Map**: Mapbox GL JS (react-map-gl)

## Local Development Setup

### Prerequisites

- Node.js 18+
- Docker and Docker Compose
- Mapbox access token (free registration: https://www.mapbox.com/)

### Installation Steps

1. **Clone repository and install dependencies**

```bash
cd coffeecompass
npm install
```

2. **Start PostgreSQL database**

```bash
docker-compose up -d
```

3. **Configure environment variables**

Copy `.env.example` to `.env` and fill in the necessary values:

```bash
cp .env.example .env
```

Edit the `.env` file, at minimum you need to set:

```env
DATABASE_URL="postgresql://coffeecompass:coffeecompass@localhost:5432/coffeecompass?schema=public"
NEXT_PUBLIC_MAPBOX_TOKEN="your-mapbox-token-here"
NEXTAUTH_SECRET="your-random-secret-key"
```

4. **Initialize database**

```bash
# Generate Prisma Client
npm run db:generate

# Push database schema
npm run db:push

# Seed database
npm run db:seed
```

5. **Start development server**

```bash
npm run dev
```

The app will run at http://localhost:3000

## Project Structure

```
coffeecompass/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   │   └── shops/         # Coffee shop API
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page
│   └── providers.tsx      # React Query Provider
├── components/            # React components
│   ├── FilterBar.tsx     # Filter bar
│   ├── MapPane.tsx       # Map component
│   ├── ResultsList.tsx   # Results list
│   ├── ShopCard.tsx      # Coffee shop card
│   └── ShopDrawer.tsx    # Detail drawer
├── hooks/                 # Custom Hooks
│   └── useDebounce.ts    # Debounce hook
├── lib/                   # Utility libraries
│   ├── prisma.ts         # Prisma Client
│   ├── scoring.ts        # Suitability scoring system
│   └── utils.ts          # Utility functions
└── prisma/                # Prisma configuration
    ├── schema.prisma     # Database schema
    └── seed.ts           # Seed data script
```

## Suitability Scoring System

The system calculates coffee shop suitability scores based on different usage scenarios:

- **Study**: Emphasizes quiet environment, outlets, seating, and lighting
- **Remote Work**: Emphasizes WiFi, outlets, and seating
- **Date**: Emphasizes privacy, lighting, and quiet environment
- **Meeting**: Emphasizes seating, quiet environment, and privacy

Each scenario has different weight configurations. Scores range from 0-100 and include detailed score breakdowns.

## API Endpoints

### GET /api/shops

Query coffee shop list

**Query Parameters:**
- `city`: City (Los Angeles | San Francisco | New York)
- `scene`: Scene (Study | Remote Work | Date | Meeting)
- `sort`: Sort order (Distance | Rating | Suitability)
- `bounds`: Map bounds (minLng,minLat,maxLng,maxLat)
- `page`: Page number (default: 1)
- `pageSize`: Items per page (default: 20)

### GET /api/shops/[id]

Get single coffee shop details

**Query Parameters:**
- `scene`: Scene (optional, used to calculate suitability score)

## Deploy to Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Configure environment variables (refer to `.env.example`)
4. Set up PostgreSQL database (can use Vercel Postgres or other services)
5. Run database migrations and seed data

**Note**: Make sure all necessary values are set in Vercel environment variables, including `DATABASE_URL` and `NEXT_PUBLIC_MAPBOX_TOKEN`.

## Development Commands

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run db:generate  # Generate Prisma Client
npm run db:push      # Push database schema changes
npm run db:seed      # Seed database
npm run db:studio    # Open Prisma Studio
```

## License

MIT
