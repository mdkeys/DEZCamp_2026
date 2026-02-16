# NYC Taxi Data Ingestion - System Architecture 

**From Claude. NOT reviewed for accuracy yet.**

## System Overview Diagram

```mermaid
graph TB
    subgraph "External Data Sources"
        A1[green_tripdata_2025-11.parquet<br/>CloudFront CDN<br/>~47k rows]
        A2[taxi_zone_lookup.csv<br/>GitHub Release<br/>265 rows]
    end

    subgraph "Project Files"
        B1[docker-compose.yaml<br/>Orchestrates containers]
        B2[Dockerfile<br/>Builds ingestion image]
        B3[hw_ingest_data.py<br/>Python ingestion script]
        B4[pyproject.toml<br/>Dependencies]
    end

    subgraph "Docker Environment"
        subgraph "Docker Network: hw_wk1_default"
            C1[PostgreSQL Container<br/>postgres:18<br/>Port: 5432 internal<br/>Port: 5433 external]
            C2[pgAdmin Container<br/>pgadmin4<br/>Port: 8085]
            C3[Ingestion Container<br/>taxi-ingest:v001<br/>Temporary - auto-removes]
        end
        D1[Docker Volume:<br/>ny_taxi_postgres_data]
        D2[Docker Volume:<br/>pgadmin_data]
    end

    subgraph "User Access"
        E1[Web Browser<br/>localhost:8085]
        E2[Terminal/VS Code<br/>Docker commands]
    end

    subgraph "Database"
        F1[(PostgreSQL Database:<br/>ny_taxi)]
        F2[Table: green_tripdata<br/>46,912 rows]
        F3[Table: taxi_zones<br/>265 rows]
    end

    %% Docker Compose builds containers
    B1 -->|defines services| C1
    B1 -->|defines services| C2
    B1 -->|defines volumes| D1
    B1 -->|defines volumes| D2

    %% Dockerfile builds ingestion image
    B2 -->|builds| C3
    B4 -->|dependencies for| B2
    B3 -->|copied into| C3

    %% Data flow
    A1 -->|downloads via HTTPS| C3
    A2 -->|downloads via HTTPS| C3
    C3 -->|connects to| C1
    C3 -->|loads data into| F1

    %% Database structure
    C1 -->|hosts| F1
    F1 -->|contains| F2
    F1 -->|contains| F3

    %% Storage persistence
    C1 -.->|persists to| D1
    C2 -.->|persists to| D2

    %% User access
    E2 -->|docker compose up| B1
    E2 -->|docker build| B2
    E2 -->|docker run| C3
    E1 -->|accesses via HTTP| C2
    C2 -->|queries| C1

    %% Network connections
    C1 -.->|same network| C2
    C1 -.->|same network| C3

    style A1 fill:#e1f5ff
    style A2 fill:#e1f5ff
    style B1 fill:#fff4e1
    style B2 fill:#fff4e1
    style B3 fill:#fff4e1
    style B4 fill:#fff4e1
    style C1 fill:#e8f5e9
    style C2 fill:#e8f5e9
    style C3 fill:#ffe8e8
    style F1 fill:#f3e5f5
    style F2 fill:#f3e5f5
    style F3 fill:#f3e5f5
    style D1 fill:#fff9c4
    style D2 fill:#fff9c4
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant DockerCompose as docker-compose.yaml
    participant Dockerfile
    participant PostgreSQL as PostgreSQL Container
    participant pgAdmin as pgAdmin Container
    participant Ingest as Ingestion Container
    participant CloudFront as Data Sources
    participant DB as ny_taxi Database

    User->>DockerCompose: docker compose up -d
    DockerCompose->>PostgreSQL: Start container (port 5433:5432)
    DockerCompose->>pgAdmin: Start container (port 8085:80)
    Note over PostgreSQL,pgAdmin: Both on hw_wk1_default network
    
    User->>Dockerfile: docker build -t taxi-ingest:v001 .
    Dockerfile->>Dockerfile: Install Python 3.13 + uv
    Dockerfile->>Dockerfile: Install pandas, sqlalchemy, etc.
    Dockerfile->>Dockerfile: Copy hw_ingest_data.py
    Note over Dockerfile: Image ready: taxi-ingest:v001
    
    User->>Ingest: docker run --rm taxi-ingest:v001
    Ingest->>CloudFront: Download green_tripdata_2025-11.parquet
    CloudFront-->>Ingest: Return 46,912 rows
    Ingest->>CloudFront: Download taxi_zone_lookup.csv
    CloudFront-->>Ingest: Return 265 rows
    
    Ingest->>Ingest: Apply data types (Int64, string, float64)
    Ingest->>PostgreSQL: Connect to pgdatabase:5432
    PostgreSQL->>DB: Create database ny_taxi
    
    Ingest->>DB: CREATE TABLE green_tripdata
    Ingest->>DB: INSERT chunks (50k rows at a time)
    Ingest->>DB: CREATE TABLE taxi_zones
    Ingest->>DB: INSERT all rows (265 total)
    
    Ingest-->>User: Data ingestion complete
    Note over Ingest: Container auto-removes (--rm flag)
    
    User->>pgAdmin: Open localhost:8085 in browser
    pgAdmin->>User: Login page
    User->>pgAdmin: Login (admin@admin.com)
    User->>pgAdmin: Register server (pgdatabase:5432)
    pgAdmin->>PostgreSQL: Connect to database
    PostgreSQL-->>pgAdmin: Return table list
    User->>pgAdmin: Query green_tripdata
    pgAdmin->>DB: SELECT * FROM green_tripdata
    DB-->>pgAdmin: Return results
    pgAdmin-->>User: Display data in browser
```

