# System Dynamics Model Prompts for Text2Sim MCP Server

This collection provides example prompts you can use with Claude Desktop (via the Text2Sim MCP Server) to create, validate, and simulate System Dynamics models. Each prompt is designed to demonstrate different aspects of SD modeling and exercise the available MCP tools.

## Urban Population Growth Model

**Complexity:** Intermediate
**Concepts:** Population dynamics, housing markets, feedback loops
**Use Case:** Urban planning, demographic analysis

```
I want to create a System Dynamics model to study urban population growth and its impact on housing demand.

The model should include:

1. **Population Dynamics:**
   - Urban population as a stock that accumulates over time
   - Birth rate and death rate as flows affecting population
   - Migration from rural areas as an additional inflow
   - Initial population of 100,000 people

2. **Housing Market:**
   - Housing stock as another stock (current supply)
   - Housing construction rate as an inflow
   - Housing demolition/depreciation as an outflow
   - Initial housing stock of 40,000 units

3. **Key Relationships:**
   - Birth rate = population × 0.02 (2% annual birth rate)
   - Death rate = population × 0.01 (1% annual death rate)
   - Migration rate = (job_opportunities - housing_pressure) × 0.001
   - Housing construction = housing_demand × construction_capacity
   - Housing demand = population / average_household_size
   - Housing pressure = MAX(0, (housing_demand - housing_stock) / housing_stock)

4. **Parameters:**
   - Average household size: 2.5 people per unit
   - Construction capacity: 0.1 (10% of demand can be built per year)
   - Job opportunities: starts at 1000, grows by 2% annually

Please create this SD model using the Text2Sim system, validate the structure, and then run a 20-year simulation. I'd like to see how population growth affects housing pressure and whether the construction rate can keep up with demand.

After creating the model, please also show me:
- Model validation results
- Key model statistics (components, structure)
- Simulation results for the first few time periods
- Any suggestions for improving the model structure
```

## Supply Chain Resilience Model

**Complexity:** Intermediate-Advanced
**Concepts:** Inventory management, capacity planning, customer satisfaction
**Use Case:** Operations management, supply chain optimization

```
Help me build a System Dynamics model for supply chain resilience analysis:

**Core Stocks:**
- Inventory level (starting at 1000 units)
- Supplier capacity (starting at 500 units/month)
- Customer satisfaction (starting at 0.8 or 80%)

**Key Flows:**
- Production rate (inflow to inventory)
- Sales rate (outflow from inventory)
- Capacity investment (inflow to supplier capacity)
- Capacity depreciation (outflow from supplier capacity)
- Satisfaction change rate (can be positive or negative)

**Model Logic:**
- Production rate = MIN(supplier_capacity, target_production)
- Sales rate = MIN(inventory, customer_demand)
- Target production = customer_demand + inventory_adjustment
- Inventory adjustment = (desired_inventory - inventory) × 0.2
- Desired inventory = customer_demand × safety_stock_weeks
- Customer demand = base_demand × demand_multiplier
- Capacity investment = capacity_gap × investment_rate
- Customer satisfaction changes based on service level
- Service level = sales_rate / customer_demand

**Parameters:**
- Base demand: 400 units/month
- Safety stock: 4 weeks
- Investment rate: 0.15
- Capacity depreciation rate: 0.05

Create this model, validate it, and simulate for 24 months. I want to see how the system responds to a demand shock (50% increase) at month 6. Show me the model structure, validation results, and simulation output focusing on inventory levels and customer satisfaction over time.
```

## Simple Savings Account Model

**Complexity:** Beginner
**Concepts:** Basic stocks and flows, compound interest
**Use Case:** Personal finance, educational introduction to SD

```
I'm new to System Dynamics. Can you help me create a simple model of a savings account?

The model should have:
- A stock called "savings_balance" starting at $1000
- Monthly deposits as an inflow ($200 per month)
- Monthly expenses as an outflow ($150 per month)
- Interest earned as another inflow (2% annual rate, so about 0.167% monthly)

Please:
1. Create this SD model using the available tools
2. Validate the model structure
3. Run a 12-month simulation
4. Show me the results and explain what's happening

Also, can you suggest ways to make this model more realistic?
```

## Epidemic Model (SIR with Extensions)

