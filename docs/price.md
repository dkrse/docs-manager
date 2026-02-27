# Pricing Analysis

**Author:** krse

## Overview

Analýza reálnych cenových modelov pre Document Manager na základe prieskumu trhu DMS (Document Management System) riešení v roku 2025/2026.

## Trhový kontext

| Segment | Typická cena | Príklady |
|---------|-------------|----------|
| Open-source / self-hosted | €0 (len hosting) | Paperless-ngx, Mayan EDMS, SeedDMS |
| SaaS - basic | €10–20 / používateľ / mesiac | ContractZen (€9.50), Xodo (~€13) |
| SaaS - mid-range | €20–50 / používateľ / mesiac | Fluix (€30), M-Files (€39–59) |
| SaaS - enterprise | €50–150+ / používateľ / mesiac | M-Files, OpenText, DocuWare |
| On-premise licencia | €5 000–50 000+ jednorazovo | Alfresco Enterprise, OpenKM Pro |

Cloud riešenia tvoria 67%+ trhu. Priemerná mesačná cena za DMS je €40–300/mesiac podľa počtu používateľov a funkcií.

## Porovnanie s konkurenciou

### Čo Document Manager ponúka
- Multi-formát (PDF, DOCX, MD, TXT) s in-browser prehliadaním
- Deduplikácia (SHA-256)
- Metadata, kategórie, hashtagy
- Live vyhľadávanie (diacritics-insensitive)
- Light/dark téma
- Docker deployment
- Self-hosted (žiadne mesačné poplatky za cloud)

### Čo chýba oproti enterprise riešeniam
- OCR (rozpoznávanie textu z obrázkov/skenov)
- Workflow / schvaľovanie dokumentov
- Verzionovanie dokumentov
- Full-text search (obsah súborov)
- API pre externé integrácie (REST API je čiastočne)
- Audit log
- Multi-tenant architektúra
- S3/object storage podpora

## Navrhované cenové modely

### Model A: Open-source + platená podpora

| Tier | Cena | Čo zahŕňa |
|------|-------|-----------|
| Community | €0 | Plná aplikácia, self-hosted, bez podpory |
| Support | €50/mesiac | Email podpora, prioritné bugfixy |
| Enterprise | €200/mesiac | Podpora + OCR + audit log + SLA |

**Pre koho:** Vývojári, malé firmy, ktoré si vedia nasadiť Docker sami.

### Model B: SaaS (hosted)

| Tier | Cena | Limity |
|------|-------|--------|
| Starter | €8/používateľ/mesiac | 5 GB storage, 3 používatelia |
| Business | €15/používateľ/mesiac | 50 GB storage, neobmedzení používatelia |
| Enterprise | €30/používateľ/mesiac | Neobmedzený storage, OCR, audit log, SLA |

**Pre koho:** Firmy, ktoré nechcú spravovať infraštruktúru.

### Model C: Jednorazová licencia (self-hosted)

| Tier | Cena | Čo zahŕňa |
|------|-------|-----------|
| Personal | €0 | 1 používateľ, plné funkcie |
| Team | €199 jednorazovo | Do 10 používateľov |
| Business | €499 jednorazovo | Neobmedzení používatelia |
| Enterprise | €999+ jednorazovo | + OCR, audit log, 1 rok support |

**Pre koho:** Firmy, ktoré preferujú jednorazový nákup.

## Realistické odporúčanie

Vzhľadom na aktuálny stav produktu (funkčný, ale bez OCR, verzionovania, audit logu):

### Najreálnejšia cena

| Scenár | Cena | Zdôvodnenie |
|--------|-------|------------|
| **Self-hosted licencia** | **€99–299 jednorazovo** | Jednoduchý DMS pre malý tím (2–10 ľudí). Porovnateľné s lacnými komerčnými riešeniami, ale bez mesačných poplatkov. |
| **SaaS hosted** | **€8–12/používateľ/mesiac** | Dolná hranica trhu. Produkt pokrýva základné potreby, ale chýbajú enterprise funkcie. |
| **Open-source + support** | **€0 + €50/mesiac za podporu** | Najlepší model pre budovanie komunity. |

### Cena za hodinu vývoja (ak predávame ako službu)

| Položka | Odhad |
|---------|-------|
| Celkový čas vývoja | ~40–60 hodín |
| Hodinová sadzba (SK trh) | €30–60/h |
| **Celková hodnota vývoja** | **€1 200–3 600** |
| Break-even pri €99/licencia | 12–36 predajov |
| Break-even pri SaaS €10/user/mes | 10 používateľov × 12–36 mesiacov |

## Záver

Najvhodnejší model závisí od cieľovej skupiny:

1. **Pre komunitu/freelancerov** → Open-source (budovanie reputácie, upsell support)
2. **Pre malé firmy (SK/CZ trh)** → Jednorazová licencia €99–299
3. **Pre širší trh** → SaaS za €8–15/používateľ/mesiac (vyžaduje hosting infraštruktúru)

Pre zvýšenie hodnoty a oprávnenie vyššej ceny by bolo potrebné pridať: OCR, verzionovanie, full-text search, audit log.

## Zdroje

- [Document Management Software Costs & Prices 2025](https://www.bitfarm-archiv.com/document-management/glossary/document-management-system-software-cost-price.html)
- [How Much Does Document Management Software Cost in 2025](https://priceithere.com/document-management-software-prices/)
- [Document Management Cost: SMB vs Enterprise 2025](https://www.pericent.com/document-management-cost-smb-vs-enterprise-2025-guide/)
- [Best Document Management Software for Small Business 2026](https://research.com/software/document-management-software-for-small-business)
- [10 Best Open Source Document Management Software 2026](https://www.papermark.com/blog/best-open-source-document-management-software)
