# System Architecture - Data Workflow Management Platform

## Overview

This is a microservices-based data workflow management platform that enables users to create, collaborate on, and execute ETL/ML pipelines through a visual drag-and-drop interface. The system is built around Apache Airflow orchestration with real-time collaboration features.

## High-Level Architecture

```mermaid
graph TB
    %% User Layer
    User[User Browser] --> Frontend[Frontend<br/>Next.js :3000]
    
    %% Application Layer
    Frontend --> Backend[Backend<br/>FastAPI :8000]
    Backend --> AirflowWeb[Airflow Webserver<br/>:8080]
    Backend --> AirflowSched[Airflow Scheduler]
    
    %% Data Layer
    Backend --> Supabase[Supabase<br/>Authentication & App Data]
    AirflowWeb --> AirflowDB[(Airflow Metadata<br/>PostgreSQL :5432)]
    AirflowSched --> AirflowDB
    AirflowInit[Airflow Init] --> AirflowDB
    
    %% Storage Layer
    Backend --> SharedData[(Shared Data Volume<br/>/shared_data)]
    AirflowSched --> SharedData
    Frontend --> SharedData
    
    %% Dependencies
    Backend -.->|depends_on| AirflowDB
    AirflowWeb -.->|depends_on| AirflowDB
    AirflowWeb -.->|depends_on| AirflowInit
    AirflowSched -.->|depends_on| AirflowWeb
    Frontend -.->|depends_on| Backend
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef airflow fill:#fff3e0
    classDef database fill:#e8f5e8
    classDef storage fill:#fce4ec
    
    class Frontend frontend
    class Backend backend
    class AirflowWeb,AirflowSched,AirflowInit airflow
    class AirflowDB,Supabase database
    class SharedData storage
```

## Service Dependencies & Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant S as Supabase
    participant A as Airflow
    participant DB as Airflow PostgreSQL
    participant SD as Shared Data
    
    %% Authentication Flow
    U->>F: Login Request
    F->>S: Authenticate User
    S-->>F: JWT Token
    F-->>U: Login Success
    
    %% Workflow Creation
    U->>F: Create Workflow
    F->>B: Save Workflow
    B->>S: Store Metadata
    B->>A: Generate DAG
    A->>DB: Store DAG Info
    
    %% Workflow Execution
    U->>F: Execute Workflow
    F->>B: Trigger Execution
    B->>A: Start DAG Run
    A->>DB: Update Status
    A->>SD: Process Data
    A-->>B: Execution Results
    B-->>F: Status Updates
    F-->>U: Real-time Updates
```

## Database Architecture

### PostgreSQL Usage Clarification

The system uses **two separate PostgreSQL instances** for different purposes:

#### 1. Airflow Metadata Database (Local PostgreSQL)
```mermaid
graph LR
    AirflowWebserver --> AirflowMetaDB[(Airflow PostgreSQL<br/>Container :5432)]
    AirflowScheduler --> AirflowMetaDB
    AirflowInit --> AirflowMetaDB
    
    AirflowMetaDB --> TaskStates[Task States & History]
    AirflowMetaDB --> DAGRuns[DAG Runs & Schedules]
    AirflowMetaDB --> Variables[Airflow Variables]
    AirflowMetaDB --> Connections[Connection Configs]
```

**Purpose**: Stores Airflow's internal metadata
- Task execution states and history
- DAG run information and schedules
- Airflow variables and connections
- User sessions and permissions
- Task logs and performance metrics

**Configuration**: Defined in `docker-compose.dev.yaml` as `postgres:15` container

#### 2. Supabase (Hosted PostgreSQL)
```mermaid
graph LR
    Backend --> SupabaseAPI[Supabase API]
    Frontend --> SupabaseAPI
    
    SupabaseAPI --> SupabaseDB[(Supabase PostgreSQL<br/>Cloud Hosted)]
    SupabaseAPI --> Auth[GoTrue Auth]
    SupabaseAPI --> Realtime[Realtime Engine]
    SupabaseAPI --> Storage[Storage API]
    
    SupabaseDB --> UserProfiles[User Profiles]
    SupabaseDB --> Workflows[Workflow Definitions]
    SupabaseDB --> Organizations[Organizations]
    SupabaseDB --> Permissions[Collaborator Permissions]
