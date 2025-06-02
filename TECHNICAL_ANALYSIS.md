# Technical and Organizational Analysis: Data Workflow Management Platform

## Project Overview

This project represents a comprehensive **data workflow management and orchestration platform** designed to enable users to create, manage, and execute complex data processing pipelines through a visual drag-and-drop interface. The platform serves as a bridge between technical and non-technical users, providing enterprise-grade data pipeline capabilities with an intuitive user experience.

### Primary Purpose
- **Visual Workflow Creation**: Enable users to design data pipelines using a drag-and-drop interface
- **Multi-User Collaboration**: Support real-time collaborative editing with presence indicators and user management
- **Data Pipeline Orchestration**: Execute complex ETL/ELT workflows using Apache Airflow as the orchestration engine
- **Specialized Data Processing**: Provide domain-specific components for cohort data harmonization and machine learning workflows

---

## Stakeholders and User Personas

### Primary Actors

1. **Data Scientists & Analysts**
   - Create machine learning pipelines with preprocessing, training, evaluation, and deployment stages
   - Analyze data using statistical and visualization components
   - Benefit from the modular ML task registry (regression, classification, forecasting)

2. **Data Engineers**
   - Design complex ETL/ELT pipelines for data integration
   - Utilize extraction components (CSV, JSON, XML, APIs, databases)
   - Manage data transformations and loading operations

3. **Healthcare/Research Organizations** 
   - Leverage specialized cohort data harmonization tools
   - Use OMOP CDM data transformation capabilities
   - Process clinical research data with standardized protocols

4. **Business Users & Domain Experts**
   - Create workflows without deep technical knowledge
   - Collaborate with technical teams through shared workspace
   - Monitor workflow execution and results

5. **System Administrators**
   - Manage user access and permissions
   - Monitor platform performance and resource usage
   - Configure deployment environments

---

## System Architecture

### High-Level Architecture Pattern
The platform follows a **microservices architecture** with service isolation, implemented using Docker containers and orchestrated through Docker Compose. The architecture emphasizes:
- **Separation of Concerns**: Each service handles specific responsibilities
- **Scalability**: Independent scaling of frontend, backend, and processing components
- **Data Isolation**: User-specific workflow execution with proper access controls

### Core Components

#### 1. **Frontend Service** (Next.js 15.2.4)
- **Technology Stack**: React 19, TypeScript, TailwindCSS, DaisyUI
- **Key Features**:
  - Drag-and-drop workflow editor using @dnd-kit
  - Real-time collaboration with cursor presence and activity feeds
  - User authentication and authorization
  - Responsive data tables with @tanstack/react-table
  - Form validation with React Hook Form + Zod

**Key Files:**
- `frontend/src/components/workflow/WorkflowEditor.tsx:28-344` - Main editor orchestration
- `frontend/src/components/workflow/WorkflowCanvas.tsx:24-101` - Drag-and-drop canvas
- `frontend/src/components/airflow-tasks/Registry.ts:5-1433` - Task component registry

#### 2. **Backend API Service** (FastAPI)
- **Technology Stack**: Python 3.10, FastAPI, Pydantic, Supabase client
- **Responsibilities**:
  - Workflow CRUD operations and user management
  - Dynamic DAG generation for Airflow
  - Authentication and authorization middleware
  - File upload handling and data persistence
  - Real-time collaboration coordination

**Key Files:**
- `backend/api/main.py:1-49` - Application entry point and CORS configuration
- `backend/api/routes/workflows.py:21-362` - Workflow management endpoints
- `backend/api/utils/dag_factory.py:37-196` - Dynamic DAG generation engine

#### 3. **Apache Airflow Orchestration** (v2.10.4)
- **Configuration**: LocalExecutor with PostgreSQL backend
- **Architecture**: Webserver + Scheduler + Init containers
- **Custom Components**: Modular task library organized by function type

**Task Component Organization:**
```
components/
├── extraction/          # Data ingestion tasks
├── transformation/      # Data manipulation and processing
├── loading/            # Data output and storage
├── analysis/           # Statistical analysis and ML
└── utils/              # Utility functions and notifications
```

**Key Files:**
- `airflow/dags/components/extraction/csv.py:11-66` - CSV data extraction with encoding detection
- `airflow/dags/components/transformation/cohorts/harmonize.py:8-131` - Healthcare data harmonization
- `airflow/dags/components/analysis/machine_learning/data_ingestion.py:11-57` - ML data ingestion pipeline

#### 4. **Database Layer** (PostgreSQL 15)
- **Shared Storage**: Common database for both backend application and Airflow metadata
- **Data Isolation**: User-specific workflow storage with collaboration support
- **Integration**: Supabase client for enhanced database operations and real-time features

#### 5. **Infrastructure Layer** 
- **Development**: Docker Compose with live code reloading and shared volumes
- **Production**: Nginx reverse proxy with service routing and load balancing
- **Storage**: Persistent volumes for database and shared file storage (`/shared_data`)

---

## Key Features and Capabilities

### 1. **Visual Workflow Designer**
- **Drag-and-Drop Interface**: Intuitive task placement and connection
- **Task Configuration**: Dynamic forms based on task type with validation
- **Dependency Management**: Visual representation of task relationships
- **Real-time Validation**: Immediate feedback on configuration errors

