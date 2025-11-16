# SNCF Price Scraper - Educational Proof of Concept

⚠️ **IMPORTANT DISCLAIMER** ⚠️

This module is a **proof-of-concept for educational purposes ONLY**. It is NOT intended for production use.

## ⚠️ Legal and Ethical Considerations

### Terms of Service
- Web scraping may **violate SNCF's Terms of Service**
- SNCF Connect (formerly Oui.sncf) prohibits automated access
- Violating ToS can result in:
  - IP address blocking
  - Legal action
  - Service termination

### Anti-Scraping Measures
SNCF employs multiple anti-scraping techniques:
- **403 Forbidden** responses for automated requests
- CAPTCHA challenges
- Rate limiting
- User agent detection
- Browser fingerprinting
- Dynamic content loading (JavaScript required)

### Why This Likely Won't Work

1. **API Endpoints Unknown**: The actual SNCF booking API structure is proprietary
2. **Authentication Required**: May need OAuth, session tokens, CSRF tokens
3. **Dynamic Content**: Prices loaded via JavaScript, not in initial HTML
4. **Bot Detection**: Advanced measures to detect and block scrapers
5. **Frequent Changes**: SNCF can change their API at any time

## 📚 Educational Value

This proof-of-concept demonstrates:

### ✅ What You Learn
- How price scraping COULD theoretically work
- The complexity of reverse-engineering booking systems
- Why anti-scraping measures exist
- The importance of official APIs
- HTTP request handling with Python
- Data model design for train offers

### ❌ What This Doesn't Provide
- Working price scraping in production
- Bypass methods for anti-scraping (unethical)
- Complete station code database
- Real-time accurate prices
- Terms of Service compliance

## 🏗️ Architecture

```
sncf_scraper/
├── __init__.py      # Module exports
├── models.py        # TrainOffer and PriceSearchResult models
├── scraper.py       # SNCFPriceScraper implementation
└── README.md        # This file
```

### How It's Supposed to Work (Theoretically)

```python
# 1. Initialize scraper
scraper = SNCFPriceScraper()

# 2. Search for prices
result = scraper.search_prices(
    origin_code="FRPLY",  # Paris Gare de Lyon
    destination_code="FRMSC",  # Marseille Saint-Charles
    departure_date=datetime(2025, 11, 20)
)

# 3. Get price offers
for offer in result.offers:
    print(f"{offer.train_type} - {offer.price} EUR")
```

### Why It Will Fail

```python
# What actually happens:
try:
    result = scraper.search_prices(...)
except httpx.HTTPStatusError as e:
    # ❌ 401 Unauthorized - Authentication required
    print("Blocked by SNCF")
```

### Real-World Evidence

From a professional web scraper on Reddit:

> "I tried both [website and app], with proxies and all that stuff,
> I'm used to doing this (it's partly my job) but this is **far from
> a simple API**. There's SSR, auth with cookies galore,
> regular re-authentication etc."

**Translation**: Even experienced professionals with proper tools can't scrape SNCF reliably.

## 🔧 Technical Implementation

### Station Code Mapping

The scraper requires SNCF station codes (e.g., "FRPLY" for Paris Gare de Lyon), but:
- Navitia API uses different IDs (e.g., "stop_area:SNCF:87686006")
- No complete public mapping exists
- Manual mapping would require 100s of stations

### Minimal Station Codes Included

```python
SIMPLE_MAPPINGS = {
    "stop_area:SNCF:87686006": "FRPLY",  # Paris Gare de Lyon
    "stop_area:SNCF:87751008": "FRMSC",  # Marseille Saint-Charles
    "stop_area:SNCF:87271007": "FRPNO",  # Paris Gare du Nord
    "stop_area:SNCF:87391003": "FRPMO",  # Paris Montparnasse
}
```

### API Endpoint Guesses

The scraper makes educated guesses about SNCF's API:

```python
# These URLs are SPECULATIVE
API_BASE = "https://www.sncf-connect.com/bff/api/v1"
SEARCH_ENDPOINT = f"{API_BASE}/travel-offers/search"
```

**Reality**: The actual API structure is unknown and likely different.

## ✅ Recommended Alternatives

### For Production Use

1. **Lyko SNCF Connect API**
   - Commercial API provider
   - Official booking integration
   - No SNCF approval needed
   - Commission-based pricing
   - Website: https://lyko.tech/en/portfolio/train-api/sncf-connect-api/

2. **Trainline API**
   - Multi-operator booking platform
   - Includes SNCF
   - Commercial partnership
   - Established provider

3. **Official SNCF Partnership**
   - Direct agreement with SNCF
   - Requires ATOUT France registration
   - €10,000+ deposit
   - Full access to booking system

### For Personal Use

1. **SNCF Connect Website**
   - https://www.sncf-connect.com
   - Official source
   - Always accurate
   - No scraping needed

2. **Trainline Website**
   - https://www.thetrainline.com
   - User-friendly interface
   - Price comparison

## 🧪 Testing

Run the test suite (expect failures):

```bash
uv run tests/test_price_scraper.py
```

**Expected Results:**
- ✅ Scraper initialization: PASS
- ❌ Price check: FAIL (403 Forbidden)
- ✅ Unknown station handling: PASS

**This is normal!** The tests demonstrate why official APIs are necessary.

## 📖 Lessons Learned

### 1. Web Scraping is Complex
- Requires reverse-engineering
- Fragile and breaks easily
- Constant maintenance needed

### 2. Anti-Scraping Works
- Modern websites have sophisticated protection
- Circumventing protection is unethical and illegal
- Not worth the legal/technical risk

### 3. Official APIs Are Better
- Stable, documented interfaces
- Legal and supported
- Better long-term solution
- Worth the investment

### 4. Renfe vs SNCF
- **Renfe**: Uses simpler DWR protocol (easier to scrape)
- **SNCF**: Modern REST API with heavy protection (harder to scrape)
- Both scraping approaches violate ToS

## 🎓 Educational Goals Achieved

If you've reviewed this code, you've learned:

✅ HTTP request handling with httpx
✅ Data modeling with dataclasses
✅ Error handling and logging
✅ API reverse-engineering concepts
✅ Why web scraping isn't always viable
✅ Importance of Terms of Service compliance
✅ Value of official APIs and partnerships

## 📝 License Note

This code is provided for educational purposes under the MIT license, but:
- Using it to scrape SNCF may violate their ToS
- User assumes all legal responsibility
- Author disclaims all liability
- Not endorsed or approved by SNCF

## 🤝 Ethical Guidelines

If you're considering web scraping:

1. **Read the Terms of Service** first
2. **Check robots.txt** for allowed/disallowed paths
3. **Respect rate limits** and add delays
4. **Identify yourself** with proper User-Agent
5. **Consider alternatives** (official APIs, partnerships)
6. **When in doubt, ask permission** from the site owner

## 🔗 Related Resources

- [Navitia API](https://doc.navitia.io/) - Official transit API (no prices)
- [SNCF Open Data](https://ressources.data.sncf.com/) - Public schedules only
- [Lyko Tech](https://lyko.tech/) - Commercial API provider
- [Trainline](https://www.thetrainline.com/) - Multi-operator booking

---

**Remember**: This is a proof-of-concept for educational purposes.
**For real applications**: Use official APIs and respect Terms of Service. 🚂
