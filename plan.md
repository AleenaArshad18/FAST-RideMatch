# FAST RideMatch Deliverable 4 Plan

## Reconstructed Cycle 1 (from verifiable Git history)

The following Cycle 1 items are reconstructed from repository commits and merged pull requests dated 2026-11-24 and 2026-11-28. They are evidence-based, not first-hand prompt reconstruction.

- S02 Passenger Ride Discovery was implemented in backend and frontend commits:
  - `c6a7c56 Aleeza Cycle 1 Slice S02: Passenger Ride Discovery`
  - `d6ca67b` and merge `da9b078`
- S04 Driver Request Management backend was implemented by commit
  - `b2039f7 Implement S04 driver request management backend`
  - merged as `156cbc6`
- Existing Cycle 1 backend and frontend foundations include SQLite ride listings,
  passenger discovery filters, driver reliability, and the S04 request gateway contract.

## Cycle 2 / S05 - Passenger Request Workflow

### Completed

- Added persistent SQLite `ride_requests` storage.
- Added passenger request submission and passenger request history/detail APIs.
- Reused the existing S04 `DriverRequestResponse` fields and `RequestStatus` values.
- Added validation for:
  - missing rides
  - inactive/cancelled/completed rides
  - unavailable rides
  - requesting one's own ride
  - duplicate pending requests
- Added a database partial unique index for one pending request per passenger per ride.
- Added a visible "Request Ride" action and success/loading/error feedback to Explore ride cards.
- Added S05 backend tests covering the required success and rejection cases.
- Added the minimal CSS module declaration required by the frontend TypeScript setup.

### Remaining at S05 completion

- Connect passenger endpoints to a real trusted authentication provider before
  enabling successful passenger submissions. The current backend has no
  authentication/token verifier or source of the authenticated student's ID:
  `require_verified_student` and `require_driver_identity` remain 503
  integration placeholders. The frontend's optional `authToken`/`driverId`
  props are not a backend authentication implementation.
- This work was carried into Cycle 3 / S06 below.

## S05 Verification

- Backend before the authentication follow-up: `81 passed` with
  `python -m pytest -q`.
- Frontend: `npx tsc --noEmit` passed after adding CSS type declarations.
- Authentication follow-up: passenger requests now reject an explicitly
  unverified student with `403` before resolving identity, and remain fail-closed
  with `503` when authentication or passenger identity providers are absent.
  A successful verified-passenger authentication case cannot be tested until
  those providers are implemented.
- Latest complete backend suite after the follow-up: `84 passed, 1 warning`.
- Latest frontend TypeScript check after the follow-up:
  `npx tsc --noEmit` passed.

## Cycle 3 / S06 - Request Validation and Seat Allocation

### Completed

- Connected the existing `RequestGateway` methods to the S05 SQLite
  `ride_requests` table without changing its protocol or
  `DriverRequestResponse` shape.
- Kept the S04 driver request routes and service layer as the API boundary.
  Drivers can list only their requests and accept/reject only requests owned
  by their driver ID.
- Decision processing now rechecks request ownership and `pending` status inside
  a SQLite `BEGIN IMMEDIATE` transaction.
- Acceptance validates the listing exists, belongs to the driver, remains
  active, and has seats available. A conditional update decrements exactly one
  seat and changes the request status in that same transaction; failures roll
  back together.
- Rejection changes only the pending request status and does not change seats.
- SQLite ride listing storage now allows zero seats after the last seat is
  allocated. Existing databases with the former positive-seats-only constraint
  are migrated while preserving listing and request rows.
- Ride-listing response schema accepts zero available seats while create/update
  input validation continues to require a positive seat count.
- Added integration coverage for driver listing, acceptance, rejection,
  unauthorized driver decisions, duplicate decisions, no seats, inactive rides,
  and concurrent acceptance with one remaining seat.
- No frontend files were changed: repository inspection found no driver request
  screen or S04 request UI in this checkout, and the prompt identified pending
  teammate ownership. The existing screen ownership was left untouched.

### Remaining Dependencies

- Authentication is still not implemented in the repository. S04's
  `require_verified_student` and `require_driver_identity` remain fail-closed
  503 integration points. S06 does not accept client-supplied driver IDs or
  claim to authenticate a driver; actual endpoints need the team's trusted
  verified-student identity provider.
- Driver request UI remains outside this change because no existing owned
  implementation was present to integrate without conflicting with teammate
  work.

### S06 Verification

- Complete backend suite: `93 passed, 1 warning` with
  `python -m pytest -q`.
- Frontend TypeScript: `npx tsc --noEmit` passed.
- The one warning is the existing Starlette deprecation notice about using
  `httpx` with `starlette.testclient` and recommending `httpx2`.
