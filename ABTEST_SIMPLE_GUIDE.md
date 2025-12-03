# 🎉 Simple A/B Test Analytics - Ready to Use!

## ✅ Setup Complete!

I've created a **simple database-backed analytics system** for your A/B test. No Google Analytics setup needed - everything is tracked in your Django database!

---

## 🚀 How to Use

### Step 1: Test the A/B Page
Visit your A/B test page:
```
http://127.0.0.1:8000/2be044d/
```

- Refresh the page multiple times (you'll see different button variants: Kudos vs Thanks)
- Click the buttons
- Each action is automatically saved to your database

### Step 2: View Analytics Dashboard
Click the **"📊 View Analytics Dashboard"** button on the test page, or visit:
```
http://127.0.0.1:8000/ab-test/results/
```

---

## 📊 What You'll See on the Dashboard

### Summary Cards
- **Total Page Views**: How many times the page was loaded
- **Variants Shown**: Total number of times a button variant was displayed
- **Total Clicks**: Total button clicks across both variants
- **Overall Conversion**: (Total Clicks / Variants Shown) × 100%

### Variant Comparison Table
Shows side-by-side comparison:
- **Times Shown**: How many times each variant (Kudos/Thanks) was displayed
- **Button Clicks**: How many times each button was clicked
- **Conversion Rate**: Click-through rate for each variant
- **Visual Progress Bar**: Shows conversion rate visually
- **🏆 Winner Indicator**: Highlights which variant is performing better

### Session Statistics
- **Unique Sessions**: Number of different browser sessions
- **Average Events per Session**: How many actions per visitor

### Recent Events Table
Shows the last 50 events with:
- Timestamp
- Event type (page view, variant shown, button click)
- Which variant it was
- Session ID

---

## 🎯 Testing Guide

### Quick Test (5 minutes)
1. Open the test page: `http://127.0.0.1:8000/2be044d/`
2. Refresh 10 times, clicking the button each time
3. Open a new incognito/private window
4. Refresh 10 more times there
5. View the results dashboard

You should see:
- ~10 page views from each session
- ~10 variants shown for kudos, ~10 for thanks (roughly 50/50)
- ~20 total clicks
- Conversion rates around 100% (if you clicked every time)

### Generate More Data
```bash
# Option 1: Open multiple browser windows
# - Regular window
# - Incognito window  
# - Different browser

# Option 2: Clear localStorage to reset session
# In browser console: localStorage.clear()
# Then refresh the page
```

---

## 💾 Data Storage

All data is stored in your SQLite database in the `ABTestEvent` table:

```python
# Model fields:
- event_type: 'page_view', 'variant_shown', or 'button_click'
- variant: 'kudos' or 'thanks' (null for page_view events)
- session_id: Unique browser session identifier
- user_agent: Browser information
- ip_address: Visitor IP address
- timestamp: When the event occurred
```

---

## 🔧 How It Works

### Frontend (JavaScript)
1. Generates a unique session ID (stored in localStorage)
2. Randomly selects variant (50/50 split using Math.random())
3. Sends events to Django backend via AJAX:
   - When page loads → `page_view` event
   - When variant is shown → `variant_shown` event with variant name
   - When button clicked → `button_click` event with variant name

### Backend (Django)
1. Receives events at `/ab-test/log-event/` endpoint
2. Saves to database with timestamp and session info
3. Dashboard at `/ab-test/results/` aggregates and displays data

---

## 📈 Understanding Your Results

### Conversion Rate Formula
```
Conversion Rate = (Button Clicks / Variants Shown) × 100%
```

### Example Results
```
Variant | Times Shown | Clicks | Conversion Rate
--------|-------------|--------|----------------
Kudos   | 150         | 89     | 59.3%
Thanks  | 148         | 112    | 75.7%
Winner: Thanks (75.7% > 59.3%)
```

### Statistical Significance
For reliable results, aim for:
- **Minimum**: 100 impressions per variant
- **Better**: 500+ impressions per variant
- **Ideal**: 1000+ impressions per variant

---

## 🎨 Customization

### Change Button Variants
Edit `templates/energy_tracker/abtest.html`:
```javascript
// Line ~200 - Change button text/styling
if (variant === 'kudos') {
    button.textContent = '👏 Give Kudos';  // ← Change this
} else {
    button.textContent = '🙏 Say Thanks';  // ← Change this
}
```

### Change Split Ratio
```javascript
// Line ~175 - Modify randomization
function selectVariant() {
    // For 70/30 split:
    if (Math.random() < 0.7) {
        return 'kudos';  // 70%
    } else {
        return 'thanks'; // 30%
    }
}
```

### Add More Variants
1. Update model choices in `energy_tracker/models.py`
2. Modify JavaScript randomization
3. Update results template styling

---

## 🔍 Troubleshooting

### "No events recorded yet"
- Make sure you visited the test page first
- Check browser console for errors (F12)
- Verify Django server is running

### Events not saving
- Check browser console for AJAX errors
- Verify CSRF token is present (should be automatic)
- Check Django server logs for errors

### Same variant every time
- This is normal for the same session
- Clear localStorage: `localStorage.clear()`
- Or use incognito/private browsing mode

### Dashboard not updating
- Click "🔄 Refresh Data" button
- Or manually refresh the page (Cmd+R / Ctrl+R)

---

## 🗑️ Reset Data

To clear all A/B test data:
```bash
cd "/Users/judebart-plange/Desktop/656 Project folder/Energy-Manager/Energy-Manager"
python manage.py shell

# In the Python shell:
from energy_tracker.models import ABTestEvent
ABTestEvent.objects.all().delete()
exit()
```

---

## 🎓 Next Steps

1. **Test Now**: Visit the test page and generate some data!
2. **Share the Link**: Send `http://127.0.0.1:8000/2be044d/` to friends/testers
3. **Monitor Results**: Check the dashboard regularly
4. **Make Decisions**: After 100+ samples, choose the winning variant

---

## 📊 Quick Access Links

- **Test Page**: http://127.0.0.1:8000/2be044d/
- **Results Dashboard**: http://127.0.0.1:8000/ab-test/results/
- **Django Admin** (to view raw data): http://127.0.0.1:8000/admin/

---

## ⚡ Pro Tips

1. **Test with real users** - Don't just test yourself
2. **Wait for enough data** - At least 100 impressions per variant
3. **Consider context** - Test at different times/days
4. **Track sessions** - Each unique visitor gets one session ID
5. **Export data** - You can query the database for deeper analysis

---

## 🎉 That's It!

You now have a fully functional A/B testing system with real-time analytics!

**No Google Analytics setup required** - everything is tracked locally in your Django database.

Start testing and see which button variant performs better! 🚀
