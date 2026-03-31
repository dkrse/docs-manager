# Pricing Analysis

**Author:** krse

## Overview

Analysis of realistic pricing models for Document Manager based on a 2025/2026 market survey of DMS (Document Management System) solutions.

## Market Context

| Segment | Typical Price | Examples |
|---------|--------------|----------|
| Open-source / self-hosted | $0 (hosting only) | Paperless-ngx, Mayan EDMS, SeedDMS |
| SaaS - basic | $10-20 / user / month | ContractZen ($9.50), Xodo (~$13) |
| SaaS - mid-range | $20-50 / user / month | Fluix ($30), M-Files ($39-59) |
| SaaS - enterprise | $50-150+ / user / month | M-Files, OpenText, DocuWare |
| On-premise license | $5,000-50,000+ one-time | Alfresco Enterprise, OpenKM Pro |

Cloud solutions make up 67%+ of the market. Average monthly cost for a DMS is $40-300/month depending on the number of users and features.

## Comparison with Competitors

### What Document Manager Offers
- Multi-format (PDF, DOCX, MD, TXT) with in-browser viewing
- Full-text search (content extraction from all supported formats)
- Deduplication (SHA-256)
- Metadata, categories, hashtags, favorites
- Grid/list view with bulk operations
- Public document sharing (shareable links)
- Multi-file upload with progress
- Secure daily-rotating document URLs
- Light/dark theme
- Docker deployment
- Self-hosted (no monthly cloud fees)
- REST API for documents, settings, upload, search

### What's Missing Compared to Enterprise Solutions
- OCR (text recognition from images/scans)
- Workflow / document approval
- Document versioning
- Audit log
- Multi-tenant architecture
- S3/object storage support

## Proposed Pricing Models

### Model A: Open-source + Paid Support

| Tier | Price | Includes |
|------|-------|----------|
| Community | $0 | Full application, self-hosted, no support |
| Support | $50/month | Email support, priority bug fixes |
| Enterprise | $200/month | Support + OCR + audit log + SLA |

**Target audience:** Developers, small businesses that can deploy Docker themselves.

### Model B: SaaS (Hosted)

| Tier | Price | Limits |
|------|-------|--------|
| Starter | $8/user/month | 5 GB storage, 3 users |
| Business | $15/user/month | 50 GB storage, unlimited users |
| Enterprise | $30/user/month | Unlimited storage, OCR, audit log, SLA |

**Target audience:** Companies that don't want to manage infrastructure.

### Model C: One-time License (Self-hosted)

| Tier | Price | Includes |
|------|-------|----------|
| Personal | $0 | 1 user, full features |
| Team | $199 one-time | Up to 10 users |
| Business | $499 one-time | Unlimited users |
| Enterprise | $999+ one-time | + OCR, audit log, 1 year support |

**Target audience:** Companies that prefer a one-time purchase.

## Realistic Recommendation

Given the current state of the product (functional, but without OCR, versioning, audit log):

### Most Realistic Price

| Scenario | Price | Justification |
|----------|-------|---------------|
| **Self-hosted license** | **$99-299 one-time** | Simple DMS for a small team (2-10 people). Comparable to inexpensive commercial solutions, but without monthly fees. |
| **SaaS hosted** | **$8-12/user/month** | Lower end of the market. The product covers basic needs, but lacks enterprise features. |
| **Open-source + support** | **$0 + $50/month for support** | Best model for building a community. |

### Development Cost (if Sold as a Service)

| Item | Estimate |
|------|----------|
| Total development time | ~40-60 hours |
| Hourly rate (market average) | $30-60/h |
| **Total development value** | **$1,200-3,600** |
| Break-even at $99/license | 12-36 sales |
| Break-even at SaaS $10/user/month | 10 users x 12-36 months |

## Conclusion

The most suitable model depends on the target audience:

1. **For community/freelancers** - Open-source (building reputation, upsell support)
2. **For small businesses** - One-time license $99-299
3. **For broader market** - SaaS at $8-15/user/month (requires hosting infrastructure)

To increase value and justify a higher price, the following features would need to be added: OCR, versioning, audit log.

## Sources

- [Document Management Software Costs & Prices 2025](https://www.bitfarm-archiv.com/document-management/glossary/document-management-system-software-cost-price.html)
- [How Much Does Document Management Software Cost in 2025](https://priceithere.com/document-management-software-prices/)
- [Document Management Cost: SMB vs Enterprise 2025](https://www.pericent.com/document-management-cost-smb-vs-enterprise-2025-guide/)
- [Best Document Management Software for Small Business 2026](https://research.com/software/document-management-software-for-small-business)
- [10 Best Open Source Document Management Software 2026](https://www.papermark.com/blog/best-open-source-document-management-software)
