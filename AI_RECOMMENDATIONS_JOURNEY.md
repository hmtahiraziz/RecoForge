# AI Recommendations Journey Flow

## 🎯 Complete User Journey

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI RECOMMENDATIONS SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DATA SOURCE   │───▶│   INGESTION     │───▶│  NORMALIZATION  │───▶│   EMBEDDINGS    │
│                 │    │                 │    │                 │    │                 │
│ • JSON/JSONL    │    │ • Stream data   │    │ • Clean data    │    │ • OpenAI API    │
│ • Large files   │    │ • Validate      │    │ • Map regions   │    │ • Batch process │
│ • Product data  │    │ • Error handle  │    │ • Parse ABV     │    │ • Rate limiting │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CATALOG.JSONL │    │   MANIFEST.JSON │    │  HIERARCHICAL   │    │  EMBEDDINGS.NPY │
│                 │    │                 │    │   CATEGORIES    │    │                 │
│ • Normalized    │    │ • Metadata      │    │ • Level 1-4     │    │ • Vector store  │
│ • Compact JSON  │    │ • Counts        │    │ • Smart infer   │    │ • Float32       │
│ • Line-by-line  │    │ • Timestamps    │    │ • Tag mapping   │    │ • Memory map    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FAISS INDEX   │◀───│  INDEX BUILDING │◀───│  VECTOR ARRAY   │◀───│   EMBEDDINGS    │
│                 │    │                 │    │                 │    │                 │
│ • IndexIVFFlat  │    │ • Smart select  │    │ • NumPy array   │    │ • OpenAI API    │
│ • IndexHNSWFlat │    │ • N>300k logic  │    │ • Batch process │    │ • Batch calls   │
│ • Fast search   │    │ • Auto train    │    │ • Error handle  │    │ • Rate limiting │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  FAISS.INDEX    │    │   ID_MAP.JSONL  │    │   META.JSONL    │    │  PROCESSING     │
│                 │    │                 │    │                 │    │                 │
│ • Binary index  │    │ • Row→ID map    │    │ • Runtime meta  │    │ • Batch logs    │
│ • Fast retrieval│    │ • SKU mapping   │    │ • Compact data  │    │ • Error reports │
│ • Memory load   │    │ • Title lookup  │    │ • Quick access  │    │ • Stats output  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Real-Time Recommendation Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        RECOMMENDATION REQUEST FLOW                             │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER QUERY    │───▶│  QUERY BUILDING │───▶│   EMBEDDING     │───▶│  FAISS SEARCH   │
│                 │    │                 │    │                 │    │                 │
│ • "BBQ beer"    │    │ • Combine query │    │ • OpenAI API    │    │ • TopK=600      │
│ • Preferences   │    │ • Add answers   │    │ • Text format   │    │ • Similarity    │
│ • User context  │    │ • Format text   │    │ • Batch call    │    │ • Fast search   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  QUERY TEXT     │    │  EMBEDDING      │    │  VECTOR ARRAY   │    │  CANDIDATES     │
│                 │    │                 │    │                 │    │                 │
│ "Beer; style    │    │ • 1536 dims     │    │ • Float32       │    │ • 600 items     │
│ Stout; brands   │    │ • Normalized    │    │ • Memory map    │    │ • Scores        │
│ Sea Legs; pack  │    │ • API response  │    │ • Fast access   │    │ • Metadata      │
│ 24; region      │    │ • Error handle  │    │ • Batch ready   │    │ • Ready filter  │
│ AU-SA; abv mid" │    │ • Rate limit    │    │ • Validation    │    │ • User context  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  HARD FILTERS   │◀───│  FILTERED ITEMS │◀───│  CANDIDATES     │◀───│  FAISS SEARCH   │
│                 │    │                 │    │                 │    │                 │
│ • Stock check   │    │ • Pass filters  │    │ • 600 items     │    │ • TopK=600      │
│ • Region check  │    │ • User context  │    │ • Scores        │    │ • Similarity    │
│ • Age check     │    │ • Legal compliance│  │ • Metadata      │    │ • Fast search   │
│ • ABV check     │    │ • Availability  │    │ • Ready filter  │    │ • Memory load   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  FILTER LOGIC   │    │  FILTERED SET   │    │  CANDIDATE      │    │  SEARCH RESULT  │
│                 │    │                 │    │  VALIDATION     │    │                 │
│ • in_stock()    │    │ • Reduced set   │    │ • Data quality  │    │ • Ranked items  │
│ • region_ok()   │    │ • User context  │    │ • Field check   │    │ • Scores        │
│ • legal_ok()    │    │ • Legal safe    │    │ • Type check    │    │ • Metadata      │
│ • abv_band_ok() │    │ • Available     │    │ • Format check  │    │ • Ready rank    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  GPT RE-RANKING │◀───│  RANKING RESULT │◀───│  FILTERED ITEMS │◀───│  HARD FILTERS   │
│                 │    │                 │    │                 │    │                 │
│ • OpenAI API    │    │ • Ranked items  │    │ • Pass filters  │    │ • Stock check   │
│ • Function call │    │ • Scores        │    │ • User context  │    │ • Region check  │
│ • Structured    │    │ • Reasons       │    │ • Legal safe    │    │ • Age check     │
│ • Instructions  │    │ • Quantities    │    │ • Available     │    │ • ABV check     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  GPT-4.1-MINI   │    │  RANKED LIST    │    │  FILTER LOGIC   │    │  FILTER RESULT  │
│                 │    │                 │    │                 │    │                 │
│ • Responses API │    │ • Top items     │    │ • Validation    │    │ • Passed items  │
│ • Function call │    │ • Explanations  │    │ • User context  │    │ • User context  │
│ • Structured    │    │ • Quantities    │    │ • Legal check   │    │ • Legal safe    │
│ • Error handle  │    │ • Confidence    │    │ • Availability  │    │ • Available     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  FINAL RESPONSE │◀───│  RESPONSE BUILD │◀───│  RANKING RESULT │◀───│  GPT RE-RANKING │
│                 │    │                 │    │                 │    │                 │
│ • Items list    │    │ • Format data   │    │ • Ranked items  │    │ • OpenAI API    │
│ • Confidence    │    │ • Add metadata  │    │ • Scores        │    │ • Function call │
│ • Subtotal      │    │ • Compute stats │    │ • Reasons       │    │ • Structured    │
│ • Processing    │    │ • Error handle  │    │ • Quantities    │    │ • Instructions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  USER RECEIVES  │    │  RESPONSE DATA  │    │  RANKING DATA   │    │  GPT RESPONSE   │
│                 │    │                 │    │                 │    │                 │
│ • Recommendations│   │ • Items array   │    │ • Top items     │    │ • Function call │
│ • Explanations  │    │ • Confidence    │    │ • Explanations  │    │ • Structured    │
│ • Quantities    │    │ • Subtotal      │    │ • Quantities    │    │ • Error handle  │
│ • Confidence    │    │ • Processing    │    │ • Confidence    │    │ • Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 User Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER QUERY    │───▶│  RECOMMENDATIONS│───▶│  USER ACTIONS   │───▶│  EVENT TRACKING │
│                 │    │                 │    │                 │    │                 │
│ • "BBQ beer"    │    │ • AI powered    │    │ • View items    │    │ • Log events    │
│ • Preferences   │    │ • Filtered      │    │ • Click items   │    │ • Track behavior│
│ • User context  │    │ • Ranked        │    │ • Add to cart   │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  QUERY PROCESS  │    │  RECOMMENDATION │    │  ACTION EVENTS  │    │  EVENT STORAGE  │
│                 │    │  GENERATION     │    │                 │    │                 │
│ • Text building │    │ • Embedding     │    │ • shown         │    │ • Database      │
│ • Context add   │    │ • FAISS search  │    │ • clicked       │    │ • JSONB meta    │
│ • Format query  │    │ • Hard filters  │    │ • added         │    │ • User tracking │
│ • API call      │    │ • GPT ranking   │    │ • purchased     │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  TEMPLATE SAVE  │◀───│  USER PREFERENCES│◀───│  ACTION EVENTS  │◀───│  EVENT TRACKING │
│                 │    │                 │    │                 │    │                 │
│ • Save template │    │ • User context  │    │ • User actions  │    │ • Log events    │
│ • Reuse later   │    │ • Preferences   │    │ • Interaction   │    │ • Track behavior│
│ • Personalize   │    │ • History       │    │ • Behavior      │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  TEMPLATE DB    │    │  PREFERENCE     │    │  EVENT DB       │    │  ANALYTICS      │
│                 │    │  STORAGE        │    │                 │    │                 │
│ • PostgreSQL    │    │ • User data     │    │ • PostgreSQL    │    │ • User behavior │
│ • JSONB items   │    │ • Preferences   │    │ • JSONB meta    │    │ • Recommendation│
│ • User auth     │    │ • History       │    │ • User tracking │    │ • Performance   │
│ • CRUD ops      │    │ • Personalize   │    │ • Event types   │    │ • Insights      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DATA LAYER    │    │  PROCESSING     │    │   AI LAYER      │    │   API LAYER     │
│                 │    │     LAYER       │    │                 │    │                 │
│ • PostgreSQL    │    │ • Ingestion     │    │ • OpenAI API    │    │ • FastAPI       │
│ • JSONB storage │    │ • Normalization │    │ • Embeddings    │    │ • JWT Auth      │
│ • Event tracking│    │ • Validation    │    │ • GPT ranking   │    │ • Rate limiting │
│ • Template mgmt │    │ • Error handle  │    │ • Function call │    │ • Error handle  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   STORAGE       │    │  DATA PIPELINE  │    │  AI SERVICES    │    │  ENDPOINTS      │
│                 │    │                 │    │                 │    │                 │
│ • Templates     │    │ • Stream data   │    │ • Embedding     │    │ • /recs/health  │
│ • Events        │    │ • Clean data    │    │ • Re-ranking    │    │ • /recs/recommendations│
│ • Metadata      │    │ • Validate      │    │ • Filtering     │    │ • /recs/templates│
│ • User data     │    │ • Transform     │    │ • Validation    │    │ • /recs/events  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   INDEX LAYER   │◀───│  VECTOR STORE   │◀───│  AI SERVICES    │◀───│  API LAYER      │
│                 │    │                 │    │                 │    │                 │
│ • FAISS index   │    │ • NumPy arrays  │    │ • OpenAI API    │    │ • REST API      │
│ • Fast search   │    │ • Memory map    │    │ • Batch process │    │ • JSON responses│
│ • Similarity    │    │ • Float32       │    │ • Rate limiting │    │ • Error codes   │
│ • TopK results  │    │ • Efficient     │    │ • Error handle  │    │ • Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SEARCH ENGINE  │    │  VECTOR DATA    │    │  AI PROCESSING  │    │  CLIENT ACCESS  │
│                 │    │                 │    │                 │    │                 │
│ • IndexIVFFlat  │    │ • Embeddings    │    │ • Text format   │    │ • HTTP requests │
│ • IndexHNSWFlat │    │ • Metadata      │    │ • Query build   │    │ • JWT tokens    │
│ • Memory load   │    │ • ID mapping    │    │ • Batch calls   │    │ • Rate limiting │
│ • Fast retrieval│    │ • Runtime meta  │    │ • Structured    │    │ • Error handle  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Performance Characteristics

