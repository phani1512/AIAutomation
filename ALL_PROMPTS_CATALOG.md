# Complete Prompts Catalog

**Generated:** November 27, 2025  
**Total Datasets:** 4  
**Total Unique Prompts:** 1,619  
**Purpose:** Comprehensive reference of all available prompts for AI-powered Selenium code generation

---

## Table of Contents

1. [Dataset Overview](#dataset-overview)
2. [Common Web Actions Prompts](#common-web-actions-prompts-40-prompts)
3. [Sircon UI Application Prompts](#sircon-ui-application-prompts-1579-prompts)
   - [Login & Authentication](#login--authentication)
   - [Form Inputs](#form-inputs)
   - [Navigation & Clicks](#navigation--clicks)
   - [Data Retrieval](#data-retrieval)
   - [Verification & Validation](#verification--validation)
4. [Selenium Methods Reference](#selenium-methods-reference-111-usage-patterns)
5. [Element Locator Patterns](#element-locator-patterns-21-patterns)
6. [Prompt Usage Guidelines](#prompt-usage-guidelines)

---

## Dataset Overview

| Dataset | Type | Entries | Prompts | Weight | Purpose |
|---------|------|---------|---------|--------|---------|
| **selenium-methods-dataset.json** | API Reference | 111 | 111 usage patterns | 1.0x | Selenium WebDriver API methods |
| **common-web-actions-dataset.json** | Generic UI | 23 | 40 prompts (39 unique) | 1.5x | Universal web patterns with placeholders |
| **element-locator-patterns.json** | Locator Strategies | 21 | 21 patterns | 1.2x | HTML element location examples |
| **sircon_ui_dataset.json** | Application-Specific | 1,582 | 1,579 prompts | 2.0x | Real-world Sircon insurance platform |

**Total Corpus:** 1,737 entries → 468,602 tokens → Trained AI Model

---

## Common Web Actions Prompts (40 Prompts)

**Purpose:** Generic web automation patterns covering common UI interactions

**Pattern Types:**
- Navigation (URLs)
- Form Input (text, email, password)
- Search Functionality
- Dropdown Selection
- Checkbox/Radio Selection
- File Upload
- Modal Dialogs
- Tab Navigation
- Alert Handling
- Hover Menus
- Form Validation
- Scroll Interactions
- Dynamic Content Wait
- Table Data Extraction
- Button Clicks

### **Navigation & Basic Input**

#### 1. Navigate to URL
**Prompt:** `navigate to {URL}`
- **Action:** navigate
- **Code:** `driver.get("{URL}");`

#### 2. Username Input
**Prompt:** `enter {USERNAME} in username field`
- **Action:** sendKeys
- **Locator:** By.id("username")

#### 3-5. Login Fields (Existing)
**Prompts:**
- `enter email in producer-email field`
- `enter password in producer-password field`
- `click producer login button`

### **Search Patterns**

#### 6. Search Box Click
**Prompt:** `click search box`

#### 7. Search Query Input
**Prompt:** `enter {SEARCH_QUERY} in search box`

#### 8. Search Submit
**Prompt:** `click search button`

### **Dropdown & Selection**

#### 9. Dropdown Click
**Prompt:** `click country dropdown`

#### 10. Dropdown Select
**Prompt:** `select United States from country dropdown`

#### 11-12. Checkboxes
**Prompts:**
- `click terms checkbox`
- `click newsletter checkbox`

#### 13. Radio Button
**Prompt:** `select male radio button`

### **File Upload**

#### 14. File Input
**Prompt:** `upload file {FILE_PATH}`

#### 15. Upload Submit
**Prompt:** `click upload button`

### **Modal Interactions**

#### 16-19. Modal Workflow
**Prompts:**
- `click open modal button`
- `wait for modal to appear`
- `enter {TEXT} in modal input`
- `click confirm button`

### **Tab & Window Navigation**

#### 20-21. Tab Switching
**Prompts:**
- `click open new tab link`
- `switch to new tab`

### **Alert Handling**

#### 22-23. Alert Workflow
**Prompts:**
- `click alert button`
- `accept alert`

### **Hover Menu Navigation**

#### 24-26. Hover Menu Workflow
**Prompts:**
- `hover over main menu`
- `wait for submenu to appear`
- `click submenu item`

### **Form Validation**

#### 27-28. Validation Check
**Prompts:**
- `click submit button`
- `verify error message`

### **Scroll Interactions**

#### 29-30. Scroll & Click
**Prompts:**
- `scroll to footer`
- `click footer link`

### **Dynamic Content**

#### 31-33. AJAX Wait Pattern
**Prompts:**
- `click load data button`
- `wait for data to load`
- `verify data rows exist`

### **Table Extraction**

#### 34-35. Table Data
**Prompts:**
- `find data table`
- `extract table rows`

### **Form Fields**

#### 36-40. Additional Input Fields
**Prompts:**
- `enter {FIRST_NAME} in first name field`
- `enter {LAST_NAME} in last name field`
- `enter {PHONE} in phone field`
- `click next button`
- `click submit button`

---

## Sircon UI Application Prompts (1,579 Prompts)

### Login & Authentication

1. `enter pvalaboju@vertafore.com in producer-email field`
2. `enter Phanindraa$1215 in producer-password`
3. `click on producer-login`
4. `click the sign in button`
5. `click the sign up now link`
6. `verify username is displayed`
7. `verify password input is displayed`
8. `click the business tab element`
9. `click the get help signing in link`
10. `click get help signing in`

### Form Inputs

#### **Text Input Fields**

11. `enter {NAME} in first name field`
12. `enter {NAME} in last name field`
13. `enter {EMAIL} in email address field`
14. `enter {PASSWORD} in password field`
15. `enter {PASSWORD} in confirm password field`
16. `enter {PHONE} in phone number field`
17. `enter text in phone number field`
18. `enter text in phone extension field`
19. `enter {ADDRESS} in address line one field`
20. `enter {ADDRESS_LINE2} in address line two field`
21. `enter {CITY} in city field`
22. `enter {STATE} in state field`
23. `enter {ZIPCODE} in zip code field`
24. `enter {TEXT} in ein field`
25. `enter {TEXT} in crd number field`
26. `enter {NAME} in organization name field`
27. `enter text in ssn field`
28. `enter text in national producer number field`
29. `enter text in resident license number field`
30. `enter text in resident license state field`
31. `enter text in search field`
32. `enter text in quick search field`
33. `enter text in custom cost center field`
34. `enter text in add cost center field`
35. `enter text in email text body field`
36. `enter text in email address field`
37. `enter text in effective start date field`
38. `enter text in effective end date field`
39. `enter {DATE} in effective start date`
40. `enter {DATE} in effective end date`
41. `type {PHONE} into phone number`
42. `enter {COMPANY_NAME} in company name field`
43. `enter {AMOUNT} in amount field`
44. `enter {TEXT} in search box`

#### **Dropdown/Select Fields**

45. `enter text in state dropdown field`
46. `enter text in search by dropdown field`
47. `select None from preferred delivery method dropdown`
48. `retrieve resident state from IndividualSignUpPage`
49. `retrieve role from HierarchiesPage`
50. `click the payment state dropdown dropdown`

#### **Date Fields**

51. `click the card expiration date input`
52. `click the atid finra filing date input`
53. `wait for profile name to be visible`

### Navigation & Clicks

#### **Button Clicks**

54. `click the cancel button`
55. `click the search button`
56. `click the continue button`
57. `click the submit button`
58. `click the save button`
59. `click the approve oba button`
60. `click the reject oba button`
61. `click the request more info button`
62. `click the already reported button`
63. `click the do not report button`
64. `click the search again link`
65. `click the view all licenses link`
66. `click the view all activity link`
67. `click the view all actions button`
68. `click the upgrade to premium button`
69. `click the confirm and continue button`
70. `click the save and exit button`
71. `click the ce change button`
72. `click the all licenses button`
73. `click the expand contract button`
74. `click the switch menu button`
75. `click the learn more about premium button`
76. `click the find courses button`
77. `click the apply for license button`
78. `click the review and confirm button`
79. `click send request to confirm`
80. `click overlay ok`
81. `click the overlay ok button`
82. `click the submission ok button`
83. `click the confirm o a continue button`
84. `click the confirm and continue button`
85. `click the save overlay ok button`
86. `click the cancel overlay save changes button`
87. `click the cancel overlay cancel without saving button`
88. `click the cancel filing task without saving button`
89. `click the update activity continue button`

#### **Link Clicks**

90. `click the agency get help signing in link`
91. `click the learn more about cost centers link`
92. `click the configure message center link`
93. `click the back to settings page link`
94. `click the reporting link`
95. `click the signup for premium link`
96. `click the quick search result producer name link`
97. `click the external link arrow link`
98. `click external link arrow`
99. `click the view workflow details link`
100. `click view all oba for this advisor`
101. `click the view all oba for this advisor link`

#### **Tab/Menu Navigation**

102. `click the business tab`
103. `click the services tab element`
104. `click the profile menu menu`
105. `click the switch menu options menu`
106. `click the ellipsis element`
107. `click the elipsus button`
108. `click the activity requests element`
109. `click the activity request menu menu`
110. `click the view carrier request element`
111. `click the edit pencil element`
112. `click edit pencil`
113. `click the security roles element`

#### **Dropdown/Modal Actions**

114. `click the dropdown menu dropdown`
115. `click confirm activity dialog`
116. `click the confirm activity dialog dialog`
117. `click the update activity dialog dialog`
118. `click the submit update activity dialog dialog`
119. `click request associate confirmation dialog`
120. `wait for edit role access permissions dialog to be visible`

#### **Checkbox/Radio Selections**

121. `click the acknowledge flagged items checkbox checkbox`
122. `click the attestations check box checkbox`
123. `click the yes radio button`
124. `click the no radio button`
125. `click the file with f i n r a_ y e s element`

#### **Special Actions**

126. `click the username input`
127. `click the password input`
128. `click the payment iframe element`
129. `click the payment credit card number text box input`
130. `click the payment first name text box input`
131. `click the payment last name text box input`
132. `click the payment address line1 text box input`
133. `click the payment city text box input`
134. `click the us postal code input`
135. `click the billing phone input`
136. `click the payment email text box input`
137. `click the atid reviewer general comments input`
138. `click the already reported internal comments input`
139. `click the do not report internal comments input`
140. `click the activity reported date element`
141. `click the method of reporting dropdown`
142. `click the already reported internal comments input`

### Data Retrieval

#### **Get Text Operations**

143. `get text from info message text`
144. `get text from branded logo`
145. `get text from branded carrier intro`
146. `get text from page header`
147. `get text from widget title`
148. `get text from account information`
149. `get text from first name`
150. `get text from last name`
151. `get text from email address`
152. `get text from confirm email address`
153. `get text from phone number`
154. `get text from phone extension`
155. `get text from current password`
156. `get text from confirm new password`
157. `get text from confirm new password confirm`
158. `get text from activities`
159. `get text from carriers table`
160. `get text from users`
161. `get text from services content`
162. `get text from email notifications content`
163. `get text from password expiration content`
164. `get text from billing profile content`
165. `enter text in cost center content field`
166. `get text from invoices content`
167. `get text from summary administrative details`
168. `get text from summary organization details`
169. `get text from summary billing information`
170. `get text from email instructions`
171. `get text from preview and send email content`
172. `get text from search agent found message`
173. `get text from body`
174. `get text from carrier`
175. `get text from instructions`
176. `get text from user info name`
177. `get text from quick search results popup`
178. `get text from user roles`
179. `get text from role entity type column`
180. `get text from hierarchy name column`
181. `get text from resident license state`
182. `get text from resident license number`
183. `get text from license widget status codes`
184. `get text from dashboard page links`
185. `get text from licenses active count`
186. `get text from licenses inactive count`
187. `get text from state service types`
188. `get text from license list`
189. `get text from ce resident state text`
190. `get text from ce widget`
191. `get text from subscription current level`
192. `get text from communication preferences expiration`
193. `get text from profile name`
194. `get text from profile email`
195. `get text from oba type`
196. `get text from user permissions text`

#### **Get Attribute/Count Operations**

197. `get count of edit pencil`
198. `get attribute from security roles`

### Verification & Validation

#### **Is Displayed Checks**

199. `verify page errors is present`
200. `verify username is displayed`
201. `verify user name input is present`
202. `verify submit is present`
203. `verify agency licenses label is present`
204. `verify search again is displayed`
205. `verify connected license fee message is displayed`
206. `verify cancel is displayed`
207. `verify search is displayed`
208. `verify save is displayed`
209. `verify view all licenses is displayed`
210. `verify apply for license is displayed`
211. `verify find courses is displayed`
212. `verify view my transcripts is displayed`
213. `verify ce change is displayed`
214. `verify course requirement is displayed`
215. `verify learn more about premium is displayed`
216. `verify signup for premium is displayed`
217. `verify upgrade to premium is displayed`
218. `verify known element on is displayed`
219. `verify recent activity widget is displayed`
220. `verify quick links widget is displayed`
221. `verify licenses widget is displayed`
222. `verify workqueue widget is displayed`
223. `verify carrier req milestone widget is displayed`
224. `verify contact info widget is displayed`
225. `verify documents widget is displayed`
226. `verify app all activity list is displayed`
227. `verify oba widget is displayed`
228. `verify oba report is present`
229. `verify pst report is present`
230. `verify registrations report is present`
231. `verify gne report is present`
232. `verify disclosure summary is displayed`
233. `verify approve comments panel is displayed`
234. `verify request more info comments panel is displayed`
235. `verify disclosure filing comments is displayed`
236. `verify pending confirmation warning is displayed`
237. `verify review and confirm is displayed`

#### **Element Found/Visible Checks**

238. `verify search agent not found message is present`
239. `wait for edit role access permissions dialog to be visible`

---

## Selenium Methods Reference (111 Usage Patterns)

These patterns represent Selenium WebDriver API method signatures and their usage:

### **Navigation Actions**
1. Navigate to URL
2. Navigation completed
3. Get current page URL
4. Current URL retrieved
5. Get page title
6. Page title retrieved
7. Navigate to previous page
8. Back navigation completed
9. Navigate to next page
10. Forward navigation completed
11. Refresh current page
12. Page refresh completed
13. Navigate to URL using Navigation
14. Navigation to URL completed

### **Element Interaction Actions**
15. Click on button, link, or interactive element
16. Click action completed
17. Type text into input field
18. Text input completed
19. Clear input field content
20. Clear action completed
21. Submit form
22. Form submission completed
23. Select dropdown option
24. Dropdown selection completed

### **Element Query Actions**
25. Get element text
26. Text retrieval completed
27. Check if element is displayed
28. Element visibility checked
29. Check if element is enabled
30. Element enabled state checked
31. Check if element is selected
32. Element selected state checked
33. Get element attribute value
34. Attribute value retrieved
35. Get CSS property value
36. CSS property retrieved
37. Get element tag name
38. Tag name retrieved
39. Get element location
40. Location retrieved
41. Get element size
42. Size retrieved
43. Get element rectangle
44. Rectangle retrieved

### **Finding Elements**
45. Find element by ID
46. Find element by name
47. Find element by class name
48. Find element by tag name
49. Find element by CSS selector
50. Find element by XPath
51. Find element by link text
52. Find element by partial link text
53. Find multiple elements
54. Element search completed

### **Window/Frame Handling**
55. Get window handle
56. Window handle retrieved
57. Get all window handles
58. Window handles retrieved
59. Switch to window
60. Window switch completed
61. Switch to frame
62. Frame switch completed
63. Switch to parent frame
64. Parent frame switch completed
65. Switch to default content
66. Default content switch completed
67. Close window
68. Window closed
69. Quit browser
70. Browser quit completed

### **Alert Handling**
71. Accept alert
72. Alert accepted
73. Dismiss alert
74. Alert dismissed
75. Get alert text
76. Alert text retrieved
77. Send keys to alert
78. Alert input completed

### **JavaScript Execution**
79. Execute JavaScript
80. JavaScript execution completed
81. Execute async JavaScript
82. Async JavaScript execution completed

### **Screenshot & Logs**
83. Take screenshot
84. Screenshot captured
85. Get browser logs
86. Logs retrieved

### **Waits**
87. Implicit wait
88. Explicit wait
89. Fluent wait
90. Wait for element visible
91. Wait for element clickable
92. Wait for element invisible
93. Wait for element staleness
94. Wait for text present
95. Wait for alert present
96. Wait for frame available
97. Wait for window count

### **Mouse & Keyboard Actions**
98. Click and hold
99. Release mouse
100. Double click
101. Right click (context click)
102. Move to element
103. Drag and drop
104. Keyboard press key
105. Keyboard release key
106. Send keys to active element

### **Cookie Management**
107. Add cookie
108. Get cookie
109. Get all cookies
110. Delete cookie
111. Delete all cookies

---

## Element Locator Patterns (21 Patterns)

These patterns demonstrate element identification strategies:

### **Input Elements**
1. Text input (id, name, class, CSS, XPath) → sendKeys
2. Textarea (id, name, tag, XPath) → sendKeys
3. File input (id, name, CSS, XPath) → sendKeys
4. Password input (id, type, CSS, XPath) → sendKeys

### **Button Elements**
5. Submit button (id, CSS, class, XPath) → click
6. Button by text (id, XPath text match) → click

### **Link Elements**
7. Link by ID (id, linkText, partialLinkText, CSS, XPath) → click
8. Link by href (CSS selector) → click

### **Selection Elements**
9. Dropdown/Select (id, name, class, XPath) → select
10. Checkbox (id, name, CSS, XPath) → click
11. Radio button (id, CSS value, XPath) → click

### **Display Elements**
12. Div (id, class, CSS, XPath) → getText
13. Span (class, CSS data-attribute, XPath) → getText
14. Error message div (id, class, CSS, XPath) → getText

### **Media Elements**
15. Image (id, class, CSS alt, XPath) → getAttribute

### **Structured Elements**
16. Table (id, class, tag, XPath) → findElements
17. List (ul) (id, class, tag, XPath) → findElements
18. List item (li) → text matching

### **Complex Elements**
19. Nested elements (parent-child relationships)
20. Dynamic elements (data attributes, ARIA labels)
21. Shadow DOM elements (special selectors)

---

## Prompt Usage Guidelines

### **1. Basic Prompts**
Simple, single-action prompts that generate standalone Selenium code:

```
Prompt: "click the sign in button"
Generated:
WebElement signInButton = driver.findElement(By.cssSelector("[Label='Sign In']"));
signInButton.click();
```

### **2. Placeholder-Enhanced Prompts**
Prompts using placeholders for reusable test data:

```
Prompt: "enter {EMAIL} in email address field"
Generated:
WebElement emailField = driver.findElement(By.id("email-address"));
emailField.sendKeys("{EMAIL}");
```

**Available Placeholders:**
- `{EMAIL}` - Email addresses
- `{PASSWORD}` - Passwords
- `{USERNAME}` - Usernames
- `{NAME}` - Generic names
- `{FIRST_NAME}` - First names
- `{LAST_NAME}` - Last names
- `{ADDRESS}` - Street addresses
- `{ADDRESS_LINE2}` - Secondary address
- `{CITY}` - City names
- `{STATE}` - State/region
- `{ZIPCODE}` - Postal codes
- `{PHONE}` - Phone numbers
- `{DATE}` - Dates
- `{AMOUNT}` - Numeric amounts
- `{COMPANY_NAME}` - Company names
- `{TEXT}` - Generic text
- `{URL}` - URLs
- `{SEARCH_QUERY}` - Search terms

### **3. Multi-Step Prompts**
Complex prompts combining multiple actions:

```
Prompt: "enter pvalaboju@vertafore.com in producer-email field and enter Phanindraa$1215 in producer-password and click on producer-login"

Generated:
// Step 1: enter pvalaboju@vertafore.com in producer-email field
WebElement inputField = driver.findElement(By.id("producer-email"));
inputField.sendKeys("pvalaboju@vertafore.com");

// Step 2: enter Phanindraa$1215 in producer-password
WebElement inputField = driver.findElement(By.id("producer-password"));
inputField.sendKeys("Phanindraa$1215");

// Step 3: click on producer-login
WebElement element = driver.findElement(By.xpath("//button[@type=\"submit\" and contains(@class, \"primary-btn\")]"));
element.click();
```

### **4. Verification Prompts**
Prompts that check element state:

```
Prompt: "verify username is displayed"
Generated:
WebElement usernameField = driver.findElement(By.id("username"));
boolean isDisplayed = usernameField.isDisplayed();
```

### **5. Data Retrieval Prompts**
Prompts that extract information:

```
Prompt: "get text from user info name"
Generated:
WebElement userInfoName = driver.findElement(By.id("userInfoName"));
String text = userInfoName.getText();
```

### **Best Practices**

✅ **DO:**
- Use specific, descriptive field names
- Include action verbs (click, enter, get, verify)
- Combine related steps with "and"
- Use placeholders for test data
- Specify element types when ambiguous

❌ **DON'T:**
- Use vague terms like "that thing"
- Mix unrelated actions in one prompt
- Hardcode sensitive data (use placeholders)
- Assume element locations (be specific)

### **Example Workflows**

**Complete Login Flow:**
```
enter {EMAIL} in producer-email field and enter {PASSWORD} in producer-password and click on producer-login
```

**Form Submission:**
```
enter {FIRST_NAME} in first name field and enter {LAST_NAME} in last name field and enter {EMAIL} in email address field and click the submit button
```

**Search Functionality:**
```
enter {SEARCH_QUERY} in search field and click the search button and get text from search results
```

**Profile Verification:**
```
verify username is displayed and get text from user info name and verify subscription current level is displayed
```

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Datasets** | 4 |
| **Total Entries** | 1,737 |
| **Unique Prompts** | 1,582 |
| **Usage Patterns** | 111 |
| **Locator Strategies** | 21 |
| **Total Tokens** | 468,295 |
| **Unique Vocabulary** | 4,281 |
| **Model Perplexity** | 1.70 |

---

## Related Documentation

- **DATASET_STATUS_REPORT.md** - Comprehensive dataset analysis and verification
- **DATASETS_QUICK_REFERENCE.md** - Quick reference card with examples
- **TRAINING_SUMMARY.md** - Training process and model statistics
- **WEB_INTERFACE_GUIDE.md** - Web interface usage guide

---

**Last Updated:** November 27, 2025  
**Model Version:** selenium_ngram_model.pkl (815 KB)  
**Tokenizer:** cl100k_base (GPT-4 BPE)