```

**Purpose**: Stores application data and user management
- User authentication and profiles
- Workflow definitions and metadata
- Organization and team management
- Collaboration permissions
- Real-time collaboration state

**Configuration**: Accessed via `SUPABASE_URL` and `SUPABASE_KEY` environment variables

## Component Architecture

### Frontend Components

```mermaid
graph TD
    App[Next.js App] --> Auth[Authentication Pages]
    App --> Dashboard[Dashboard<br/>Workflow Management]
    App --> WorkflowEditor[Workflow Editor<br/>Drag & Drop]
    App --> WorkflowExecute[Workflow Execute<br/>Run & Monitor]
    App --> WorkflowHistory[Workflow History<br/>Execution Logs]
    
    WorkflowEditor --> TaskRegistry[Task Component Registry]
    WorkflowEditor --> Canvas[Workflow Canvas<br/>@dnd-kit]
    WorkflowEditor --> Sidebar[Config Sidebar]
    WorkflowEditor --> Collaboration[Real-time Collaboration]
    
    Dashboard --> DataTable[Data Tables<br/>@tanstack/react-table]
    
    Collaboration --> RealtimeCursor[Realtime Cursors]
    Collaboration --> PresenceIndicator[Presence Indicators]
    Collaboration --> CollaboratorManager[Collaborator Manager]
