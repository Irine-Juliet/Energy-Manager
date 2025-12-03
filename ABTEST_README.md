# A/B Test Implementation with Google Analytics 4

## Overview

This implementation provides a complete A/B testing solution with Google Analytics 4 (GA4) tracking for testing two button variants:
- **Variant A ("kudos")**: "👏 Give Kudos" button (green)
- **Variant B ("thanks")**: "🙏 Say Thanks" button (blue)

## Features

✅ **50/50 Random Split**: Uses `Math.random()` for client-side randomization  
✅ **Google Analytics 4 Integration**: Full event tracking with gtag.js  
✅ **Three Event Types**: Page views, variant shown, and button clicks  
✅ **Real-time Feedback**: Visual confirmation when button is clicked  
✅ **Debug Information**: Shows current variant and console logs for testing  

## Files

### 1. Django Template (Integrated)
**File**: `templates/energy_tracker/abtest.html`
- Extends the Django base template
- Integrated with your existing Energy Manager app
- Access at: `http://127.0.0.1:8000/2be044d/`

### 2. Standalone HTML
**File**: `abtest_standalone.html`
- Complete standalone HTML file
- Can be opened directly in a browser
- No server required for testing

## Setup Instructions

### Step 1: Get Your Google Analytics Measurement ID

1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new GA4 property (or use an existing one)
3. Go to **Admin** → **Data Streams** → Select your web stream
4. Copy your **Measurement ID** (format: `G-XXXXXXXXXX`)

### Step 2: Update the Code

Replace `G-TEST123456` with your real measurement ID in both files:

```html
<!-- Find this line: -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TEST123456"></script>

<!-- And this line: -->
gtag('config', 'G-TEST123456');

<!-- Replace G-TEST123456 with your actual ID: -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YOUR_ACTUAL_ID"></script>
gtag('config', 'G-YOUR_ACTUAL_ID');
```

### Step 3: Test the Implementation

#### Option A: Using Django (Integrated)
1. Make sure your Django server is running: `python manage.py runserver`
2. Navigate to: `http://127.0.0.1:8000/2be044d/`
3. Refresh the page multiple times to see different variants (50/50 chance)

#### Option B: Using Standalone HTML
1. Open `abtest_standalone.html` directly in your browser
2. Refresh to see different variants

### Step 4: Verify Events in GA4

1. Go to Google Analytics → **Reports** → **Realtime**
2. Open your test page and click the button
3. You should see events appearing in real-time:
   - `ab_test_page_view` - When page loads
   - `variant_shown` - When variant is selected (kudos or thanks)
   - `button_click` - When user clicks the button

## Event Tracking Details

### 1. Page View Event
- **Event Name**: `ab_test_page_view`
- **Parameters**: 
  - `page`: `/ab-test`
- **When Fired**: On page load

### 2. Variant Shown Event
- **Event Name**: `variant_shown`
- **Parameters**: 
  - `variant`: `"kudos"` or `"thanks"`
- **When Fired**: Immediately after variant is randomly selected

### 3. Button Click Event
- **Event Name**: `button_click`
- **Parameters**: 
  - `variant`: `"kudos"` or `"thanks"`
- **When Fired**: When user clicks the button

## How It Works

### Randomization Logic

```javascript
function selectVariant() {
    // 50/50 random split using Math.random()
    if (Math.random() < 0.5) {
        return 'kudos';
    } else {
        return 'thanks';
    }
}
```

- `Math.random()` generates a number between 0 and 1
- If < 0.5 (50% chance) → show "kudos" variant
- If ≥ 0.5 (50% chance) → show "thanks" variant

### Event Flow

```
1. Page loads
   ↓
2. Track page view (ab_test_page_view)
   ↓
3. Select random variant (kudos or thanks)
   ↓
4. Track variant shown (variant_shown)
   ↓
5. Render button
   ↓
6. User clicks button
   ↓
7. Track button click (button_click)
   ↓
8. Show feedback message
```

