### Overview of the Docker Compose File

This is a Docker Compose configuration file (version 3.8) for orchestrating a multi-container application stack named "appdemo". Docker Compose is a tool for defining and running multi-container Docker applications using a YAML file. This file defines services, networks, volumes, and their interdependencies to set up a full-stack web application with frontend, backend, databases, authentication, AWS service emulation, database management tools, a reverse proxy, and a custom emulator for security scanning.

The setup appears to be for a development or local environment of a web application that involves user authentication, data storage with geospatial capabilities (via PostGIS), file storage and security emulation (using LocalStack to mimic AWS S3 and GuardDuty), and a frontend served via Nginx. It uses environment variables from `.env` and override files for configuration, allowing flexibility for secrets and settings without hardcoding them.

Key high-level behaviors:
- **Containerization**: All components run in isolated Docker containers for portability and consistency across environments (e.g., handling Apple M1/M4 chip compatibility with `platform: linux/amd64`).
- **Networking**: All services connect via a custom bridge network (`appdemo-network`) for internal communication.
- **Volumes**: Persistent data storage for databases and shared static files between frontend and backend.
- **Dependencies**: Services start in a specific order (e.g., backend depends on database and Keycloak).
- **Builds**: Custom Docker images are built for several services using Dockerfiles in subdirectories (e.g., `./web-ui` for frontend).
- **Ports**: Exposes various ports for local access (e.g., frontend on 3000, backend APIs on 8080/8443).
- **Environment Variables**: Pulled from `.env` files, allowing customization (e.g., database credentials, AWS keys).
- **Health Checks**: Ensures Keycloak is healthy before dependent services start.

The application likely handles data-intensive tasks (e.g., geospatial data via PostGIS), secure authentication (Keycloak), and cloud-like storage/security (LocalStack emulating AWS). Based on the provided POM.xml for the backend (built from `./api-server`), it is a Spring Boot-based Java REST API server with features for database interactions, security, AWS S3 integration, PDF processing, and OCR (Optical Character Recognition) capabilities, suggesting the app involves document handling, analysis, or ingestion (e.g., extracting text from scanned PDFs or images). The frontend (built from `./web-ui`) is a React-based single-page application (SPA) as detailed in its `package.json`, focusing on interactive UI elements like maps, tables, and forms, integrated with the backend via APIs.

### Detailed Explanation of What It's Doing

This configuration launches 9 services that form a cohesive application ecosystem. Here's a breakdown of each service and its role:

1. **Frontend (appdemo-frontend)**:
   - Builds a custom image from `./web-ui` using Node.js (builder base: `node:20-alpine`) for building the UI and Nginx (runner base: `nginx:1.27.3`) for serving it.
   - Serves a web UI on port 3000 (mapped to container's 80).
   - Shares static files via a volume (`static-files`) with the backend.
   - Loads env vars from `.env`.
   - Purpose: Handles user-facing interface, a React-based SPA (version 18.3.1) built with Vite (5.4.19) as the development/build tool for fast bundling and hot module replacement (HMR). The app is named "appdemo" (version 0.1.0) and configured for private use with a homepage at `/appdemo`.
   - **React Package Details** (from `package.json`):
     - **What It Is**: A modern React application setup using Vite for tooling, Material-UI (MUI v7.1.0) for styled components and icons, Redux Toolkit (2.2.7) for state management, React Router (7.6.0) for navigation, and mapping libraries like Leaflet (1.9.4 with react-leaflet 4.2.1) and OpenLayers (ol 10.6.1) for geospatial visualizations. It includes authentication via OIDC (react-oidc-context 3.2.0, integrating with Keycloak), date handling (date-fns 4.1.0, dayjs 1.11.13, @mui/x-date-pickers 8.3.1), and utilities for geohash (latlon-geohash 2.0.0), MGRS coordinates (mgrs 2.1.0), and resizable panels (react-resizable-panels 3.0.3). Tables are handled with material-react-table (3.2.1), and HTTP requests via Axios (1.8.3). Testing uses Vitest (3.0.9) with coverage, Storybook (8.6.12) for component stories, and ESLint/Prettier for code quality.
     - **How It Is Used**: Scripts like `yarn dev` or `yarn start` run Vite server on port 3000 with HMR; `yarn build` compiles to production assets (output to `/dist` for Nginx serving); `yarn lint` and `yarn format` enforce code style; `yarn test` runs Vitest tests; `yarn storybook` launches Storybook for isolated component development. Dependencies are managed via Yarn/NPM, with resolutions for specific versions to avoid conflicts/vulnerabilities (e.g., Babel 7.26.0 for transpilation).
     - **Why It Is Used**: React provides a component-based architecture for building dynamic, responsive UIs efficiently. Vite offers faster builds than Create React App (CRA), which this setup partially references (e.g., `eject` script). MUI ensures consistent, accessible design with theming. Redux manages global state (e.g., user auth, map data). Mapping libs support geospatial features (e.g., displaying layers on maps). OIDC handles secure login flows. Testing/story tools improve dev productivity and quality. Overall, this stack enables a scalable, maintainable frontend for complex apps like GIS tools with real-time interactions.
     - **Examples of Use**:
       - **Mapping Integration**: Use Leaflet/OpenLayers for rendering geospatial data: `<MapContainer center={[lat, lon]} zoom={13}><TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" /></MapContainer>` in a React component, fetching data from backend API via Axios.
       - **State Management**: Redux store for auth: `const store = configureStore({ reducer: { auth: authReducer } });` then `<Provider store={store}><App /></Provider>`.
       - **Auth Flow**: Wrap app in `<AuthProvider settings={oidcConfig}><Routes>...</Routes></AuthProvider>` to handle Keycloak redirects and token storage.
       - **Tables/Forms**: `<MaterialReactTable columns={columns} data={data} />` for displaying query results; date pickers like `<DatePicker value={selectedDate} onChange={handleChange} />`.
       - **Dev Workflow**: Run `yarn storybook` to develop a button component in isolation: `export const Primary: Story = { args: { label: 'Button' } };`.
       - **Build/Deploy**: `yarn build` generates optimized bundles; Docker uses this to create the image, serving via Nginx.

2. **Backend (appdemo-backend)**:
   - Builds a custom image from `./api-server` using Alpine Linux bases (both builder and runner: `alpine:3.21`).
   - A Java-based API server using Spring Boot 3.5.4 (with OpenJDK 17 or 21 via profile), configured for REST APIs, database access, security, and integrations.
   - Exposes APIs on multiple ports (e.g., 8080 for HTTP, 8443 for HTTPS, 9090 possibly for management/metrics like Actuator endpoints).
   - Depends on the database (`appdemo-db`) and Keycloak for startup.
   - Shares static files with frontend.
   - Loads env vars from `.env` and `.env-docker-compose-override` (for overrides like dev/prod settings).
   - **Java Technologies Used** (derived from POM.xml analysis): The backend is built as a Maven project with a focus on secure, scalable API development, vulnerability mitigation (e.g., updated versions for CVEs), and specialized processing for documents/PDFs. Key technologies include:
     - **Spring Boot (3.5.4)**: 
       - **What/How Used**: Core framework for the application, providing auto-configuration for web servers, dependency injection, and starters (e.g., `spring-boot-starter-web` for REST controllers, `spring-boot-starter-data-jpa` for ORM/database interactions, `spring-boot-starter-security` and `spring-boot-starter-oauth2-resource-server` for authentication/authorization).
       - **Why Needed**: Simplifies building production-ready applications with embedded servers (Tomcat by default, overridden to 10.1.44 for vulns), health checks via Actuator, and easy integration with other Spring modules. It handles bootstrapping the app, managing beans, and providing a standalone executable JAR.
       - **Examples**: REST endpoints defined with `@RestController` annotations; JPA repositories for CRUD on PostGIS entities (e.g., geospatial queries like `ST_Intersects`); OAuth2 token validation for secured routes (e.g., `@PreAuthorize` for role-based access). In this setup, it integrates with Keycloak for JWT-based auth.
     
     - **Spring Data JPA**:
       - **What/How Used**: Via `spring-boot-starter-data-jpa`, it provides repository interfaces for database operations, using Hibernate as the JPA provider.
       - **Why Needed**: Abstracts SQL queries into Java methods, supports entity mapping, transactions, and pagination. Essential for interacting with PostGIS (e.g., handling spatial types like Geometry).
       - **Examples**: Defining `@Entity` classes for tables (e.g., User or Location entities); repositories like `UserRepository extends JpaRepository<User, Long>` with custom queries (e.g., `@Query("SELECT u FROM User u WHERE u.location WITHIN :area")`).
     
     - **Spring Security (6.5.2)**:
       - **What/How Used**: Configures authentication/authorization, integrated with OAuth2 for resource server protection. Uses Nimbus JOSE JWT for token handling.
       - **Why Needed**: Secures APIs against unauthorized access, especially in a multi-user app with sensitive data (e.g., geospatial info). Mitigates vulns like those in older versions.
       - **Examples**: Security config with `SecurityFilterChain` to enable JWT validation from Keycloak; protecting endpoints like `/api/data` with `@Secured("ROLE_ADMIN")`.
     
     - **Liquibase**:
       - **What/How Used**: Database migration tool for schema changes, integrated via `liquibase-core`.
       - **Why Needed**: Manages database evolutions (e.g., creating tables, indexes) in a version-controlled way, ensuring consistency across envs.
       - **Examples**: Changelog files in `src/main/resources/db/changelog` with SQL or YAML for migrations (e.g., adding a geospatial column: `ADD COLUMN location GEOMETRY`).
     
     - **AWS SDK for Java (2.31.47)**:
       - **What/How Used**: `software.amazon.awssdk:s3` for interacting with S3 (or LocalStack emulation).
       - **Why Needed**: Handles file uploads/downloads to cloud storage, integrated with GuardDuty emulator for scanning.
       - **Examples**: Using `S3Client` to put objects (e.g., `s3Client.putObject(PutObjectRequest.builder().bucket("my-bucket").key("file.pdf").build(), RequestBody.fromFile(file))`); tagging for malware status.
     
     - **PDFBox (3.0.3) and Related (JAI-ImageIO, JBIG2-ImageIO)**:
       - **What/How Used**: For PDF parsing, rendering, and image extraction.
       - **Why Needed**: Processes PDF documents, handling formats like JPEG2000 or JBIG2 to avoid errors during extraction.
       - **Examples**: Loading PDFs with `PDDocument.load(file)`; extracting text/images (e.g., for metadata analysis or conversion to searchable text).
     
     - **Tesseract/Tess4J (5.13.0) and Leptonica**:
       - **What/How Used**: OCR engine for text recognition from images/PDFs, with platform-specific bindings.
       - **Why Needed**: Extracts text from scanned/non-searchable documents, crucial for apps involving document ingestion (e.g., analyzing geospatial reports).
       - **Examples**: Initializing `ITesseract instance = new Tesseract(); instance.doOCR(imageFile)` to get text; integrated with PDFBox for multi-page scans.
     
     - **Apache Tika (3.1.0)**:
       - **What/How Used**: Content analysis and metadata extraction from files.
       - **Why Needed**: Detects file types and extracts content/metadata, complementing PDF/OCR processing.
       - **Examples**: `Tika tika = new Tika(); String content = tika.parseToString(inputStream);` for file parsing.
     
     - **ModelMapper (3.2.0)**:
       - **What/How Used**: Maps DTOs to/from entities.
       - **Why Needed**: Simplifies object conversions, reducing boilerplate in APIs.
       - **Examples**: `ModelMapper mapper = new ModelMapper(); UserDTO dto = mapper.map(userEntity, UserDTO.class);`.
     
     - **Springdoc OpenAPI (2.2.0)**:
       - **What/How Used**: Generates Swagger UI for API docs.
       - **Why Needed**: Auto-documents endpoints for devs/testers.
       - **Examples**: Access `/swagger-ui.html` for interactive API exploration.
     
     - **Testing Tools (RestAssured, Testcontainers)**:
       - **What/How Used**: Integration/unit tests with mocked DB/S3 via Testcontainers; API testing with RestAssured.
       - **Why Needed**: Ensures reliability; emulates deps like PostgreSQL/LocalStack in tests.
       - **Examples**: `@Testcontainers` with `PostgreSQLContainer` for DB tests; `given().get("/api").then().statusCode(200)`.
     
     - **Other (Lombok, Jackson 2.19.2, Netty 4.2.4.Final)**:
       - Lombok for annotations like `@Data`; Jackson for JSON serialization; Netty for networking (overridden for vulns).
       - **Why Needed**: Reduces code verbosity, handles JSON, improves performance/security.

3. **Database (appdemo-db)**:
   - Uses PostGIS image (PostgreSQL with geospatial extensions) for storing application data.
   - Configured with user/password/DB from env vars.
   - Persistent data in volume `appdemo-pg-data`.
   - Exposes port 5432 for local connections.
   - Commented init scripts suggest SQL files for schema setup (e.g., metadata and audit tables), but they're disabled—likely run manually or via migrations (e.g., Liquibase in backend).

4. **Keycloak Database (appdemo-kc-db)**:
   - A separate PostgreSQL instance for Keycloak's data.
   - Configured similarly to `appdemo-db` but on port 5433 to avoid conflicts.
   - Persistent data in `appdemo-kc-pg-data`.
   - Runs an init script (`init-db.sh`) on startup for database setup.

5. **Keycloak (appdemo-keycloak)**:
   - Builds a custom image from `./keycloak` based on Keycloak 25.0.4.
   - Handles identity and access management (IAM): authentication, authorization, SSO.
   - Connects to its own DB (`appdemo-kc-db`).
   - Imports realms/users from `./keycloak/import/` and exports to `./keycloak/export/`.
   - Health check pings port 8080 with retries.
   - Command starts in dev mode with realm import; commented options for export.
   - Features enabled: Advanced auth like token exchange, step-up auth.
   - Exposes ports 8081 (HTTP) and 9000 (possibly metrics/debug).
   - Environment tweaks for dev (e.g., relaxed hostname checks). Integrates with frontend's OIDC for seamless auth.

6. **LocalStack (appdemo-localstack)**:
   - Uses LocalStack image to emulate AWS services locally (here, only S3 enabled via `SERVICES=s3`).
   - For testing AWS integrations without real cloud costs (e.g., S3 bucket for file storage).
   - Mounts `/var/run/docker.sock` for Lambda support if needed.
   - Debug mode enabled; data in `/tmp/localstack`.
   - Exposes port 4566 for AWS API endpoints (e.g., http://localhost:4566).
   - Init scripts from `./localstack/` for setup (e.g., creating buckets).

7. **pgAdmin (appdemo-pgadmin)**:
   - Web-based admin tool for PostgreSQL databases (dpage/pgadmin4 image).
   - Access via port 8083 with email/password from env vars.
   - Persistent config in `pgadmin-data` volume.
   - Used for browsing/managing `appdemo-db` and `appdemo-kc-db`.

8. **Nginx (appdemo-nginx)**:
   - Builds custom image from `./nginx` (likely a reverse proxy config).
   - Exposes port 80, mapping to container's 8080—possibly proxies traffic to other services (e.g., serving frontend statics).
   - Depends on Keycloak (for auth integration?).
   - Env var for Content Security Policy (CSP) hosts.

9. **GuardDuty Emulator (guard-duty)**:
   - Custom build from `./guard-duty-emulation`.
   - Emulates AWS GuardDuty malware scanning on S3 objects.
   - Polls S3 (via LocalStack endpoint) every 3 seconds, tags objects with scan status (e.g., "NO_THREATS_FOUND").
   - Depends on LocalStack.
   - For simulating security workflows in dev.

Overall orchestration:
- **Startup Sequence**: Databases first, then Keycloak (with health check), backend (depends on DB/Keycloak), others in parallel.
- **Shared Resources**: Volumes for data persistence; network for service discovery (e.g., backend connects to `appdemo-db:5432`).
- **Customization**: Build args allow overriding base images (e.g., for different Node/Java versions).
- **Platform Fix**: `linux/amd64` ensures compatibility on ARM chips like Apple Silicon.

### Technologies Used

- **Containerization/Orchestration**: Docker (for containers), Docker Compose v3.8 (for multi-service management).
- **Frontend**: React 18.3.1 (core library for UI components), Vite 5.4.19 (build tool for fast dev/prod bundling), Material-UI 7.1.0 (for themed components/icons), Redux Toolkit 2.2.7 (state management), React Router 7.6.0 (routing), Leaflet 1.9.4/OpenLayers 10.6.1 (maps), react-oidc-context 3.2.0 (auth), Axios 1.8.3 (HTTP), Vitest 3.0.9 (testing), Storybook 8.6.12 (component dev), ESLint/Prettier (linting), Nginx (v1.27.3 for serving static files/SPA). Other: date-fns/Dayjs for dates, geohash/MGRS for coords.
- **Backend**: Java 17/21 (OpenJDK), Spring Boot 3.5.4 as the core framework, with modules for web, security, JPA, and more (detailed above); built on Alpine Linux; Maven for dependency management and builds, with plugins for testing, vulnerability checks (OWASP Dependency-Check), code coverage (JaCoCo), and integration tests.
- **Databases**: PostgreSQL (latest for Keycloak DB), PostGIS (PostgreSQL with GIS extensions for spatial data).
- **Authentication/IAM**: Keycloak (v25.0.4) with JDBC PostgreSQL driver, supporting OpenID Connect/OAuth2/SAML; frontend OIDC integration.
- **AWS Emulation**: LocalStack (emulates S3, potentially others; uses Boto3/AWS SDK internally).
- **Database Admin**: pgAdmin4 (web UI for SQL querying/schema management).
- **Reverse Proxy**: Nginx (custom config for routing, CSP headers).
- **Security Emulator**: Custom script (likely Python/Node with AWS SDK) for GuardDuty-like tagging on S3.
- **Other**: Alpine Linux (lightweight base for images), Environment variables/files for config, Health checks (bash-based), Volumes/Networks for persistence and isolation. Backend-specific: PDFBox/Tesseract for document processing, AWS SDK for S3, Liquibase for DB migrations.

### How It May Be Used and What It Is Used For

- **Primary Use**: Local development/testing of a secure, data-driven web app (e.g., GIS/mapping tool with user auth, file uploads/scans, document OCR/PDF processing, and interactive UI via React).
- **Deployment Scenarios**:
  - Development: Run locally to iterate on code without cloud dependencies.
  - Testing: Simulate production with AWS emulation for integration tests.
  - CI/CD: Extend to pipelines for building/testing images.
- **Specific Use Cases**:
  - **Geospatial Applications**: Store/query spatial data (e.g., maps, locations) using PostGIS, with backend JPA for queries and frontend Leaflet/OpenLayers for visualization.
  - **Secure APIs**: Backend APIs protected by Keycloak for role-based access, with frontend OIDC for token handling.
  - **File Management**: Upload files to emulated S3, auto-scan for malware via GuardDuty emulator, process PDFs/images with OCR.
  - **Admin Tasks**: Use pgAdmin for DB debugging, Keycloak admin UI for user/realm management.
  - **Proxying**: Nginx for load balancing or SSL termination in front of services.
- **Potential Extensions**: Scale to Kubernetes for production; integrate real AWS by swapping LocalStack env vars.

### Tutorial Information

To set up and run:
1. **Prerequisites**: Install Docker and Docker Compose. Create a `.env` file with vars like `POSTGRES_USER=postgres`, `KEYCLOAK_ADMIN_USERNAME=admin`, etc. (copy from sample if available). For backend builds, ensure Maven is available if building outside Docker. For frontend, install Yarn/NPM.
2. **Build and Run**: In `./web-ui`, run `yarn install` then `yarn build` for frontend assets; overall: `docker compose up --build` (rebuilds images, including Vite build for frontend and Maven for backend). Use `-d` for detached mode.
3. **Access Services**:
   - Frontend: http://localhost:3000/appdemo (interact with maps, tables; auth redirects to Keycloak).
   - Backend API: http://localhost:8080 (e.g., `/actuator/health` for status; `/swagger-ui.html` for docs).
   - Keycloak Admin: http://localhost:8081/auth (login with admin creds).
   - pgAdmin: http://localhost:8083 (add servers for appdemo-db: host `appdemo-db`, port 5432).
   - LocalStack S3: Use AWS CLI with `--endpoint-url http://localhost:4566`.
4. **Debugging**: `docker compose logs <service>`; for Keycloak export, edit command and restart. For backend, attach debugger on port 9090/9443. For frontend, `yarn dev` locally for HMR.
5. **Customization**: Override images via env vars (e.g., `export FRONTEND_BUILDER_BASE_IMAGE=node:18-alpine; docker compose up`). For Java 21: Activate profile in POM and rebuild. Update React deps via `yarn add <pkg>`.
6. **Teardown**: `docker compose down -v` (removes volumes).
7. **Common Issues**: On M1/M4 Macs, ensure Rosetta for amd64 emulation. If builds fail, check Dockerfiles in contexts (e.g., `./web-ui/Dockerfile`) or Maven dependencies (run `mvn dependency:tree` locally). Vulnerability scans via `mvn dependency-check:check`. For frontend, check browserlist for compatibility.
8. **Migrations**: Uncomment init SQL in appdemo-db for schema setup; use Liquibase in backend for automated changes (e.g., `mvn liquibase:update`). For frontend, `yarn lint-fix` to auto-fix code.

### Design Architecture Document

#### High-Level Architecture
The system follows a microservices-like architecture with separation of concerns:
- **Presentation Layer**: Frontend (React/Vite/MUI) → Serves interactive UI with maps, tables, auth; communicates with backend via API (Axios).
- **Application Layer**: Backend (Spring Boot/Java) → Handles business logic, APIs, document processing; depends on DB and auth.
- **Data Layer**: appdemo-db (PostGIS) for app data; appdemo-kc-db (PostgreSQL) for auth data.
- **Security Layer**: Keycloak → Central auth server (OIDC integration with frontend); GuardDuty emulator → Scans S3 uploads.
- **Infrastructure Layer**: LocalStack → AWS mocks; Nginx → Proxy/gateway; pgAdmin → DB tooling.

#### Component Diagram
- **User → Nginx (Proxy) → Frontend/Backend**
- **Frontend ↔ Backend** (via shared static volume and API calls)
- **Frontend → Keycloak** (OIDC for auth)
- **Backend → appdemo-db** (JDBC/JPA for data)
- **Backend → Keycloak** (OAuth for auth)
- **Keycloak → appdemo-kc-db** (JDBC)
- **Backend/GuardDuty → LocalStack** (AWS SDK for S3)
- **Admin → pgAdmin** (for DB access)

#### Data Flow
1. User authenticates via Keycloak (OIDC redirect from frontend).
2. Authenticated requests hit backend APIs (secured with Spring Security).
3. Backend queries PostGIS DB for data (e.g., spatial queries via JPA).
4. File uploads go to S3 (LocalStack), triggering GuardDuty scan/tags; backend processes with PDFBox/Tesseract for OCR.
5. Frontend renders data (e.g., maps with Leaflet, tables with MUI).
6. Static assets shared between frontend/backend.

#### Scalability/Security Considerations
- **Scalability**: Add replicas for backend/frontend; use real AWS in prod. Spring Boot supports clustering; React's component model aids modular scaling.
- **Security**: Env vars for secrets; Keycloak/Spring Security for fine-grained auth; CSP in Nginx; OWASP checks in Maven for vulns; updated deps (e.g., Jackson/Netty in backend, resolutions in frontend package.json) to fix CVEs. Frontend uses secure auth flows.
- **Monitoring**: Keycloak health checks; Spring Actuator for metrics (e.g., `/actuator/prometheus`); add Prometheus via exposed ports.
- **Deployment**: For prod, remove dev flags (e.g., Keycloak's `start-dev`), use orchestrators like Swarm/K8s. Build with `mvn clean package` for backend JAR, `yarn build` for frontend, deploy via Docker.