```

### Backend API Structure

```mermaid
graph TD
    FastAPI[FastAPI Main] --> AuthRoutes[Auth Routes<br/>/auth/*]
    FastAPI --> WorkflowRoutes[Workflow Routes<br/>/workflows/*]
    
    AuthRoutes --> AuthUtils[Auth Utils<br/>JWT Validation]
    WorkflowRoutes --> WorkflowPerms[Workflow Permissions]
    WorkflowRoutes --> DAGFactory[DAG Factory<br/>Dynamic Generation]
    
    FastAPI --> SupabaseClient[Supabase Client<br/>Database Operations]
    FastAPI --> AirflowAPI[Airflow API Client<br/>REST Integration]
    
    DAGFactory --> UserDAGs[User-specific DAGs<br/>/users/user_id/]
    AirflowAPI --> TriggerRuns[Trigger DAG Runs]
    AirflowAPI --> StatusCheck[Status Monitoring]
```

### Airflow Task Components

```mermaid
graph TD
    TaskRegistry[Task Component Registry] --> Extraction[Data Extraction]
    TaskRegistry --> Transformation[Data Transformation]
    TaskRegistry --> Loading[Data Loading]
    TaskRegistry --> Analysis[Analysis & ML]
    TaskRegistry --> Utils[Utilities]
    
    Extraction --> CSV[CSV Files]
    Extraction --> RestAPI[REST APIs]
    Extraction --> Database[Database Queries]
    Extraction --> WebScraping[Web Scraping]
    Extraction --> FTPSFTP[FTP/SFTP]
    
    Transformation --> DataCleaning[Data Cleaning]
    Transformation --> DataJoin[Data Joins]
    Transformation --> DataFilter[Data Filtering]
    Transformation --> DataPivot[Data Pivot]
    Transformation --> Cohorts[Cohort Harmonization]
    
    Loading --> FileExport[File Export]
    Loading --> PostgresLoad[PostgreSQL Loading]
    Loading --> BatchLoad[Batch Loading]
    Loading --> IncrementalLoad[Incremental Loading]
    
    Analysis --> MachineLearning[Machine Learning Pipeline]
    Analysis --> Visualization[Data Visualization]
    Analysis --> Statistics[Descriptive Statistics]
    Analysis --> Reports[Report Generation]
    
    Utils --> Notifications[Notifications]
    Utils --> CohortsUtils[Cohort Utilities]
```

## Data Flow Patterns

### Workflow Creation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend Editor
    participant BE as Backend API
    participant S as Supabase
    participant DF as DAG Factory
    participant A as Airflow
    
    U->>FE: Drag & Drop Tasks
    FE->>FE: Validate Configuration
    FE->>BE: Save Workflow
    BE->>S: Store Workflow Metadata
    BE->>DF: Generate DAG Python File
    DF->>A: Write to /users/user_id/
    A->>A: Auto-discover New DAG
    A-->>BE: DAG Available
    BE-->>FE: Workflow Saved
    FE-->>U: Success Notification
```

### Workflow Execution Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant A as Airflow
    participant DB as Airflow PostgreSQL
    participant SD as Shared Data
    
    U->>FE: Trigger Execution
    FE->>BE: Execute Workflow
    BE->>A: POST /dags/{dag_id}/dagRuns
    A->>DB: Create DAG Run Record
    A->>A: Start Task Execution
    A->>SD: Read/Write Data Files
    A->>DB: Update Task States
    A-->>BE: Execution Status
    BE-->>FE: Real-time Updates
    FE-->>U: Progress Display
```

## Real-time Collaboration

### Collaboration Architecture

```mermaid
graph TD
    UserA[User A Browser] --> WebSocket[WebSocket Connection]
    UserB[User B Browser] --> WebSocket
    UserC[User C Browser] --> WebSocket
    
    WebSocket --> BackendCollab[Backend Collaboration Handler]
    BackendCollab --> PresenceManager[Presence Management]
    BackendCollab --> CursorTracking[Cursor Tracking]
    BackendCollab --> EditLocks[Edit Locks]
    
    PresenceManager --> SupabaseRealtime[Supabase Realtime]
    SupabaseRealtime --> CollabState[(Collaboration State<br/>Supabase PostgreSQL)]
    
    BackendCollab --> PermissionSystem[Permission System]
    PermissionSystem --> RoleBasedAccess[Role-based Access<br/>view/edit/execute/manage]
```

### Collaboration Features

- **Real-time Cursors**: Show other users' mouse positions using WebSocket
- **Presence Indicators**: Display active collaborators with avatars
- **Permission System**: Role-based access (view/edit/execute/manage)
- **Conflict Resolution**: Operational transformation for simultaneous edits
- **Edit Locks**: Prevent concurrent editing of same components

## Security & Isolation

### User Isolation Strategy

```mermaid
graph TD
    AirflowDAGs[/opt/airflow/dags/] --> Users[users/]
    Users --> UserA[user_cb3518f9_a698_43a7_91cf_8479de0a346d/]
    Users --> UserB[user_cbd6da17_3e9d_4d32_8127_f3ef4d000bed/]
    Users --> UserC[user_d65788fe_2aba_478a_9513_bd7c01d72ca7/]
    
    UserA --> UserADAGs[User A DAG Files]
    UserB --> UserBDAGs[User B DAG Files]
    UserC --> UserCDAGs[User C DAG Files]
    
    SharedData[/shared_data/] --> UserAData[user_a/]
    SharedData --> UserBData[user_b/]
    SharedData --> UserCData[user_c/]
```

### Security Layers

1. **Authentication**: Supabase JWT tokens with configurable expiration
2. **Authorization**: Role-based permissions stored in Supabase
3. **Data Isolation**: User-specific DAG directories and data folders
4. **API Security**: Validated endpoints with proper authentication headers
5. **Container Isolation**: Docker network separation between services

## Deployment Architecture

### Development Environment

```mermaid
graph TD
    DevEnv[Development Environment] --> Frontend[Frontend :3000<br/>Hot Reload]
    DevEnv --> Backend[Backend :8000<br/>Debug Mode]
    DevEnv --> AirflowWeb[Airflow Web :8080<br/>Dev Mode]
    DevEnv --> AirflowSched[Airflow Scheduler<br/>LocalExecutor]
    DevEnv --> PostgresLocal[(PostgreSQL :5432<br/>Exposed for Debug)]
    
    Frontend --> SharedVol[Shared Volume<br/>Live Mounting]
    Backend --> SharedVol
    AirflowSched --> SharedVol
    
    PostgresLocal --> AirflowWeb
    PostgresLocal --> AirflowSched
    PostgresLocal --> Backend
    
    SupabaseCloud[Supabase Cloud] --> Backend
    SupabaseCloud --> Frontend
```

### Production Environment (without Nginx)

```mermaid
graph TD
    ProdEnv[Production Environment] --> Frontend[Frontend :3000<br/>Optimized Build]
    ProdEnv --> Backend[Backend :8000<br/>Production Mode]
    ProdEnv --> AirflowWeb[Airflow Web :8080<br/>Production]
    ProdEnv --> AirflowSched[Airflow Scheduler<br/>LocalExecutor]
    ProdEnv --> PostgresProd[(PostgreSQL :5432<br/>Internal Network)]
    
    Frontend --> PersistentVol[Persistent Volume<br/>Data Storage]
    Backend --> PersistentVol
    AirflowSched --> PersistentVol
    
    PostgresProd --> AirflowWeb
    PostgresProd --> AirflowSched
    PostgresProd --> Backend
    
    SupabaseCloud[Supabase Cloud] --> Backend
    SupabaseCloud --> Frontend
```

## Scalability Considerations

### Horizontal Scaling Points

```mermaid
graph TD
    LoadBalancer[Load Balancer] --> FrontendA[Frontend Instance A]
    LoadBalancer --> FrontendB[Frontend Instance B]
    LoadBalancer --> FrontendC[Frontend Instance C]
    
    APIGateway[API Gateway] --> BackendA[Backend Instance A]
    APIGateway --> BackendB[Backend Instance B]
    APIGateway --> BackendC[Backend Instance C]
    
    BackendA --> SharedPostgres[(Shared PostgreSQL<br/>Airflow Metadata)]
    BackendB --> SharedPostgres
    BackendC --> SharedPostgres
    
    SharedPostgres --> AirflowScheduler[Airflow Scheduler<br/>Single Instance]
    AirflowScheduler --> DistributedExecutor[Future: CeleryExecutor<br/>Redis Backend]
```

### Performance Optimizations

1. **Frontend**: Multiple Next.js instances with session affinity
2. **Backend**: FastAPI instances sharing PostgreSQL connection pool
3. **Airflow**: Upgrade path from LocalExecutor to CeleryExecutor for distributed processing
4. **Database**: Read replicas for analytics and reporting queries
5. **Caching**: Redis integration for session management and frequent queries

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Next.js | 15.2.4 | React-based UI framework |
| UI Components | @dnd-kit, TailwindCSS | Latest | Drag-and-drop, styling |
| Backend | FastAPI | Latest | Python API framework |
| Orchestration | Apache Airflow | 2.10.4 | Workflow execution engine |
| Airflow Database | PostgreSQL | 15 | Airflow metadata storage |
| Application Database | Supabase PostgreSQL | Latest | User & workflow data |
| Authentication | Supabase Auth (GoTrue) | Latest | JWT-based authentication |
| Real-time | Supabase Realtime | Latest | WebSocket collaboration |
| Containerization | Docker Compose | Latest | Service orchestration |

## Key Architectural Benefits

1. **Clear Separation of Concerns**: Separate databases for Airflow metadata vs application data
2. **Modular Design**: Component-based task system allows easy extension
3. **Real-time Collaboration**: Live editing with presence awareness via Supabase Realtime
4. **User Isolation**: Multi-tenant architecture with proper separation
5. **Dynamic Workflow Generation**: Runtime DAG creation from visual configurations
6. **Development-friendly**: Hot reloading and debugging support
7. **Cloud-native Authentication**: Leverages Supabase for robust user management

## Future Architecture Considerations

1. **Message Queue**: Add Redis/RabbitMQ for async communication patterns
2. **Microservices**: Split backend into smaller, domain-focused services
3. **Distributed Execution**: Upgrade to CeleryExecutor with Redis backend for scalability
4. **Monitoring**: Add observability with Prometheus/Grafana integration
5. **Multi-region**: Database replication and geographic distribution
6. **API Gateway**: Implement proper API gateway for rate limiting and security