## Analyzing Results in Google Analytics

### Method 1: Custom Report
1. Go to **Explore** → Create a new exploration
2. Add dimensions: Event name, Custom event parameter (variant)
3. Add metrics: Event count
4. Filter for events: `variant_shown` and `button_click`

### Method 2: Conversion Rate Calculation
```
Conversion Rate = (button_click events) / (variant_shown events) × 100%
```

Compare conversion rates between variants:
- **Kudos Conversion Rate** = (kudos button clicks) / (kudos variant shown) × 100%
- **Thanks Conversion Rate** = (thanks button clicks) / (thanks variant shown) × 100%

### Method 3: Real-time Debugging
- Open browser DevTools → Console
- Watch for log messages: `GA Event: variant_shown - variant: kudos`
- Verify events are firing correctly

## Customization

### Change Button Text
Edit in `renderButton()` function:
```javascript
if (variant === 'kudos') {
    button.textContent = '👏 Give Kudos';  // Change this
} else {
    button.textContent = '🙏 Say Thanks';  // Change this
}
```

### Change Button Colors
Edit Tailwind classes:
```javascript
if (variant === 'kudos') {
    button.className = 'px-8 py-4 bg-green-600 ...';  // Change bg-green-600
} else {
    button.className = 'px-8 py-4 bg-blue-600 ...';   // Change bg-blue-600
}
```

### Change Split Ratio (not 50/50)
Edit in `selectVariant()` function:
```javascript
function selectVariant() {
    // Example: 70/30 split (70% kudos, 30% thanks)
    if (Math.random() < 0.7) {
        return 'kudos';
    } else {
        return 'thanks';
    }
}
```

### Add More Variants
Extend the logic:
```javascript
function selectVariant() {
    const rand = Math.random();
    if (rand < 0.33) {
        return 'kudos';
    } else if (rand < 0.66) {
        return 'thanks';
    } else {
        return 'awesome';  // New variant
    }
}
```

## Troubleshooting

### Events Not Showing in GA4
1. **Check measurement ID**: Make sure you replaced `G-TEST123456`
2. **Wait 24 hours**: GA4 can take time to process events
3. **Use Realtime view**: Check **Reports** → **Realtime** for immediate feedback
4. **Check console**: Look for errors in browser DevTools
5. **Ad blockers**: Disable ad blockers that might block GA scripts

### Button Not Appearing
1. **Check console**: Look for JavaScript errors
2. **Verify DOM**: Check if `button-container` element exists
3. **Check browser**: Try a different browser

### Same Variant Every Time
- This is normal! Each page load is independent
- Refresh multiple times to see different variants
- In a real A/B test, users typically see the same variant across sessions

## Best Practices

1. **Don't remove debug info immediately**: Keep it during testing phase
2. **Test with real measurement ID**: Don't use `G-TEST123456` in production
3. **Monitor for 1-2 weeks**: Get statistically significant results
4. **Track enough events**: Aim for at least 100-200 conversions per variant
5. **Consider user sessions**: In production, you might want to store variant in localStorage

## Production Considerations

### Remove Debug Information
Remove or hide the debug section:
```html
<!-- Comment out or delete this section in production -->
<!--
<div class="mt-8 bg-gray-50 rounded-lg p-6 border border-gray-200">
    ...
</div>
-->
```

### Add Persistent Variant Assignment
Store variant in localStorage so users see the same variant across sessions:
```javascript
function selectVariant() {
    // Check if variant already stored
    let storedVariant = localStorage.getItem('ab_test_variant');
    if (storedVariant) {
        return storedVariant;
    }
    
    // Otherwise, select new variant
    const variant = Math.random() < 0.5 ? 'kudos' : 'thanks';
    localStorage.setItem('ab_test_variant', variant);
    return variant;
}
```

## Support

For questions or issues:
1. Check the browser console for errors
2. Verify GA4 setup in Google Analytics
3. Review the code comments in the HTML file

## License

This implementation is part of the Energy Manager project.
