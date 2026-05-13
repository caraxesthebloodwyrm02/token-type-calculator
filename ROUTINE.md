# 5-Day Muscle Memory Routine: API & Data Operations

**Core Discipline: Autocomplete Muscle Memory**
*The 2006 rule of thumb: "The compiler is your first line of defense; the IDE is your navigator."*
1. **The Shape First:** Always type the interface/class signature before implementing it.
2. **The Pause:** Type 3-4 letters of a variable, method, or payload key. **Pause for 300ms.**
3. **The Scan & Trigger:** Look at the ghost text. If it aligns with your locked scope, press `Tab` or `→`.
4. **The Verification:** Never trust blindly. Check that the types and properties match the contract.

---

## Day 1: Architecture, Scope Lock, & The Data Contract (Design)
*Focus: Design governs the project. No coding until the API contract is written and locked.*
* **09:00 - 10:00**: **Scope Lock & Requirements**. Define the exact API boundaries. Put this in `DESIGN.md`. 
* **10:00 - 11:30**: **Interface Definition (The Contract)**. Write the API payload schemas using Pydantic/Typescript interfaces. *(Drill: Let the IDE predict the types).*
* **11:30 - 13:00**: **Response Structure Design**. Map out success (200 OK) and failure (400 Bad Request) structures.
* **13:00 - 14:00**: *Lunch.*
* **14:00 - 16:00**: **Mocking the Endpoints**. Create empty route handlers that only return hardcoded JSON matching the design. *(Drill: Type `def compute(` and let autocomplete suggest the payload).*
* **16:00 - 17:00**: **Review**. Verify the mock API perfectly matches the `DESIGN.md` contract. **Lock the scope. No new features after this hour.**

// Evening Journal & Reflection: reflecting on the first part of the journey, i was looking at all the lights.. there were rooms and shapes and light and some moments that fed the pain.. the first thing that was a vibe at a time that was there and nothing but dark... and as i sit here now and think of it there could not be a state more full of fuel.. i have been through AZKABAN on a horse with no name it felt good to be out of the rain... in AZKABAN you cant remember your name and there ain't no one there to give you no pain.. la la la...[TAB]

## Day 2: Structured Data Handling & The Dummy API (Operations)
*Focus: Processing API calls safely using strict validation. No database yet.*
* **09:00 - 10:30**: **Parsing the Payload**. Map incoming API JSON to a structured object.
* **10:30 - 12:00**: **Validation Logic**. Write strict `if/else` checks for the data. *(Drill: Type `payload.` and pause. Select properties using arrows).*
* **12:00 - 13:00**: **Data Transformation**. Write a function that takes the valid payload, calculates the `TokenType`, and formats the output.
* **13:00 - 14:00**: *Lunch.*
* **14:00 - 16:00**: **Making the First Calls**. Manually trigger the API (Postman/cURL) with good, bad, and missing data.
* **16:00 - 17:00**: **Metadata Collection Setup**. Add a simple logger or timestamp to the request pipeline.

// Hey, Bob
I'm lookin' at what, uh, Jack was talkin' about
And, uh, it's definitely not a particle that's nearby
It is a, uh, bright object
And it's, uh, obviously rotating because it's flashing
It's, uh, way out in the distance
Currently rotating in a very rhythmic fashion
Because the, uh, flashes come around, uh, almost on time
As we look back at the earth, it's, uh, up at about 11 o'clock
About, uh, well, maybe ten or twelve dianrers—diameters, uh
I don't know whether that does you any good
But there's somethin' out there

## Day 3: State, Storage & Metadata (Processing)
*Focus: Persisting structured data and keeping the system stateful.*
* **09:00 - 10:30**: **Storage Schema Design**. Define how data is saved (JSON file or SQLite). 
* **10:30 - 12:00**: **Writing the Storage Layer**. Create a dedicated module for saving data. *(Drill: Wait for IDE parameter hints on method calls).*
* **12:00 - 13:00**: **Wiring API to Storage**. Connect the API route handler to the storage layer. 
* **13:00 - 14:00**: *Lunch.*
* **14:00 - 16:00**: **Metadata Processing**. Extract headers, simulated IPs, or request duration and save alongside the payload.
* **16:00 - 17:00**: **Testing the Pipeline**. Verify files/DB are writing exactly as the scope intended.

## Day 4: Consuming & Using Data (Making Calls)
*Focus: Client-side operations. You are making the calls.*
* **09:00 - 11:00**: **Building the Client Script**. Write a standalone Python `requests` script to ping your API. 
* **11:00 - 12:30**: **Batch Processing**. Create a loop sending 50 generated scenarios to the API. *(Drill: Let autocomplete build the `for` loop structure).*
* **12:30 - 13:30**: *Lunch.*
* **13:30 - 15:30**: **Reading the Stored Data**. Write a function to read the stored metadata and print a summary report (e.g., "NO-TAKE events counted").
* **15:30 - 17:00**: **Handling Client Errors**. Code the client to gracefully handle 400s/500s.

## Day 5: End-to-End Operations & Muscle Memory Gauntlet (Polish)
*Focus: Drilling the mechanics until natural.*
* **09:00 - 11:00**: **The Tear Down**. Delete the client script and storage layer class entirely.
* **11:00 - 13:00**: **The Rebuild (Muscle Memory Drill)**. Rewrite them from scratch. Rely heavily on Autocomplete and Scope knowledge. Do not look at reference code. Type, pause, Tab, verify.
* **13:00 - 14:00**: *Lunch.*
* **14:00 - 15:30**: **System Integration Test**. Run the rebuilt client. Watch the API process, storage save, and summary print. 
* **15:30 - 17:00**: **Final Review against Design**. Compare the living API against `DESIGN.md`. Document anomalies.