## File Relationships

```mermaid
graph LR
    subgraph "Configuration Files"
        A[docker-compose.yaml]
        B[Dockerfile]
        C[pyproject.toml]
    end

    subgraph "Application Code"
        D[hw_ingest_data.py]
    end

    subgraph "Docker Images"
        E[postgres:18<br/>from Docker Hub]
        F[pgadmin4<br/>from Docker Hub]
        G[python:3.13-slim<br/>from Docker Hub]
        H[taxi-ingest:v001<br/>custom built]
    end

    subgraph "Runtime Containers"
        I[pgdatabase]
        J[pgadmin]
        K[ingestion<br/>temporary]
    end

    A -->|pulls image| E
    A -->|pulls image| F
    A -->|creates container| I
    A -->|creates container| J
    
    B -->|uses base| G
    C -->|defines dependencies| B
    D -->|code to copy| B
    B -->|builds into| H
    H -->|runs as| K
    
    K -->|connects to| I
    J -->|connects to| I

    style A fill:#fff4e1
    style B fill:#fff4e1
    style C fill:#fff4e1
    style D fill:#ffe8e8
    style E fill:#e1f5ff
    style F fill:#e1f5ff
    style G fill:#e1f5ff
    style H fill:#e8f5e9
    style I fill:#e8f5e9
    style J fill:#e8f5e9
    style K fill:#ffebee
```

## Network Architecture

```mermaid
graph TB
    subgraph "Host Machine: localhost"
        A[Web Browser]
        B[Terminal/VS Code]
    end

    subgraph "Docker Network: hw_wk1_default"
        C[pgdatabase<br/>PostgreSQL<br/>Internal: 5432]
        D[pgadmin<br/>pgAdmin UI<br/>Internal: 80]
        E[Ingestion Container<br/>Runs once, removes]
    end

    subgraph "Port Mappings"
        F[localhost:5433]
        G[localhost:8085]
    end

    subgraph "Internet"
        H[CloudFront CDN<br/>parquet file]
        I[GitHub Releases<br/>CSV file]
    end

    A -->|HTTP| G
    B -->|docker commands| Docker
    
    G -.->|maps to| D
    F -.->|maps to| C
    
    D <-->|queries| C
    E -->|loads data| C
    E -->|downloads| H
    E -->|downloads| I

    style A fill:#e3f2fd
    style B fill:#e3f2fd
    style C fill:#e8f5e9
    style D fill:#e8f5e9
    style E fill:#ffebee
    style F fill:#fff9c4
    style G fill:#fff9c4
    style H fill:#f3e5f5
    style I fill:#f3e5f5
```

## Component Responsibilities

```mermaid
mindmap
  root((NYC Taxi<br/>Data Pipeline))
    Docker Compose
      Defines services
      Creates network
      Manages volumes
      Orchestrates startup
    Dockerfile
      Base image: Python 3.13
      Install uv package manager
      Install dependencies
      Copy ingestion script
      Set entry point
    hw_ingest_data.py
      Download data files
      Apply data types
      Connect to PostgreSQL
      Create tables
      Load data in chunks
      Handle SSL issues
    PostgreSQL Container
      Store database
      Persist to volume
      Accept connections
      Execute queries
    pgAdmin Container
      Web UI on port 8085
      Database management
      Query execution
      Visual data exploration
    Ingestion Container
      Temporary execution
      Auto-removes after run
      Network: hw_wk1_default
      Downloads from internet
```

## Legend

**Colors:**
- 🔵 Blue: External data sources or images
- 🟡 Yellow: Configuration files
- 🟢 Green: Running containers
- 🔴 Red: Temporary/ephemeral components
- 🟣 Purple: Database objects
- ⚪ Gray: Storage/volumes

**Line Types:**
- Solid arrows (→): Active connections or actions
- Dotted arrows (-.->): Persistent storage or network relationships
