# 🔧 Self-Healing Quick Reference Guide

## 🎯 What You Need to Know

### Visual Highlighting (Phase 4)
When an element is healed during test execution, you'll see:

**✨ Visual Indicators:**
- 🟢 **Green border** = High confidence (≥80%) - Auto-approved!
- 🟠 **Orange border** = Medium confidence (60-79%) - Needs approval
- 🔴 **Red border** = Low confidence (<60%) - Needs approval
- Badge shows: `🔧 Healed (87%)` with confidence percentage

**What Happens:**
1. Test runs and finds element is missing
2. Self-healing finds alternative element
3. Element gets highlighted with colored border
4. Badge appears showing confidence score
5. Element smoothly scrolls into view
6. Highlight fades after 5 seconds

---

### Approval Workflow (Phase 5)
For healing decisions with <80% confidence, you'll get a notification:

**📢 Notification Appears (top-right corner):**
```
🔧 Element Healed
Confidence: 72%

Old: #submit-button
New: button[type="submit"]

✅ Accept    ❌ Reject
```

**Your Options:**
- **✅ Accept**: Test case is updated with new locator
- **❌ Reject**: Test case keeps original locator

**High Confidence (≥80%):**
- Automatically approved
- Test case updated immediately
- Notification shows: "✅ Auto-approved (high confidence)"

---

## 🚀 How to Use

### Step 1: Enable Advanced Healing
1. Open **Test Suite** page
2. Find the healing mode dropdown (top section)
3. Select **"✨ Advanced (v2 Beta)"**

### Step 2: Run Your Tests
1. Click any test case to execute
2. Watch the browser - healed elements will highlight!
3. Check top-right corner for approval notifications

### Step 3: Approve or Reject
**For low-confidence healings (<80%):**
1. Notification slides in from top-right
2. Click **✅ Accept** to update test case
3. Or click **❌ Reject** to keep original
4. Toast notification confirms your action

**For high-confidence healings (≥80%):**
- No action needed!
- Auto-approved and test case updated
- Notification shows auto-approval status

---

## 📊 Confidence Scores Explained

| Score | Color | Meaning | Action |
|-------|-------|---------|--------|
| 80-100% | 🟢 Green | High confidence match | Auto-approved |
| 60-79% | 🟠 Orange | Medium confidence | Needs approval |
| 0-59% | 🔴 Red | Low confidence | Needs approval |

**Confidence factors:**
- Element type matches (e.g., both buttons)
- Similar attributes (class, id, name)
- Similar text content
- Same position/context in page
- Visual similarity

---

## 🎬 What Happens Behind the Scenes

### When Element Fails:
```
1. Test tries original locator → ❌ Fails
2. Advanced healing activates
3. Searches for similar elements
4. Calculates confidence score
5. Highlights best match
6. Creates approval request (if <80%)
7. Waits for your decision
```

### When You Approve:
```
1. Test case JSON file opens
2. Old locator replaced with new one
3. File saved to disk
4. Notification: "✅ Healing approved"
5. Next time test runs, uses new locator
```

### When You Reject:
```
1. Test case keeps original locator
2. Healing marked as rejected
3. Notification: "❌ Healing rejected"
4. Next time test runs, may heal again
```

---

## 📂 Where Are Test Cases Stored?

Test cases get updated in these locations:
- **Builder tests**: `test_cases/builder/TC001_test_name.json`
- **Recorder tests**: `test_cases/builder/recorded_TC001_session.json`

You can open these files to see the locator changes!

---

## 🔍 Viewing Statistics

Check approval statistics:
```javascript
// GET /healing/statistics
{
  "pending": 2,
  "approved": 15,
  "rejected": 3,
  "approval_rate": 83.3
}
```

View pending approvals:
```javascript
// GET /healing/pending-approvals
{
  "approvals": [
    {
      "id": "abc123",
      "test_case_id": "TC001",
      "step_number": 5,
      "confidence": 0.72,
      "old_locator": "#submit-button",
      "new_locator": "button[type='submit']",
      "created_at": "2025-01-24T10:30:00"
    }
  ]
}
```

---

## 🎨 UI Elements

### Notification Styles:
- **Slide-in animation**: Smooth entry from top-right
- **Expandable details**: Click to show/hide locator changes
- **Inline buttons**: Accept/reject without leaving page
- **Toast notifications**: Temporary success/error messages
- **Color-coded badges**: Instant visual feedback

### Button Actions:
- **✅ Accept**: Green button, approves healing
- **❌ Reject**: Red button, keeps original
- **🔍 Details**: Expands to show old vs new locators
- **✖️ Close**: Dismisses notification (keeps pending)

---

## ⚙️ Configuration

### Default Settings:
- **Auto-approval threshold**: 80%
- **Approval expiry**: 24 hours
- **Max healing attempts**: 3 per step
- **Highlight duration**: 5 seconds

### Feature Flags:
```python
# Toggle between v1 and v2
healing_mode = 'v1'  # Standard
healing_mode = 'v2'  # Advanced with visual feedback
```

---

## 🐛 Troubleshooting

### Notification Not Appearing?
✅ Check healing mode is set to "v2"
✅ Verify `healing-ui.js` loaded (check browser console)
✅ Ensure healing confidence is <80%

### Highlight Not Visible?
✅ Element might be off-screen (should auto-scroll)
✅ Check browser console for JavaScript errors
✅ Verify element exists when healing occurs

### Test Case Not Updating?
✅ Ensure you clicked **✅ Accept** (not just closed notification)
✅ Check file permissions on `test_cases/` directory
✅ Verify JSON file exists before approval

### Statistics Not Showing?
✅ Check API server is running (`api_server_modular.py`)
✅ Verify endpoint: `GET http://localhost:5002/healing/statistics`
✅ Ensure approval workflow initialized

---

## 📞 Support

**Common Questions:**
- **Q: Can I batch approve?** A: Not yet - approve individually for now
- **Q: Can I undo approval?** A: No - but you can manually edit JSON file
- **Q: How long do approvals wait?** A: 24 hours, then auto-expire
- **Q: Can I change confidence threshold?** A: Yes - edit `ConfidenceCalculator.calculate()`

**Files to Check:**
- Backend logic: `src/main/python/advanced_self_healing.py`
- Approval workflow: `src/main/python/healing_approval.py`
- Frontend UI: `src/main/resources/web/js/features/healing-ui.js`
- API endpoints: `src/main/python/api_server_modular.py`

---

## 🎉 Success Tips

**Best Practices:**
1. ✅ **Review low-confidence healings carefully** (60-79%)
2. ✅ **Trust high-confidence healings** (80%+) - they're usually correct!
3. ✅ **Watch the highlights** during test execution - very informative
4. ✅ **Check statistics regularly** to see healing patterns
5. ✅ **Keep test cases in version control** to track locator changes

**When to Use v2:**
- ✅ Tests fail due to changing locators
- ✅ Want to see what healing is doing
- ✅ Need confidence scores for decisions
- ✅ Want automatic test maintenance

**When to Use v1:**
- ✅ Tests are stable (not breaking)
- ✅ Don't want UI notifications
- ✅ Prefer simpler fallback chains

---

**🚀 You're all set! Run your tests and watch the magic happen!** ✨

**Need more details?** See `PHASE_4_5_IMPLEMENTATION.md` for technical documentation.
