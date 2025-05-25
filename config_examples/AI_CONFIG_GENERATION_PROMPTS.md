# 🤖 AI-Assisted Configuration Generation Guide

Use these proven prompts with any LLM (Claude, ChatGPT, etc.) to generate production-ready configuration files for your Universal Organization RAG System.

## 🎯 Master Prompt Template

```
I need to create a configuration file for a Universal Organization RAG System. 

Please generate a config.yaml file for:

ORGANIZATION: [Your company name]
TYPE: [startup/enterprise/consulting/personal]
PURPOSE: [interview_preparation/knowledge_management/onboarding]
TEAMS: [List the main teams/departments]
DOCS LOCATION: [Path to your documentation]
SPECIAL FOCUS: [Any specific areas to emphasize]

Example values:
- ORGANIZATION: "TechCorp Inc"
- TYPE: "enterprise"
- PURPOSE: "interview_preparation"
- TEAMS: ["engineering", "product", "data", "platform"]
- DOCS LOCATION: "/Users/username/company-docs"
- SPECIAL FOCUS: "Focus on product strategy and engineering culture"

Please create a complete config.yaml file following the Universal Organization RAG format with:
1. Organization details
2. RAG goals and focus areas
3. Data source paths
4. Target teams with relevant keywords
5. Content categorization settings
6. Processing configuration optimized for the organization type
7. ChromaDB settings
8. Interview preparation settings if applicable

Make it production-ready and include helpful comments.
```

## 🏢 Industry-Specific Prompts

### Fintech/Banking
```
Generate a config.yaml for a fintech company interview preparation:

ORGANIZATION: "FinanceFlow Corp"
TYPE: "enterprise"
PURPOSE: "interview_preparation"
TEAMS: ["engineering", "product", "compliance", "risk", "data"]
DOCS LOCATION: "/Users/candidate/financeflow-research"
SPECIAL FOCUS: "Regulatory compliance, risk management, financial product strategy, and security practices"

Include fintech-specific keywords for:
- Regulatory compliance (SOX, PCI DSS, KYC, AML)
- Financial products (payments, lending, trading)
- Risk management and fraud detection
- Data privacy and security
```

### Healthcare/Biotech
```
Generate a config.yaml for a healthcare technology company:

ORGANIZATION: "HealthTech Solutions"
TYPE: "startup"
PURPOSE: "interview_preparation"
TEAMS: ["engineering", "product", "clinical", "regulatory", "data-science"]
DOCS LOCATION: "/Users/candidate/healthtech-docs"
SPECIAL FOCUS: "HIPAA compliance, clinical workflows, patient safety, and medical device regulations"

Include healthcare-specific considerations for:
- Medical device regulations (FDA, CE marking)
- Clinical trial management
- Patient data privacy (HIPAA, GDPR)
- Healthcare interoperability (HL7, FHIR)
```

### E-commerce/Retail
```
Generate a config.yaml for an e-commerce platform:

ORGANIZATION: "ShopSmart Inc"
TYPE: "enterprise"
PURPOSE: "interview_preparation"
TEAMS: ["engineering", "product", "growth", "operations", "data"]
DOCS LOCATION: "/Users/candidate/shopsmart-research"
SPECIAL FOCUS: "Customer acquisition, conversion optimization, supply chain, and marketplace dynamics"

Include e-commerce-specific areas:
- Customer journey and conversion funnels
- Payment processing and fraud prevention
- Inventory management and logistics
- Personalization and recommendation systems
```

### Developer Tools/SaaS
```
Generate a config.yaml for a developer tools company:

ORGANIZATION: "DevTools Pro"
TYPE: "startup"
PURPOSE: "interview_preparation"
TEAMS: ["engineering", "product", "developer-relations", "growth"]
DOCS LOCATION: "/Users/candidate/devtools-research"
SPECIAL FOCUS: "Developer experience, API design, platform adoption, and technical community building"

Include developer tools specific elements:
- API design and documentation
- SDK and integration patterns
- Developer community engagement
- Technical product marketing
```

## 🎯 Role-Specific Prompts

### Product Manager Interview
```
Create a PM-optimized config.yaml for:

ORGANIZATION: "[Company Name]"
TYPE: "[startup/enterprise]"
PURPOSE: "interview_preparation"
ROLE FOCUS: "Product Manager"
SPECIAL FOCUS: "Customer insights, product strategy, team collaboration, and competitive positioning"

Optimize for PM interview preparation with emphasis on:
- Customer pain points and use cases
- Product roadmap and strategy documents
- Cross-functional team collaboration patterns
- Competitive analysis and market positioning
- User research and data-driven decision making
```

