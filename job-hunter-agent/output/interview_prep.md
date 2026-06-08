```markdown
# Interview Prep: Leaseweb – Senior Golang Developer (Developer Platform Team)

---

## Job Overview
**Role**: Senior Golang Developer – Developer Platform Team  
**Location**: Amsterdam, Netherlands (Hybrid, remote‐friendly)  
**Compensation**: €62,000 – €76,000 per year  
**Team Context**:  
- Part of a 90-engineer Product Engineering organization, working in small Scrum squads  
- Flat structure, high autonomy: end-to-end ownership of APIs and supporting platforms  
- Leaseweb API is the “front door” for all hosting services, powering websites, dashboards, CLI tools, SDKs  

**Key Responsibilities**  
- Architect, implement and review new APIs in Go (and PHP where needed)  
- Build and maintain Terraform plugins & SDKs  
- Design/support tools (authentication platform, abuse platform, CLI)  
- Engage with developer community and represent Leaseweb at events  
- Collaborate across Product, Security, DevOps, Customer Success  

**Must-Have Qualifications**  
- 5+ years software development (strong preference: Golang)  
- API design & implementation experience  
- Linux & Git expertise, experience with Agile/Scrum  
- Familiarity with Terraform plugin model & OAuth2 protocol (advantage)  

---

## Why This Job Is a Fit
1. **API-First Mindset**  
   - You’ve built and scaled RESTful & GraphQL APIs in Node.js/Python, serving 10k+ daily users.  
   - Your history of designing microservices maps directly to building market-leading APIs in Go.

2. **Security & Authentication**  
   - You integrated OAuth2 flows and JWT-based auth in past roles—core to Leaseweb’s authentication platform.

3. **DevOps & Reliability Culture**  
   - Docker, CI/CD pipelines and Linux administration are second nature to you.  
   - You understand “you build it, you run it,” aligning with Leaseweb’s “build and operate” squads.

4. **Agile Collaboration**  
   - Proven track record working in Scrum, leading retrospectives, mentoring peers—mirrors Leaseweb’s remote-first, cross-functional ethos.

5. **Growth & Learning**  
   - Although your production Go experience is limited, you have demonstrated rapid language uptake (Python → Node.js) and hold AWS and React certifications—showing adaptability.

---

## Resume Highlights for This Role
- **API Development & Microservices**  
  • Architected RESTful services in Node.js/Express, optimized PostgreSQL schemas (30% faster).  
  • Built GraphQL endpoints and secured them with OAuth2 and role-based access.

- **DevOps & Automation**  
  • Containerized microservices (Docker) and automated CI/CD (GitHub Actions), reducing releases by 40%.  
  • Managed Linux servers (Ubuntu/CentOS), troubleshooting and performance tuning.

- **Cloud & Infrastructure as Code**  
  • Deployed applications on AWS (EC2, S3, Lambda).  
  • Familiar with writing CloudFormation—transferable to Terraform plugin development.

- **Collaboration & Leadership**  
  • Led code reviews, mentored junior engineers, participated in all Scrum ceremonies.  
  • Presented internal tech talks on API best practices and DevOps pipelines.

---

## Company Summary
**Leaseweb**  
- Founded 1997, ~600 employees, headquartered in Amsterdam  
- Global footprint: Tier-III data centers, 20+ PoPs, serving startups to Fortune 500  
- Portfolio: dedicated servers, public/private cloud, colocation, CDN, managed Kubernetes  

**Mission & Values**  
- Deliver world-class hosting/cloud solutions with customer centricity, ownership, transparency, collaboration, continuous improvement.  

**Recent Highlights**  
- Launched managed Kubernetes-as-a-Service (Jun 2026)  
- Expanded to U.S. data center in Dallas (Apr 2026)  
- Partnered with Cloudflare for DDoS/WAF (Feb 2026)  
- Published 2030 sustainability roadmap (Dec 2025)  
- Developer Platform hackathon winners for AI-driven API analytics (Q3 2025)  

---

## Predicted Interview Questions

### Technical
1. **Golang & API Design**  
   - “Walk us through designing a high-throughput Go microservice. How do you handle errors, logging, middleware?”  
   - “Compare REST vs. gRPC vs. OpenAPI in the context of Leaseweb’s API strategy.”

2. **Terraform Plugin Development**  
   - “Explain the lifecycle of a Terraform provider. How do you model resources, handle state, and implement CRUD operations?”

3. **Authentication & Security**  
   - “Describe OAuth2 flows you’ve implemented. How would you secure token issuance, revocation, and refresh in a high-scale environment?”

4. **System Architecture & Scalability**  
   - “How would you architect Leaseweb’s abuse platform to handle real-time detection and blocking of malicious traffic?”

5. **Linux & DevOps**  
   - “Show how you’d troubleshoot a Go service running on Linux that suddenly spikes CPU usage.”  
   - “Explain how you’d use Chef (or similar) to provision and maintain a fleet of API servers.”

### Behavioral / Cultural
1. “Tell us about a time you took end-to-end ownership of a production service.”  
2. “How do you adapt when you need to learn a new language or framework quickly?”  
3. “Describe a challenging API design decision you led—what trade-offs did you weigh?”

---

## Questions to Ask Them
1. **Roadmap & Vision**  
   - “How does the Developer Platform’s roadmap align with Leaseweb’s 3-year strategic goals?”  
   - “What are the priority features or major integrations planned for the Terraform provider?”

2. **Team & Process**  
   - “Can you walk me through a recent API rollout—from design, testing, to production?”  
   - “How do squads coordinate with Security and DevOps when releasing breaking changes?”

3. **Success Metrics**  
   - “Which KPIs define API success at Leaseweb (uptime, adoption, latency)?”  
   - “How do you balance feature velocity with reliability and backwards compatibility?”

4. **Learning & Growth**  
   - “What training or mentorship programs exist for engineers new to Go?”  
   - “How can senior engineers shape technical direction or mentor across squads?”

5. **Culture & Events**  
   - “How active is the team in open-source contributions or public forums?”  
   - “Can you share examples of hackathon projects that made it into production?”

---

## Concepts To Know/Review
- **Golang Fundamentals**: goroutines, channels, context.Context patterns, error wrapping  
- **API Best Practices**: idempotency, versioning, pagination, rate limiting  
- **Terraform Plugin SDK**: resource schemas, CRUD functions, state management  
- **OAuth2/JWT**: grant types, token lifecycle, revocation strategies  
- **Distributed Systems**: load balancing, caching (Redis), circuit breakers  
- **Logging & Observability**: ELK Stack, Prometheus, Grafana, distributed tracing (Jaeger)  
- **Chef & IaC**: cookbooks, recipes, idempotency, infrastructure testing  

---

## Strategic Advice
Tone & Focus  
- **Confidence & Humility**: Acknowledge your primary background in Node.js/Python but emphasize rapid learning and proven API expertise.  
- **Ownership Mindset**: Highlight projects where you owned design, deployment, and support—mirror “you build it, you run it.”  
- **Customer Centricity**: Frame technical decisions around internal/external developer experience and uptime.

Red Flags to Watch  
- **Training on Go**: Clarify support for upskilling—ensure resources or mentorship are available.  
- **On-Call Expectations**: Ask about incident rotations and SLAs for API uptime.  
- **Remote-First Dynamics**: Understand cadence of in-person meetups, core working hours, and time zone overlaps.

Final Tip  
- Prepare a 5-minute deep dive on one API you’ve built end-to-end; include architecture, performance metrics, and lessons learned.  
- Bring code samples or diagrams (even a whiteboard sketch) to illustrate your system thinking.  

Good luck—go own that interview!  
```