**Complexity:** Advanced
**Concepts:** Compartmental modeling, nonlinear dynamics, policy analysis
**Use Case:** Public health, epidemiology, policy planning

```
Create a sophisticated System Dynamics model of disease spread (SIR model with additional complexity):

**Population Stocks:**
- Susceptible population (S) - starts at 999,000
- Infected population (I) - starts at 1,000
- Recovered population (R) - starts at 0
- Vaccinated population (V) - starts at 0

**Flow Structure:**
- Infection rate: S → I
- Recovery rate: I → R
- Vaccination rate: S → V
- Possible reinfection: R → S (for some diseases)

**Model Equations:**
- Infection rate = (S × I × transmission_rate) / total_population
- Recovery rate = I × recovery_rate_constant
- Vaccination rate = S × vaccination_coverage × vaccination_speed
- Reinfection rate = R × immunity_loss_rate
- Total population = S + I + R + V

**Parameters:**
- Transmission rate: 0.0003 (contacts per person per day)
- Recovery rate constant: 0.1 (average 10-day recovery)
- Vaccination speed: 0.01 (1% of susceptible vaccinated daily)
- Vaccination coverage: 0.8 (80% willing to vaccinate)
- Immunity loss rate: 0.002 (immunity lasts ~500 days average)

Build this model, validate its structure, and simulate for 365 days. I want to analyze:
1. Peak infection timing and magnitude
2. Final attack rate (% of population infected)
3. Impact of vaccination on outbreak dynamics
4. Effectiveness of different intervention timing

Please also suggest model improvements and extensions.
```

## Technology Adoption Model

**Complexity:** Intermediate
**Concepts:** Diffusion processes, network effects, market dynamics
**Use Case:** Innovation management, market analysis

```
Build a System Dynamics model of technology adoption in a market:

**Core Stocks:**
- Non-adopters (potential customers) - starts at 10,000
- Adopters (current users) - starts at 100
- Total market awareness - starts at 0.1 (10% aware)

**Key Flows:**
- Adoption rate: Non-adopters → Adopters
- Awareness spreading rate (increases market awareness)
- Churn rate: Adopters → Non-adopters (some abandon the technology)

**Model Logic:**
- Adoption rate = non_adopters × adoption_probability × awareness_level
- Adoption probability = base_adoption_rate + network_effect + price_effect
- Network effect = (adopters / total_market) × network_strength
- Price effect = (reference_price - current_price) / reference_price × price_sensitivity
- Awareness spreading = (adopters × word_of_mouth_rate) + marketing_effect
- Churn rate = adopters × churn_probability

**Parameters:**
- Base adoption rate: 0.02 (2% monthly for aware non-adopters)
- Network strength: 0.5 (strong network effects)
- Price sensitivity: 0.3
- Reference price: $100
- Current price: $80
- Word of mouth rate: 0.05
- Marketing budget: $1000/month
- Churn probability: 0.01 (1% monthly)

Create this model, validate it, and simulate for 36 months. I want to understand:
1. How quickly the technology spreads
2. The impact of network effects on adoption
3. Market saturation timing
4. Sensitivity to price changes

Show validation results and suggest model enhancements.
```

## Organizational Learning Model

**Complexity:** Advanced
**Concepts:** Learning curves, knowledge retention, capability building
**Use Case:** Organizational development, training effectiveness

```
Create a System Dynamics model of organizational learning and capability development:

**Knowledge Stocks:**
- Individual knowledge (average per person) - starts at 50 units
- Organizational knowledge (stored in systems/processes) - starts at 100 units
- Team collaboration effectiveness - starts at 0.6 (60%)

**Learning Flows:**
- Individual learning rate (increases individual knowledge)
- Knowledge sharing rate (individual → organizational)
- Knowledge loss rate (forgetting, turnover)
- Collaboration improvement rate

**Model Relationships:**
- Individual learning = learning_capacity × training_investment × learning_efficiency
- Learning efficiency = base_efficiency + (organizational_knowledge × knowledge_leverage)
- Knowledge sharing = individual_knowledge × sharing_rate × collaboration_effectiveness
- Knowledge loss = (individual_knowledge × turnover_rate) + (organizational_knowledge × forgetting_rate)
- Collaboration improvement = team_interaction_frequency × trust_level - collaboration_decay

**Parameters:**
- Learning capacity: 10 units/month per person
- Training investment: $500/person/month
- Base learning efficiency: 0.1
- Knowledge leverage: 0.001
- Sharing rate: 0.05 (5% of individual knowledge shared monthly)
- Turnover rate: 0.02 (2% monthly)
- Forgetting rate: 0.01 (1% monthly)
- Team interaction frequency: 20 meetings/month
- Trust level: 0.8

Model this system, validate it, and simulate for 24 months. Analyze:
1. Knowledge accumulation patterns
2. Impact of training investment on organizational capability
3. Effect of turnover on knowledge retention
4. ROI of different learning interventions

Provide validation results and improvement suggestions.
```