### Engineering Manager Interview
```
Create an EM-optimized config.yaml for:

ORGANIZATION: "[Company Name]"
TYPE: "[startup/enterprise]"
PURPOSE: "interview_preparation"
ROLE FOCUS: "Engineering Manager"
SPECIAL FOCUS: "Technical architecture, team scaling, engineering culture, and delivery processes"

Optimize for EM interview preparation with emphasis on:
- Technical architecture and system design
- Engineering culture and team dynamics
- Development processes and methodologies
- Performance management and career development
- Technical debt and infrastructure decisions
```

### Data Scientist Interview
```
Create a DS-optimized config.yaml for:

ORGANIZATION: "[Company Name]"
TYPE: "[startup/enterprise]"
PURPOSE: "interview_preparation"
ROLE FOCUS: "Data Scientist"
SPECIAL FOCUS: "Data infrastructure, ML systems, analytics culture, and data-driven insights"

Optimize for DS interview preparation with emphasis on:
- Data infrastructure and pipelines
- Machine learning model deployment
- Analytics and experimentation frameworks
- Data governance and quality
- Business impact measurement
```

## 📋 Context-Specific Additions

### Series A Startup
```
Additional context for Series A startup:
- Fast-paced environment with rapid iteration
- Limited resources requiring prioritization skills
- Emphasis on product-market fit and growth metrics
- Cross-functional collaboration in small teams
- Culture of experimentation and learning
```

### Enterprise (1000+ employees)
```
Additional context for large enterprise:
- Complex organizational structure with multiple divisions
- Emphasis on process standardization and governance
- Stakeholder management across departments
- Compliance and regulatory considerations
- Scale challenges and technical complexity
```

### Consulting Firm
```
Additional context for consulting:
- Client-focused delivery and relationship management
- Industry expertise and thought leadership
- Project management and timeline delivery
- Knowledge sharing and methodology development
- Business development and proposal processes
```

## 🛠 Best Practices for AI-Generated Configs

### ✅ Do This:
1. **Be specific** about company type, size, and industry
2. **Include actual team names** from the organization
3. **Provide real documentation paths** if you have them
4. **Mention the specific role** you're interviewing for
5. **Include unique company aspects** (remote-first, open source, etc.)
6. **Ask for helpful comments** in the generated config
7. **Request optimization** for your specific use case

### ❌ Avoid This:
1. **Generic prompts** without specific context
2. **Assuming standard team structures** without verification
3. **Ignoring industry-specific requirements**
4. **Forgetting to validate paths** before running setup
5. **Not customizing keywords** for the company's domain
6. **Using placeholder values** in production configs

## 🎯 Example AI Conversations

### Successful Prompt:
**Human**: *"I'm preparing for a Senior Product Manager interview at Stripe. They focus on payments infrastructure, have engineering, product, partnerships, and risk teams. My research docs are in /Users/alex/stripe-research. I want to understand their approach to global payments, developer experience, and platform strategy."*

**AI Response**: *[Generates comprehensive config.yaml with payments-specific keywords, fintech compliance settings, developer platform focus, and global scaling considerations]*

### Enhanced Follow-up:
**Human**: *"Great! Can you also add keywords for marketplace dynamics, two-sided networks, and API ecosystem management since Stripe connects merchants and payment processors?"*

**AI Response**: *[Updates config with marketplace-specific content categorization and two-sided network keywords]*

## 🚀 Production Tips

1. **Save your prompts** - You might need to regenerate configs
2. **Version control** your configs alongside documentation changes
3. **Test configurations** before important interviews or deployments
4. **Share successful prompts** with your team for consistency
5. **Iterate based on results** - Improve prompts based on what works

## 📝 Template Checklist

Before using an AI-generated config, verify:
- [ ] Organization name and description are accurate
- [ ] All team names match the actual company structure
- [ ] File paths exist and are accessible
- [ ] Keywords reflect the company's specific domain
- [ ] Processing settings are appropriate for your hardware
- [ ] ChromaDB collection name follows naming conventions
- [ ] Focus areas align with your interview preparation goals

---

**🎯 Ready to generate your config? Use the master prompt template above and customize with your specific details!**
