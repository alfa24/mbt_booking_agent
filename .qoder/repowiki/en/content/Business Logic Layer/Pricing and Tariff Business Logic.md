# Pricing and Tariff Business Logic

<cite>
**Referenced Files in This Document**
- [tariff.py](file://backend/models/tariff.py)
- [tariff.py](file://backend/services/tariff.py)
- [tariff.py](file://backend/repositories/tariff.py)
- [tariff.py](file://backend/schemas/tariff.py)
- [tariffs.py](file://backend/api/tariffs.py)
- [booking.py](file://backend/models/booking.py)
- [booking.py](file://backend/services/booking.py)
- [booking.py](file://backend/schemas/booking.py)
- [house.py](file://backend/models/house.py)
- [house.py](file://backend/services/house.py)
- [exceptions.py](file://backend/exceptions.py)
- [test_tariffs.py](file://backend/tests/test_tariffs.py)
- [test_bookings.py](file://backend/tests/test_bookings.py)
- [database.py](file://backend/database.py)
- [main.py](file://backend/main.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document explains the pricing and tariff business logic implemented in the system. It focuses on how tariffs are managed, how prices are calculated for bookings, and how the system integrates with houses for availability and with users for authorization. It also documents business rules, validation constraints, and error handling for pricing scenarios such as free tariffs, multiple guest categories, and date conflicts.

## Project Structure
The pricing and tariff logic spans models, repositories, services, schemas, and API endpoints for tariffs and bookings, plus house availability and shared exceptions.

```mermaid
graph TB
subgraph "Tariff Domain"
TModel["Tariff Model<br/>backend/models/tariff.py"]
TSvc["Tariff Service<br/>backend/services/tariff.py"]
TRepo["Tariff Repository<br/>backend/repositories/tariff.py"]
TSch["Tariff Schemas<br/>backend/schemas/tariff.py"]
TApi["Tariff API<br/>backend/api/tariffs.py"]
end
subgraph "Booking Domain"
BModel["Booking Model<br/>backend/models/booking.py"]
BSvc["Booking Service<br/>backend/services/booking.py"]
BSch["Booking Schemas<br/>backend/schemas/booking.py"]
end
subgraph "House Domain"
HModel["House Model<br/>backend/models/house.py"]
HSvc["House Service<br/>backend/services/house.py"]
end
subgraph "Shared"
DB["Database Session<br/>backend/database.py"]
EX["Exceptions<br/>backend/exceptions.py"]
APP["FastAPI App & Handlers<br/>backend/main.py"]
end
TApi --> TSvc
TSvc --> TRepo
TRepo --> DB
TModel --> TRepo
BSvc --> TRepo
BSvc --> BModel
BModel --> DB
HSvc --> BModel
HSvc --> DB
APP --> TApi
APP --> BSvc
APP --> HSvc
APP --> EX
```

**Diagram sources**
- [tariff.py:9-21](file://backend/models/tariff.py#L9-L21)
- [tariff.py:32-144](file://backend/services/tariff.py#L32-L144)
- [tariff.py:12-151](file://backend/repositories/tariff.py#L12-L151)
- [tariff.py:9-54](file://backend/schemas/tariff.py#L9-L54)
- [tariffs.py:1-187](file://backend/api/tariffs.py#L1-L187)
- [booking.py:20-41](file://backend/models/booking.py#L20-L41)
- [booking.py:57-322](file://backend/services/booking.py#L57-L322)
- [booking.py:25-133](file://backend/schemas/booking.py#L25-L133)
- [house.py:9-24](file://backend/models/house.py#L9-L24)
- [house.py:51-253](file://backend/services/house.py#L51-L253)
- [database.py:26-41](file://backend/database.py#L26-L41)
- [main.py:59-173](file://backend/main.py#L59-L173)

**Section sources**
- [tariff.py:1-21](file://backend/models/tariff.py#L1-L21)
- [tariff.py:1-144](file://backend/services/tariff.py#L1-L144)
- [tariff.py:1-151](file://backend/repositories/tariff.py#L1-L151)
- [tariff.py:1-54](file://backend/schemas/tariff.py#L1-L54)
- [tariffs.py:1-187](file://backend/api/tariffs.py#L1-L187)
- [booking.py:1-41](file://backend/models/booking.py#L1-L41)
- [booking.py:1-322](file://backend/services/booking.py#L1-L322)
- [booking.py:1-133](file://backend/schemas/booking.py#L1-L133)
- [house.py:1-24](file://backend/models/house.py#L1-L24)
- [house.py:1-253](file://backend/services/house.py#L1-L253)
- [database.py:1-41](file://backend/database.py#L1-L41)
- [main.py:1-173](file://backend/main.py#L1-L173)

## Core Components
- Tariff model and repository: Store and manage pricing tiers (name and amount per night).
- Tariff service: Implements CRUD operations with validation and error handling.
- Booking service: Calculates total price from guest composition using tariff rates and enforces date conflict checks.
- House service: Provides availability calendars based on bookings.
- Shared exceptions: Centralized domain errors surfaced to clients.

Key business rules:
- Tariff amount is stored as integer “rubles per night,” with zero enabling free pricing.
- Booking total amount equals sum over guests of (tariff.amount × count).
- Date validation ensures check-in precedes check-out.
- Date conflict validation prevents overlapping stays for the same house.

**Section sources**
- [tariff.py:9-21](file://backend/models/tariff.py#L9-L21)
- [tariff.py:23-41](file://backend/repositories/tariff.py#L23-L41)
- [tariff.py:49-144](file://backend/services/tariff.py#L49-L144)
- [tariff.py:9-54](file://backend/schemas/tariff.py#L9-L54)
- [booking.py:108-170](file://backend/services/booking.py#L108-L170)
- [booking.py:70-108](file://backend/schemas/booking.py#L70-L108)
- [house.py:207-253](file://backend/services/house.py#L207-L253)
- [exceptions.py:76-82](file://backend/exceptions.py#L76-L82)

## Architecture Overview
The system separates concerns across layers:
- API layer exposes endpoints for tariffs and bookings.
- Service layer encapsulates business logic and orchestrates repositories.
- Repository layer handles persistence with SQLAlchemy async sessions.
- Models define the schema and relationships.
- Exceptions unify error responses.

```mermaid
sequenceDiagram
participant Client as "Client"
participant API as "Tariff API"
participant Svc as "Tariff Service"
participant Repo as "Tariff Repository"
participant DB as "Database"
Client->>API : POST /api/v1/tariffs
API->>Svc : create_tariff(request)
Svc->>Repo : create(name, amount)
Repo->>DB : INSERT INTO tariffs
DB-->>Repo : new tariff row
Repo-->>Svc : TariffResponse
Svc-->>API : TariffResponse
API-->>Client : 201 TariffResponse
```

**Diagram sources**
- [tariffs.py:101-117](file://backend/api/tariffs.py#L101-L117)
- [tariff.py:49-61](file://backend/services/tariff.py#L49-L61)
- [tariff.py:23-41](file://backend/repositories/tariff.py#L23-L41)

**Section sources**
- [tariffs.py:1-187](file://backend/api/tariffs.py#L1-L187)
- [tariff.py:1-144](file://backend/services/tariff.py#L1-L144)
- [tariff.py:1-151](file://backend/repositories/tariff.py#L1-L151)
- [database.py:26-41](file://backend/database.py#L26-L41)

## Detailed Component Analysis

### Tariff Management
Tariff management covers creation, retrieval, listing, updates, and deletion. The service validates presence before updates/deletes and raises a domain-specific error if missing.

```mermaid
classDiagram
class TariffModel {
+int id
+string name
+int amount
+datetime created_at
}
class TariffRepository {
+create(name, amount) TariffResponse
+get(tariff_id) TariffResponse?
+get_all(limit, offset, sort) (TariffResponse[], int)
+update(tariff_id, name?, amount?) TariffResponse?
+delete(tariff_id) bool
}
class TariffService {
+create_tariff(request) TariffResponse
+get_tariff(tariff_id) TariffResponse
+list_tariffs(limit, offset, sort) (TariffResponse[], int)
+update_tariff(tariff_id, request) TariffResponse
+delete_tariff(tariff_id) void
}
TariffService --> TariffRepository : "uses"
TariffRepository --> TariffModel : "persists"
```

**Diagram sources**
- [tariff.py:9-21](file://backend/models/tariff.py#L9-L21)
- [tariff.py:12-151](file://backend/repositories/tariff.py#L12-L151)
- [tariff.py:32-144](file://backend/services/tariff.py#L32-L144)

Business rules and validations:
- Name length and amount constraints enforced by Pydantic schemas.
- Amount must be non-negative; free tariffs are supported by amount=0.
- Listing supports pagination and sorting by any model field.

**Section sources**
- [tariff.py:9-54](file://backend/schemas/tariff.py#L9-L54)
- [tariff.py:49-144](file://backend/services/tariff.py#L49-L144)
- [tariff.py:23-151](file://backend/repositories/tariff.py#L23-L151)
- [tariffs.py:18-187](file://backend/api/tariffs.py#L18-L187)

### Booking Price Calculation Workflow
The booking service calculates the total amount by summing the product of each guest group’s tariff rate and count. It fetches the current tariff amount from the database for accuracy.

```mermaid
sequenceDiagram
participant Client as "Client"
participant API as "Booking API"
participant B as "Booking Service"
participant TR as "Tariff Repository"
participant BR as "Booking Repository"
participant DB as "Database"
Client->>API : POST /api/v1/bookings
API->>B : create_booking(tenant_id, request)
B->>B : _check_date_conflicts(house_id, check_in, check_out)
B->>TR : get(tariff_id) for each guest
TR->>DB : SELECT tariffs WHERE id=?
DB-->>TR : Tariff or NULL
TR-->>B : TariffResponse or None
B->>B : _calculate_amount(guests) = Σ(count * rate)
B->>BR : create(house_id, tenant_id, dates, guests, total_amount)
BR->>DB : INSERT INTO bookings
DB-->>BR : new booking row
BR-->>B : BookingResponse
B-->>API : BookingResponse
API-->>Client : 201 BookingResponse
```

**Diagram sources**
- [booking.py:127-170](file://backend/services/booking.py#L127-L170)
- [booking.py:78-126](file://backend/services/booking.py#L78-L126)
- [booking.py:43-56](file://backend/repositories/tariff.py#L43-L56)
- [booking.py:20-41](file://backend/models/booking.py#L20-L41)

Pricing calculation logic:
- For each guest group, fetch the tariff by ID and multiply by the count.
- If a tariff is missing, its contribution is treated as zero in the current implementation.
- Duration is not part of the calculation; total amount reflects nightly rates multiplied by guest counts.

**Section sources**
- [booking.py:108-170](file://backend/services/booking.py#L108-L170)
- [booking.py:25-88](file://backend/schemas/booking.py#L25-L88)
- [booking.py:20-41](file://backend/models/booking.py#L20-L41)

### House Availability and Tariff Relationship
House availability is derived from bookings. While house pricing is not modeled in the current schema, the house service aggregates occupied date ranges for a given property, which indirectly informs pricing decisions by preventing double-booking.

```mermaid
flowchart TD
Start(["Get House Calendar"]) --> LoadHouse["Load House by ID"]
LoadHouse --> NotFound{"House exists?"}
NotFound --> |No| RaiseHouseNotFound["Raise HouseNotFoundError"]
NotFound --> |Yes| FetchBookings["Fetch bookings for house (exclude cancelled)"]
FetchBookings --> FilterDates["Optionally filter by date range"]
FilterDates --> BuildRanges["Build OccupiedDateRange list"]
BuildRanges --> ReturnCal["Return HouseCalendarResponse"]
RaiseHouseNotFound --> End(["Exit"])
ReturnCal --> End
```

**Diagram sources**
- [house.py:207-253](file://backend/services/house.py#L207-L253)
- [exceptions.py:60-66](file://backend/exceptions.py#L60-L66)

**Section sources**
- [house.py:9-24](file://backend/models/house.py#L9-L24)
- [house.py:207-253](file://backend/services/house.py#L207-L253)
- [exceptions.py:60-66](file://backend/exceptions.py#L60-L66)

### API Endpoints and Error Handling
Endpoints expose CRUD operations for tariffs and integrate with centralized exception handlers that convert domain errors into standardized JSON responses.

```mermaid
sequenceDiagram
participant Client as "Client"
participant API as "Tariff API"
participant Svc as "Tariff Service"
participant Repo as "Tariff Repository"
participant DB as "Database"
participant App as "FastAPI App"
Client->>API : PATCH /api/v1/tariffs/{id}
API->>Svc : update_tariff(id, request)
Svc->>Repo : get(id)
Repo->>DB : SELECT tariffs WHERE id=?
DB-->>Repo : Tariff or NULL
Repo-->>Svc : TariffResponse or None
alt Not Found
Svc-->>API : raise TariffNotFoundError
API-->>App : propagate exception
App-->>Client : 404 ErrorResponse
else Found
Svc->>Repo : update(id, name?, amount?)
Repo->>DB : UPDATE tariffs SET ...
DB-->>Repo : OK
Repo-->>Svc : TariffResponse
Svc-->>API : TariffResponse
API-->>Client : 200 TariffResponse
end
```

**Diagram sources**
- [tariffs.py:137-157](file://backend/api/tariffs.py#L137-L157)
- [tariff.py:102-128](file://backend/services/tariff.py#L102-L128)
- [tariff.py:101-131](file://backend/repositories/tariff.py#L101-L131)
- [exceptions.py:76-82](file://backend/exceptions.py#L76-L82)
- [main.py:145-153](file://backend/main.py#L145-L153)

**Section sources**
- [tariffs.py:1-187](file://backend/api/tariffs.py#L1-L187)
- [tariff.py:102-128](file://backend/services/tariff.py#L102-L128)
- [tariff.py:101-131](file://backend/repositories/tariff.py#L101-L131)
- [exceptions.py:76-82](file://backend/exceptions.py#L76-L82)
- [main.py:145-153](file://backend/main.py#L145-L153)

## Dependency Analysis
- Tariff API depends on Tariff Service.
- Tariff Service depends on Tariff Repository and Pydantic schemas.
- Booking Service depends on Tariff Repository and Booking Repository; it orchestrates price calculation.
- House Service depends on Booking Repository to build availability calendars.
- FastAPI app registers routers and exception handlers globally.

```mermaid
graph LR
TA["Tariff API"] --> TS["Tariff Service"]
TS --> TR["Tariff Repository"]
TR --> M["Tariff Model"]
BA["Booking API"] --> BS["Booking Service"]
BS --> BR["Booking Repository"]
BS --> TR
BR --> BM["Booking Model"]
HA["House API"] --> HS["House Service"]
HS --> BR
HS --> HM["House Model"]
APP["FastAPI App"] --> TA
APP --> BA
APP --> HA
APP --> EX["Exceptions"]
```

**Diagram sources**
- [tariffs.py:1-187](file://backend/api/tariffs.py#L1-L187)
- [tariff.py:32-144](file://backend/services/tariff.py#L32-L144)
- [tariff.py:12-151](file://backend/repositories/tariff.py#L12-L151)
- [tariff.py:9-21](file://backend/models/tariff.py#L9-L21)
- [booking.py:57-322](file://backend/services/booking.py#L57-L322)
- [booking.py:20-41](file://backend/models/booking.py#L20-L41)
- [house.py:51-253](file://backend/services/house.py#L51-L253)
- [house.py:9-24](file://backend/models/house.py#L9-L24)
- [main.py:59-173](file://backend/main.py#L59-L173)

**Section sources**
- [tariffs.py:1-187](file://backend/api/tariffs.py#L1-L187)
- [tariff.py:32-144](file://backend/services/tariff.py#L32-L144)
- [tariff.py:12-151](file://backend/repositories/tariff.py#L12-L151)
- [booking.py:57-322](file://backend/services/booking.py#L57-L322)
- [house.py:51-253](file://backend/services/house.py#L51-L253)
- [main.py:59-173](file://backend/main.py#L59-L173)

## Performance Considerations
- Tariff lookups in price calculation are O(n) over guest groups; batching or caching could reduce N+1 queries if guest lists grow large.
- Sorting and pagination in tariff listing are handled at the database level, minimizing memory overhead.
- Booking date conflict checks iterate over existing bookings for a house; consider indexing or limiting the search window for very busy properties.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Tariff not found during booking: The service raises a domain error; ensure the tariff exists and the ID is correct.
- Invalid amount on tariff creation/update: Amount must be non-negative; adjust payload accordingly.
- Invalid booking dates: Ensure check-in is strictly before check-out.
- Date conflicts: Overlapping stays for the same house are rejected; adjust dates or house selection.

Validation and error mapping:
- Tariff not found: 404 ErrorResponse with “not_found”.
- Date conflict: 400 ErrorResponse with “date_conflict”.
- Permission errors: 403 ErrorResponse with “forbidden”.
- General internal errors: 500 ErrorResponse with “internal_error”.

**Section sources**
- [exceptions.py:76-82](file://backend/exceptions.py#L76-L82)
- [booking.py:82-107](file://backend/schemas/booking.py#L82-L107)
- [booking.py:78-107](file://backend/services/booking.py#L78-L107)
- [main.py:145-153](file://backend/main.py#L145-L153)

## Conclusion
The system implements a straightforward yet robust tariff and pricing model:
- Tariffs are simple, immutable pricing tiers with non-negative amounts.
- Bookings calculate totals by multiplying nightly rates by guest counts.
- Availability is enforced via date conflict checks.
- Extensibility points exist for richer pricing features (e.g., seasonality, occupancy tiers) by augmenting schemas and services while preserving current validation and error semantics.

[No sources needed since this section summarizes without analyzing specific files]