### Data Processing Pipeline
- **Ingestion**: ~1000 items/second
- **Normalization**: ~500 items/second
- **Embeddings**: ~50 items/second (API rate limited)
- **Index Building**: ~1000 items/second

### Real-Time Recommendations
- **Query Processing**: ~100ms
- **FAISS Search**: ~10ms
- **Hard Filtering**: ~5ms
- **GPT Re-ranking**: ~1-2 seconds
- **Total Response**: ~1-3 seconds

### Storage Requirements
- **Embeddings**: ~6MB per 1000 items (1536 dims)
- **FAISS Index**: ~2MB per 1000 items
- **Metadata**: ~1MB per 1000 items
- **Total**: ~9MB per 1000 items

## 🎯 Key Success Metrics

### System Performance
- **Uptime**: 99.9%
- **Response Time**: <3 seconds
- **Error Rate**: <1%
- **Throughput**: 100 requests/minute

### AI Quality
- **Embedding Quality**: OpenAI state-of-the-art
- **Re-ranking Accuracy**: GPT-4.1-mini powered
- **Filter Effectiveness**: 100% compliance
- **User Satisfaction**: Measured via events

### Business Impact
- **Recommendation Relevance**: High user engagement
- **Conversion Rate**: Tracked via events
- **User Retention**: Template usage
- **Cost Efficiency**: Optimized API usage