## Environmental Resource Management

**Complexity:** Intermediate-Advanced
**Concepts:** Resource depletion, sustainability, carrying capacity
**Use Case:** Environmental policy, resource management

```
Develop a System Dynamics model for renewable resource management (e.g., forest):

**Resource Stocks:**
- Forest biomass (tons) - starts at 10,000 tons
- Harvesting equipment capacity - starts at 100 tons/month
- Environmental quality index - starts at 0.8 (80%)

**Resource Flows:**
- Natural growth rate (increases biomass)
- Harvesting rate (decreases biomass)
- Equipment investment (increases capacity)
- Equipment depreciation (decreases capacity)
- Environmental degradation/restoration

**Model Logic:**
- Natural growth = biomass × growth_rate × carrying_capacity_effect × environmental_quality
- Carrying capacity effect = MAX(0, (carrying_capacity - biomass) / carrying_capacity)
- Harvesting rate = MIN(biomass, harvesting_capacity, market_demand)
- Equipment investment = (target_capacity - current_capacity) × investment_rate
- Environmental quality changes based on harvesting pressure vs. regeneration
- Market demand varies with price and external demand

**Parameters:**
- Base growth rate: 0.05 (5% monthly under ideal conditions)
- Carrying capacity: 15,000 tons
- Market demand: 80 tons/month (base level)
- Price elasticity: -0.5
- Investment rate: 0.2
- Equipment depreciation: 0.02 (2% monthly)
- Environmental recovery rate: 0.03

Create this model, validate structure, and run a 60-month simulation. Examine:
1. Sustainable harvesting levels
2. Impact of different harvesting strategies
3. Long-term environmental outcomes
4. Economic vs. environmental trade-offs

Show validation and suggest policy interventions.
```

---

## How to Use These Prompts

### Getting Started
1. **Start Claude Desktop** with the Text2Sim MCP Server running
2. **Copy any prompt** above into your conversation with Claude
3. **Follow the responses** as Claude creates, validates, and simulates your model
4. **Ask follow-up questions** to refine or extend the model

### Expected Workflow
1. **Model Creation** - Claude will use `validate_sd_model` and `get_sd_model_info`
2. **Structure Validation** - Check model components and relationships
3. **Simulation** - Use `simulate_sd` to run the model
4. **Analysis** - Interpret results and suggest improvements
5. **Iteration** - Refine model based on insights

### Tips for Best Results
- **Be specific** about initial values and parameters
- **Request validation** explicitly to catch structural issues
- **Ask for explanations** of model behavior and results
- **Iterate and refine** based on Claude's suggestions
- **Explore scenarios** by changing parameters

### Available MCP Tools
- `simulate_sd` - Run model simulations with parameters
- `validate_sd_model` - Check model structure and schema compliance
- `get_sd_model_info` - Extract model metadata and statistics
- `convert_vensim_to_sd_json` - Convert existing Vensim models

---

## Learning Progression

### Beginner Path
1. Start with **Savings Account Model**
2. Try **Technology Adoption Model**
3. Experiment with **Urban Population Growth**

### Intermediate Path
1. Build **Supply Chain Resilience Model**
2. Create **Environmental Resource Management** model
3. Develop **Organizational Learning Model**

### Advanced Path
1. Implement **Epidemic Model** with policy scenarios
2. Create multi-sector economic models
3. Build complex social system models

Each prompt is designed to teach specific SD concepts while providing practical, real-world applications. Start simple and work your way up to more complex models as you become comfortable with the system!