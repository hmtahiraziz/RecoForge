# 🚀 Complete API Documentation

## Table of Contents
1. [Authentication](#authentication)
2. [Admin User Management](#admin-user-management)
3. [Questionnaire Management](#questionnaire-management)
4. [Enquiry Management](#enquiry-management)
5. [Question Types Reference](#question-types-reference)
6. [Error Handling](#error-handling)
7. [Sample Workflows](#sample-workflows)

---

## 🔐 Authentication

All mutations require JWT authentication via `Authorization: Bearer <token>` header.

### Login Admin User
```graphql
mutation {
  loginAdminUser(loginInput: {
    email: "admin@example.com"
    password: "admin123"
  }) {
    accessToken
    adminUser {
      id
      email
      role
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "loginAdminUser": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "adminUser": {
        "id": "a029898d-45bb-4f29-9d58-173ea706eccd",
        "email": "admin@example.com",
        "role": "SUPERADMIN"
      }
    }
  }
}
```

### Get Current User
```graphql
query {
  me {
    id
    email
    role
    createdAt
    updatedAt
  }
}
```

**Headers Required:**
```
Authorization: Bearer <your_jwt_token>
```

---

## 👥 Admin User Management

### Register New Admin User (Superadmin only)
```graphql
mutation {
  registerAdminUser(adminInput: {
    email: "editor@example.com"
    password: "editor123"
    role: EDITOR
  }) {
    id
    email
    role
    createdAt
  }
}
```

**Available Roles:**
- `SUPERADMIN` - Full access to everything
- `EDITOR` - Can manage questionnaires
- `VIEWER` - Read-only access

---

## 📋 Questionnaire Management

### 1. Create Questionnaire

#### Simple Questionnaire (No Questions)
```graphql
mutation {
  createQuestionnaire(input: {
    categoryCode: "restaurant"
    title: "Restaurant Feedback Form"
    description: "A simple feedback form"
  }) {
    id
    title
    categoryCode
    status
    isActive
    version
    description
    createdAt
  }
}
```

#### Complex Questionnaire (With Questions)
```graphql
mutation {
  createQuestionnaire(input: {
    categoryCode: "hotel"
    title: "Hotel Feedback Form"
    description: "A comprehensive hotel feedback form"
    questions: [
      {
        key: "overall_rating"
        type: SCALE
        label: "How would you rate your overall experience?"
        required: true
        orderIndex: 1
      },
      {
        key: "food_quality"
        type: SINGLE
        label: "How was the food quality?"
        required: true
        orderIndex: 2
        options: [
          {value: "excellent", label: "Excellent", orderIndex: 1}
          {value: "good", label: "Good", orderIndex: 2}
          {value: "average", label: "Average", orderIndex: 3}
          {value: "poor", label: "Poor", orderIndex: 4}
        ]
      },
      {
        key: "recommendations"
        type: MULTI
        label: "What would you recommend to others?"
        required: false
        orderIndex: 3
        options: [
          {value: "food", label: "The Food", orderIndex: 1}
          {value: "service", label: "The Service", orderIndex: 2}
          {value: "atmosphere", label: "The Atmosphere", orderIndex: 3}
        ]
      },
      {
        key: "newsletter"
        type: BOOLEAN
        label: "Would you like to receive our newsletter?"
        required: true
        orderIndex: 4
      },
      {
        key: "visit_frequency"
        type: NUMBER
        label: "How many times have you visited us?"
        required: false
        orderIndex: 5
      },
      {
        key: "comments"
        type: TEXT
        label: "Additional comments or suggestions"
        required: false
        orderIndex: 6
      }
    ]
  }) {
    id
    title
    categoryCode
    status
    isActive
    version
    questions {
      id
      key
      type
      label
      required
      orderIndex
      options {
        id
        value
        label
        orderIndex
      }
    }
  }
}
```

### 2. Query Questionnaires

#### List All Questionnaires
```graphql
query {
  questionnaires {
    id
    title
    categoryCode
    status
    isActive
    version
    createdAt
    updatedAt
    publishedAt
  }
}
```

#### Filter Questionnaires
```graphql
# Filter by category
query {
  questionnaires(category: "restaurant") {
    id
    title
    categoryCode
    status
  }
}

# Filter by status
query {
  questionnaires(status: DRAFT) {
    id
    title
    status
  }
}

# Include deleted questionnaires
query {
  questionnaires(includeDeleted: true) {
    id
    title
    status
    deletedAt
  }
}
```

#### Get Specific Questionnaire
```graphql
query {
  questionnaire(id: "your-questionnaire-id") {
    id
    title
    categoryCode
    status
    isActive
    version
    description
    createdAt
    updatedAt
    publishedAt
    questions {
      id
      key
      type
      label
      helpText
      required
      orderIndex
      constraints
      meta
      options {
        id
        value
        label
        orderIndex
        isOther
      }
    }
  }
}
```

#### Get Active Questionnaire by Category
```graphql
query {
  activeQuestionnaireByCategory(category: "restaurant") {
    id
    title
    categoryCode
    status
    isActive
    version
    publishedAt
  }
}
```

### 3. Update Questionnaire (Draft Only)
```graphql
mutation {
  updateQuestionnaire(id: "your-questionnaire-id", input: {
    title: "Updated Restaurant Feedback Form"
    description: "An updated comprehensive restaurant feedback form"
  }) {
    id
    title
    description
    status
    updatedAt
  }
}
```

### 4. Publish Questionnaire (Draft → Published + Active)
```graphql
mutation {
  publishQuestionnaire(id: "your-questionnaire-id") {
    id
    title
    status
    isActive
    version
    publishedAt
  }
}
```

### 5. Activate Questionnaire (Published → Active)
```graphql
mutation {
  activateQuestionnaire(id: "your-questionnaire-id") {
    id
    title
    status
    isActive
  }
}
```

### 6. Deactivate Questionnaire (Active → Inactive)
```graphql
mutation {
  deactivateQuestionnaire(id: "your-questionnaire-id") {
    id
    title
    status
    isActive
  }
}
```

### 7. Clone Questionnaire (Deep Copy)
```graphql
mutation {
  cloneQuestionnaire(id: "your-questionnaire-id") {
    id
    title
    categoryCode
    status
    isActive
    version
  }
}
```

### 8. Delete Questionnaire (Soft Delete - Draft Only)
```graphql
mutation {
  deleteQuestionnaire(id: "your-questionnaire-id")
}
```

**Response:**
```json
{
  "data": {
    "deleteQuestionnaire": true
  }
}
```

---

## 📧 Enquiry Management

The enquiry system allows customers to submit business enquiries for products and services. Enquiries go through a multi-step process from creation to submission.

### Enquiry States
- **PENDING**: Initial state, can be updated
- **SUBMITTED**: Final state, cannot be updated

### 1. Create Enquiry (Public - No Auth Required)

#### Basic Enquiry
```graphql
mutation {
  createEnquiry(input: {
    venueType: "restaurant"
    venueStyle: "casual"
    productCategory: "beer"
    legalEntityName: "Test Restaurant Pty Ltd"
    tradingName: "Test Restaurant"
    entityType: "company"
    abn: "12345678901"
    outletType: "restaurant"
    businessAddress: "123 Test Street"
    businessCity: "Melbourne"
    businessState: "VIC"
    businessPostalCode: "3000"
    firstName: "John"
    surname: "Doe"
    contactNumber: "0412345678"
    email: "john.doe@test.com"
    referralSourced: "google"
    cuisine: "italian"
    outletStyle: "casual"
    applyCommercialCreditTerms: true
  }) {
    id
    status
    venueType
    venueStyle
    productCategory
    childCategory
    legalEntityName
    tradingName
    email
    createdAt
  }
}
```

**Response:**
```json
{
  "data": {
    "createEnquiry": {
      "id": "2c622453-cdfa-41c0-9949-956cecb01b24",
      "status": "PENDING",
      "venueType": "restaurant",
      "venueStyle": "casual",
      "productCategory": "beer",
      "childCategory": null,
      "legalEntityName": "Test Restaurant Pty Ltd",
      "tradingName": "Test Restaurant",
      "email": "john.doe@test.com",
      "createdAt": "2025-09-16T13:34:36.506539+00:00"
    }
  }
}
```

#### Complete Enquiry with All Fields
```graphql
mutation {
  createEnquiry(input: {
    venueType: "bar"
    venueStyle: "sports"
    productCategory: "wine"
    childCategory: "red-wine"
    legalEntityName: "Test Bar Pty Ltd"
    tradingName: "Test Bar"
    entityType: "company"
    abn: "98765432109"
    acn: "123456789"
    liquorLicenseNumber: "LL123456"
    outletType: "bar"
    businessAddress: "456 Test Avenue"
    businessCity: "Sydney"
    businessState: "NSW"
    businessPostalCode: "2000"
    firstName: "Jane"
    surname: "Smith"
    contactNumber: "0498765432"
    email: "jane.smith@test.com"
    unitNumber: "Unit 5"
    streetNumber: "456"
    streetName: "Test Avenue"
    referralSourced: "facebook"
    cuisine: "australian"
    outletStyle: "sports"
    applyCommercialCreditTerms: false
    applicationId: 12345
  }) {
    id
    status
    venueType
    productCategory
    childCategory
    legalEntityName
    tradingName
    email
  }
}
```

### 2. Query Enquiry (Public - No Auth Required)

#### Get Enquiry by ID
```graphql
query {
  enquiryPublic(id: "2c622453-cdfa-41c0-9949-956cecb01b24") {
    id
    status
    venueType
    venueStyle
    productCategory
    childCategory
    legalEntityName
    tradingName
    entityType
    abn
    acn
    liquorLicenseNumber
    outletType
    businessAddress
    businessCity
    businessState
    businessPostalCode
    firstName
    surname
    contactNumber
    email
    unitNumber
    streetNumber
    streetName
    referralSourced
    cuisine
    outletStyle
    applyCommercialCreditTerms
    applicationId
    questionnaireId
    questionnaireVersion
    questionnaireTitle
    answersJson
    submittedAt
    createdAt
    updatedAt
    ipAddress
    userAgent
  }
}
```

**Response:**
```json
{
  "data": {
    "enquiryPublic": {
      "id": "2c622453-cdfa-41c0-9949-956cecb01b24",
      "status": "PENDING",
      "venueType": "restaurant",
      "venueStyle": "casual",
      "productCategory": "beer",
      "childCategory": null,
      "legalEntityName": "Test Restaurant Pty Ltd",
      "tradingName": "Test Restaurant",
      "email": "john.doe@test.com",
      "createdAt": "2025-09-16T13:34:36.506539+00:00",
      "submittedAt": null,
      "questionnaireId": null,
      "answersJson": null
    }
  }
}
```

### 3. Update Enquiry (Public - No Auth Required)

**Note:** Only PENDING enquiries can be updated. SUBMITTED enquiries are immutable.

#### Update Basic Fields
```graphql
mutation {
  updateEnquiry(id: "2c622453-cdfa-41c0-9949-956cecb01b24", input: {
    venueStyle: "fine-dining"
    productCategory: "wine"
    childCategory: "red-wine"
    cuisine: "french"
    outletStyle: "upscale"
  }) {
    id
    status
    venueType
    venueStyle
    productCategory
    childCategory
    cuisine
    outletStyle
    updatedAt
  }
}
```

**Response:**
```json
{
  "data": {
    "updateEnquiry": {
      "id": "2c622453-cdfa-41c0-9949-956cecb01b24",
      "status": "PENDING",
      "venueType": "restaurant",
      "venueStyle": "fine-dining",
      "productCategory": "wine",
      "childCategory": "red-wine",
      "cuisine": "french",
      "outletStyle": "upscale",
      "updatedAt": "2025-09-16T13:35:45.123456+00:00"
    }
  }
}
```

#### Update Contact Information
```graphql
mutation {
  updateEnquiry(id: "2c622453-cdfa-41c0-9949-956cecb01b24", input: {
    firstName: "John"
    surname: "Smith"
    contactNumber: "0412345678"
    email: "john.smith@test.com"
    businessAddress: "789 New Street"
    businessCity: "Brisbane"
    businessState: "QLD"
    businessPostalCode: "4000"
  }) {
    id
    firstName
    surname
    contactNumber
    email
    businessAddress
    businessCity
    businessState
    businessPostalCode
  }
}
```

### 4. Submit Enquiry (Public - No Auth Required)

Submit an enquiry with questionnaire data. This changes the status from PENDING to SUBMITTED.

```graphql
mutation {
  submitEnquiry(
    id: "2c622453-cdfa-41c0-9949-956cecb01b24"
    questionnaireId: "550e8400-e29b-41d4-a716-446655440000"
    questionnaireVersion: 1
    questionnaireTitle: "Product Interest Questionnaire"
    answers: "{\"question1\": \"answer1\", \"question2\": \"answer2\", \"question3\": \"answer3\"}"
  ) {
    id
    status
    submittedAt
    questionnaireId
    questionnaireVersion
    questionnaireTitle
    answersJson
  }
}
```

**Response:**
```json
{
  "data": {
    "submitEnquiry": {
      "id": "2c622453-cdfa-41c0-9949-956cecb01b24",
      "status": "SUBMITTED",
      "submittedAt": "2025-09-16T13:35:14.657159+00:00",
      "questionnaireId": "550e8400-e29b-41d4-a716-446655440000",
      "questionnaireVersion": 1,
      "questionnaireTitle": "Product Interest Questionnaire",
      "answersJson": "{\"question1\": \"answer1\", \"question2\": \"answer2\", \"question3\": \"answer3\"}"
    }
  }
}
```

### 5. Enquiry Input Types

#### EnquiryInput (for createEnquiry)
```graphql
input EnquiryInput {
  # Required fields
  venueType: String!
  productCategory: String!
  
  # Optional fields
  venueStyle: String
  childCategory: String
  legalEntityName: String
  tradingName: String
  entityType: String
  abn: String
  acn: String
  liquorLicenseNumber: String
  outletType: String
  businessAddress: String
  businessCity: String
  businessState: String
  businessPostalCode: String
  firstName: String
  surname: String
  contactNumber: String
  email: String
  unitNumber: String
  streetNumber: String
  streetName: String
  referralSourced: String
  cuisine: String
  outletStyle: String
  applyCommercialCreditTerms: Boolean = false
  applicationId: Int
}
```

#### EnquiryUpdateInput (for updateEnquiry)
```graphql
input EnquiryUpdateInput {
  # All fields optional for updates
  venueType: String
  venueStyle: String
  productCategory: String
  childCategory: String
  legalEntityName: String
  tradingName: String
  entityType: String
  abn: String
  acn: String
  liquorLicenseNumber: String
  outletType: String
  businessAddress: String
  businessCity: String
  businessState: String
  businessPostalCode: String
  firstName: String
  surname: String
  contactNumber: String
  email: String
  unitNumber: String
  streetNumber: String
  streetName: String
  referralSourced: String
  cuisine: String
  outletStyle: String
  applyCommercialCreditTerms: Boolean
  applicationId: Int
}
```

### 6. Enquiry Business Rules

#### Data Validation
- **Email Uniqueness**: Each email can only be used once per enquiry
- **Required Fields**: `venueType` and `productCategory` are mandatory
- **Status Transitions**: PENDING → SUBMITTED (one-way only)

#### Update Restrictions
- Only PENDING enquiries can be updated
- SUBMITTED enquiries are immutable
- Attempting to update a SUBMITTED enquiry returns an error

#### Error Handling
```json
{
  "data": null,
  "errors": [
    {
      "message": "Only pending enquiries can be updated",
      "locations": [{"line": 1, "column": 12}],
      "path": ["updateEnquiry"]
    }
  ]
}
```

#### Duplicate Email Error
```json
{
  "data": null,
  "errors": [
    {
      "message": "duplicate key value violates unique constraint \"enquiries_email_key\"",
      "locations": [{"line": 1, "column": 12}],
      "path": ["createEnquiry"]
    }
  ]
}
```

### 7. Complete Enquiry Workflow

#### Step 1: Create Enquiry
```graphql
mutation {
  createEnquiry(input: {
    venueType: "restaurant"
    productCategory: "beer"
    email: "customer@example.com"
    # ... other fields
  }) {
    id
    status
  }
}
```

#### Step 2: Update Enquiry (Optional)
```graphql
mutation {
  updateEnquiry(id: "enquiry-id", input: {
    venueStyle: "casual"
    childCategory: "craft-beer"
    # ... other updates
  }) {
    id
    status
  }
}
```

#### Step 3: Submit Enquiry
```graphql
mutation {
  submitEnquiry(
    id: "enquiry-id"
    questionnaireId: "questionnaire-id"
    questionnaireVersion: 1
    questionnaireTitle: "Product Questionnaire"
    answers: "{\"questions\": \"answers\"}"
  ) {
    id
    status
    submittedAt
  }
}
```

#### Step 4: Query Final Enquiry
```graphql
query {
  enquiryPublic(id: "enquiry-id") {
    id
    status
    submittedAt
    questionnaireId
    answersJson
    # ... all other fields
  }
}
```

---

## 📝 Question Types Reference

### 1. SINGLE (Radio Buttons)
**Use for:** Gender, Rating, Age groups, etc.
**UI:** User selects ONE option from multiple choices

```graphql
{
  key: "gender"
  type: SINGLE
  label: "What is your gender?"
  required: true
  orderIndex: 1
  options: [
    {value: "male", label: "Male", orderIndex: 1}
    {value: "female", label: "Female", orderIndex: 2}
    {value: "other", label: "Other", orderIndex: 3}
  ]
}
```

### 2. MULTI (Checkboxes)
**Use for:** Hobbies, Interests, Features, etc.
**UI:** User can select MULTIPLE options

```graphql
{
  key: "interests"
  type: MULTI
  label: "What are your interests? (Select all that apply)"
  required: false
  orderIndex: 1
  options: [
    {value: "sports", label: "Sports", orderIndex: 1}
    {value: "music", label: "Music", orderIndex: 2}
    {value: "movies", label: "Movies", orderIndex: 3}
    {value: "reading", label: "Reading", orderIndex: 4}
  ]
}
```

### 3. BOOLEAN (Yes/No)
**Use for:** Newsletter subscription, Terms acceptance, etc.
**UI:** Toggle switch or Yes/No buttons

```graphql
{
  key: "newsletter"
  type: BOOLEAN
  label: "Would you like to receive our newsletter?"
  required: true
  orderIndex: 1
}
```

### 4. SCALE (Rating Scale)
**Use for:** Satisfaction ratings, Likert scales, etc.
**UI:** Slider or numbered scale

```graphql
{
  key: "satisfaction"
  type: SCALE
  label: "How satisfied are you with our service? (1-10)"
  required: true
  orderIndex: 1
  constraints: {
    "min": 1,
    "max": 10,
    "step": 1
  }
}
```

### 5. NUMBER (Numeric Input)
**Use for:** Age, Quantity, Frequency, etc.
**UI:** Number input field

```graphql
{
  key: "age"
  type: NUMBER
  label: "What is your age?"
  required: true
  orderIndex: 1
  constraints: {
    "min": 18,
    "max": 100
  }
}
```

### 6. TEXT (Free Text)
**Use for:** Comments, Feedback, Open-ended questions
**UI:** Text area or input field

```graphql
{
  key: "comments"
  type: TEXT
  label: "Any additional comments or suggestions?"
  required: false
  orderIndex: 1
}
```

### 7. CHIPS (Tag Selection)
**Use for:** Skills, Colors, Tags, etc.
**UI:** Tag-style selection

```graphql
{
  key: "skills"
  type: CHIPS
  label: "What are your technical skills?"
  required: false
  orderIndex: 1
  options: [
    {value: "javascript", label: "JavaScript", orderIndex: 1}
    {value: "python", label: "Python", orderIndex: 2}
    {value: "react", label: "React", orderIndex: 3}
    {value: "nodejs", label: "Node.js", orderIndex: 4}
  ]
}
```

---

## ⚠️ Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "data": null,
  "errors": [
    {
      "message": "No token provided",
      "locations": [{"line": 2, "column": 5}],
      "path": ["createQuestionnaire"]
    }
  ]
}
```

#### 403 Forbidden
```json
{
  "data": null,
  "errors": [
    {
      "message": "Insufficient permissions",
      "locations": [{"line": 2, "column": 5}],
      "path": ["createQuestionnaire"]
    }
  ]
}
```

#### 400 Bad Request
```json
{
  "data": null,
  "errors": [
    {
      "message": "Only draft questionnaires can be updated",
      "locations": [{"line": 2, "column": 5}],
      "path": ["updateQuestionnaire"]
    }
  ]
}
```

#### 404 Not Found
```json
{
  "data": null,
  "errors": [
    {
      "message": "Questionnaire not found",
      "locations": [{"line": 2, "column": 5}],
      "path": ["updateQuestionnaire"]
    }
  ]
}
```

---

## 🔄 Sample Workflows

### Complete Questionnaire Lifecycle

#### 1. Login and Get Token
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { loginAdminUser(loginInput: {email: \"admin@example.com\", password: \"admin123\"}) { accessToken } }"}'
```

#### 2. Create Questionnaire
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "mutation { createQuestionnaire(input: {categoryCode: \"restaurant\", title: \"Restaurant Feedback Form\", description: \"A comprehensive feedback form\", questions: [{key: \"rating\", type: SCALE, label: \"Rate your experience\", required: true, orderIndex: 1}]) { id title status } }"}'
```

#### 3. Update Questionnaire
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "mutation { updateQuestionnaire(id: \"QUESTIONNAIRE_ID\", input: {title: \"Updated Restaurant Form\"}) { id title } }"}'
```

#### 4. Publish Questionnaire
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "mutation { publishQuestionnaire(id: \"QUESTIONNAIRE_ID\") { id title status isActive } }"}'
```

#### 5. Get Active Questionnaire
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "query { activeQuestionnaireByCategory(category: \"restaurant\") { id title status isActive } }"}'
```

### Complete Enquiry Lifecycle

#### 1. Create Enquiry
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createEnquiry(input: { venueType: \"restaurant\", productCategory: \"beer\", legalEntityName: \"Test Restaurant Pty Ltd\", tradingName: \"Test Restaurant\", email: \"customer@example.com\", firstName: \"John\", surname: \"Doe\" }) { id status venueType productCategory email } }"}'
```

#### 2. Update Enquiry (Optional)
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { updateEnquiry(id: \"ENQUIRY_ID\", input: { venueStyle: \"casual\", childCategory: \"craft-beer\", cuisine: \"italian\" }) { id status venueStyle childCategory cuisine } }"}'
```

#### 3. Submit Enquiry
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { submitEnquiry(id: \"ENQUIRY_ID\", questionnaireId: \"QUESTIONNAIRE_ID\", questionnaireVersion: 1, questionnaireTitle: \"Product Questionnaire\", answers: \"{\\\"question1\\\": \\\"answer1\\\"}\") { id status submittedAt } }"}'
```

#### 4. Query Final Enquiry
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { enquiryPublic(id: \"ENQUIRY_ID\") { id status venueType productCategory email submittedAt questionnaireId answersJson } }"}'
```

---

## 🎯 Business Rules

### Questionnaire States
- **DRAFT**: Can be edited, updated, deleted, or published
- **PUBLISHED**: Can be activated, deactivated, or cloned
- **ARCHIVED**: Read-only, cannot be modified

### Enquiry States
- **PENDING**: Can be updated, queried, or submitted
- **SUBMITTED**: Read-only, cannot be updated or modified

### Permissions
- **SUPERADMIN**: Full access to everything
- **EDITOR**: Can manage questionnaires (create, update, delete, publish, etc.)
- **VIEWER**: Read-only access (queries only)

### Constraints
- Only one active questionnaire per category
- Only draft questionnaires can be edited/deleted
- Publishing automatically activates the questionnaire
- Cloning creates a new draft with all questions and options

---

## 🚀 Quick Start

1. **Start the server**: `docker-compose up -d`
2. **Get JWT token**: Use login mutation
3. **Create questionnaire**: Use createQuestionnaire mutation
4. **Publish questionnaire**: Use publishQuestionnaire mutation
5. **Get active questionnaire**: Use activeQuestionnaireByCategory query

**GraphQL Playground**: http://localhost:8000/graphql

---

## 📞 Support

For questions or issues, please refer to the GraphQL schema introspection:
```graphql
query {
  __schema {
    types {
      name
      description
    }
  }
}
```