### 2. **Extensive Task Library** (89+ predefined components)

#### **Data Extraction Components**
- File formats: CSV, JSON, XML with encoding detection
- APIs: REST endpoints with authentication and pagination
- Databases: SQL query execution with parameterization
- External sources: FTP/SFTP, web scraping with browser automation

#### **Data Transformation Components**
- Standard operations: Filtering, aggregation, joins, pivots, sorting
- Data quality: Cleaning, deduplication, outlier detection
- Specialized: Cohort harmonization, healthcare data standardization

#### **Machine Learning Pipeline**
- Data preprocessing: Scaling, encoding, missing value handling
- Model training: Multiple algorithms (Random Forest, XGBoost, Neural Networks)
- Model evaluation: Comprehensive metrics and validation
- Model deployment: Multiple target environments (local, cloud, API)

#### **Data Loading Components**
- Database: Batch loading, incremental updates, CDC processing
- File export: Multiple formats with compression options
- Streaming: Real-time data loading with windowing

### 3. **Real-time Collaboration**
- **Live Presence**: See other users working on the same workflow
- **Cursor Tracking**: Real-time cursor positions and user activity
- **Permission Management**: Granular access control (view, edit, execute, manage)
- **Activity Feeds**: Live updates on user actions and workflow changes

### 4. **User and Workflow Isolation**
- **Multi-tenancy**: User-specific DAG generation with isolated execution
- **Namespace Separation**: Workflows organized by user ownership
- **Access Control**: Role-based permissions with collaborator management

### 5. **Execution and Monitoring**
- **Immediate Execution**: Real-time workflow triggering
- **Scheduled Execution**: Cron-based recurring workflows
- **Execution History**: Detailed logs and result tracking
- **Error Handling**: Comprehensive error reporting and retry mechanisms

---

## Technical Implementation Details

### Data Flow Architecture
```
User Interface → FastAPI Backend → Dynamic DAG Generation → Airflow Execution → Results Storage
     ↓                                      ↓                        ↓
Frontend State      Database Storage     User Isolation      Shared File System
     ↓                                      ↓                        ↓
Real-time Sync      Workflow Metadata   Task Execution     Data Persistence
```

### Dynamic DAG Generation
The platform's core innovation lies in its dynamic DAG generation system (`backend/api/utils/dag_factory.py:37-196`):

1. **User Input Processing**: Convert visual workflow to structured configuration
2. **Template Generation**: Create Airflow DAG code with proper imports and dependencies
3. **User Isolation**: Namespace DAGs with user-specific prefixes
4. **File Management**: Write DAG files to user-specific directories

### Task Registry System
The modular task system (`frontend/src/components/airflow-tasks/Registry.ts:5-1433`) provides:
- **Type-safe Configuration**: Pydantic-based validation schemas
- **Dynamic UI Generation**: Automatic form creation from task definitions
- **Extensibility**: Plugin architecture for adding new task types
- **Reusability**: Consistent task interface across different domains

### Real-time Collaboration Implementation
- **WebSocket Integration**: Real-time communication for cursor tracking
- **State Synchronization**: Conflict resolution for simultaneous edits
- **Presence Management**: User session tracking and activity broadcasting

---

## Deployment and Operations

### Development Environment
- **Local Development**: `docker-compose -f docker-compose.dev.yaml up`
- **Hot Reloading**: Live code updates for frontend and backend
- **Shared Volumes**: Consistent data across services
- **Debug Access**: Direct service port exposure for development tools

### Production Environment  
- **Container Orchestration**: `docker-compose -f docker-compose.prod.yaml up`
- **Reverse Proxy**: Nginx routing with upstream service configuration
- **Service Discovery**: Container networking with service names
- **Resource Management**: Container restart policies and health checks

### Security Considerations
- **Authentication**: Supabase-based user management with JWT tokens
- **Authorization**: Role-based access control with workflow-level permissions
- **Data Isolation**: User-specific execution environments
- **Input Validation**: Comprehensive data validation and sanitization

---

## Technology Choices and Rationale

### Frontend Technology Stack
- **Next.js 15**: Full-stack React framework with SSR capabilities
- **TypeScript**: Type safety for large-scale application development
- **@dnd-kit**: Accessible drag-and-drop with touch support
- **TailwindCSS + DaisyUI**: Utility-first styling with component library

### Backend Technology Stack
- **FastAPI**: High-performance async API framework with automatic documentation
- **Pydantic**: Data validation and serialization with type hints
- **Supabase**: PostgreSQL with real-time capabilities and built-in authentication

### Orchestration Technology Stack
- **Apache Airflow**: Industry-standard workflow orchestration
- **LocalExecutor**: Simplified deployment with shared database
- **PostgreSQL**: Reliable relational database with ACID compliance

---

## Conclusion

This platform represents a sophisticated solution for democratizing data pipeline creation and management. By combining visual design tools with enterprise-grade orchestration capabilities, it bridges the gap between technical and non-technical users while maintaining the scalability and reliability required for production data workflows.

The modular architecture, comprehensive task library, and real-time collaboration features position this platform as a competitive solution in the data pipeline management space, with particular strengths in healthcare data processing and machine learning workflow orchestration.