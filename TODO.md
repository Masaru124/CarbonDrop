
# TODO: Implement "What-if Simulator" Feature

## Backend Changes
- [x] Extend backend/app/footprint.py to add simulation logic for scenarios (e.g., replace meat meals, change transport modes)
- [x] Add new API endpoint in backend/app/main.py for "What-if Simulator" that accepts scenarios and returns simulated results

## Frontend Changes
- [x] Create new React component app/src/components/WhatIfSimulator.jsx for user input and displaying simulation results
- [x] Create dedicated Simulator page (app/src/components/Simulator.jsx) for better organization
- [x] Add new route "/simulator" in App.jsx
- [x] Update navbar to link to the dedicated simulator page
- [x] Remove simulator from dashboard for cleaner separation

## Testing
- [x] Test the What-if Simulator feature end-to-end to ensure backend and frontend work together correctly
- [x] Test the updated virtual tree planting feature with automatic calculation based on carbon footprint

## Virtual Offset System (New Feature)
- [x] Create user_offsets table in database models
- [x] Add offset conversion logic (1 tree = 21 kg CO2/year)
- [x] Create API endpoints for planting virtual trees and viewing offsets
- [x] Add offset planting UI to the simulator page
- [x] Update dashboard to show offset progress and virtual forest
- [x] Add gamification elements (badges, levels, progress tracking)
- [x] Integrate offset visualization with existing carbon footprint data
