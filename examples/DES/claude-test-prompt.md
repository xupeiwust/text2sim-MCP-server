# Complex DES Test Prompt for Claude

## 🏭 **Manufacturing Plant Simulation Challenge**

I need you to create a comprehensive discrete-event simulation for a **high-tech electronics manufacturing plant** that produces smartphones. This is a complex multi-stage operation with various challenges that need to be modeled accurately.

### **Business Context**
TechFlow Manufacturing produces premium smartphones with a complex assembly process. They're experiencing bottlenecks and want to optimize their operations. The plant operates 16 hours per day (960 minutes) and needs to understand their current performance and identify improvement opportunities.

### **System Description**

**Production Stages:**
1. **Component Inspection** - Incoming components are inspected for quality
2. **PCB Assembly** - Circuit boards are populated with components  
3. **Display Installation** - Screens are carefully installed
4. **Final Assembly** - All components are assembled into final product
5. **Quality Testing** - Comprehensive testing of finished devices
6. **Packaging** - Products are packaged for shipping

**Product Types:**
- **Standard Model** (60% of production): Regular smartphone, $400 value
- **Pro Model** (30% of production): Enhanced features, $800 value  
- **Premium Model** (10% of production): Top-tier device, $1200 value

**Operational Challenges:**

**Resource Constraints:**
- Component Inspection: 2 stations, can handle any product type
- PCB Assembly: 3 specialized stations, higher-end models take longer
- Display Installation: 2 stations, Premium models require extra care
- Final Assembly: 4 stations, Pro and Premium models are more complex
- Quality Testing: 2 stations, more thorough testing for expensive models
- Packaging: 3 stations, all products package similarly

**Processing Times:**
- Component Inspection: 3-7 minutes for all models
- PCB Assembly: Standard (15-25 min), Pro (20-35 min), Premium (30-45 min)
- Display Installation: Standard (8-12 min), Pro (10-15 min), Premium (15-25 min)
- Final Assembly: Standard (20-30 min), Pro (25-40 min), Premium (35-50 min)
- Quality Testing: Standard (10-15 min), Pro (15-25 min), Premium (20-35 min)
- Packaging: 5-8 minutes for all models

**Quality and Reliability Issues:**
- PCB Assembly station fails every 4-6 hours on average, takes 20-40 minutes to repair
- Quality Testing rejects products 5% of the time, requiring them to return to Final Assembly
- Premium products have priority throughout the system (priority 1)
- Pro products have medium priority (priority 3)  
- Standard products have lowest priority (priority 5)

**Customer Behavior:**
- Orders arrive every 8-15 minutes on average
- If more than 12 orders are waiting at Component Inspection, new orders are cancelled (customer goes to competitor)
- Large orders (Premium products) are more patient, but Standard product customers will cancel if they wait more than 45 minutes in any queue

**Business Metrics Needed:**
- Track orders received, products completed, and orders cancelled
- Calculate total production value and average value per completed product
- Monitor station utilization rates
- Measure processing efficiency (completed vs received orders)

### **Your Task**

Create a complete discrete-event simulation configuration that models this complex manufacturing system. The simulation should:

1. **Accurately model all production stages** with appropriate processing times
2. **Handle different product types** with varying complexity and priority
3. **Include realistic failure scenarios** for equipment breakdowns
4. **Model customer behavior** including order cancellations and patience
5. **Track comprehensive business metrics** for operational analysis
6. **Account for priority-based processing** throughout the system
7. **Include quality control feedback loops** for rejected products

**Expected Deliverables:**
- Complete simulation configuration using the DES tool
- Brief analysis of the results explaining what the simulation reveals about the manufacturing process
- Recommendations for operational improvements based on the simulation outcomes

**Bonus Challenge:**
If the initial results show bottlenecks or inefficiencies, suggest and test configuration changes that could improve overall system performance.

---

*This scenario tests Claude's ability to:*
- *Handle complex multi-stage processes with conditional routing*
- *Manage multiple entity types with different processing requirements*
- *Implement priority-based processing with preemption*
- *Model realistic failure scenarios and feedback loops*
- *Configure comprehensive business metrics and KPIs*
- *Analyze simulation results and provide business insights*
