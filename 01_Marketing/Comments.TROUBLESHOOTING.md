# Comments Component - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Table of Contents
- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [API Integration Problems](#api-integration-problems)
- [Performance Issues](#performance-issues)
- [UI/UX Problems](#uiux-problems)
- [Browser Compatibility](#browser-compatibility)
- [Debugging Tools](#debugging-tools)
- [FAQ](#frequently-asked-questions)

## 🔧 Installation Issues

### Issue: Module Not Found
**Error:** `Module not found: Can't resolve './pages/Comments'`

**Solutions:**
```bash
# Check file path
ls -la frontend/src/pages/Comments.jsx

# Verify import statement
import Comments from './pages/Comments'; // Correct
import Comments from './pages/Comments.jsx'; // Also correct
```

### Issue: Missing Dependencies
**Error:** `Cannot resolve module '@tanstack/react-query'`

**Solutions:**
```bash
# Install missing dependencies
npm install @tanstack/react-query react-hot-toast @heroicons/react

# Or with yarn
yarn add @tanstack/react-query react-hot-toast @heroicons/react

# Check package.json
cat package.json | grep -E "(react-query|hot-toast|heroicons)"
```

### Issue: Tailwind CSS Not Working
**Error:** Styles not applying correctly

**Solutions:**
```bash
# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind
npx tailwindcss init -p

# Update tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

# Add to index.css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## ⚠️ Runtime Errors

### Issue: Comments Not Loading
**Error:** Comments list is empty or shows loading indefinitely

**Debug Steps:**
```javascript
// 1. Check API endpoint
console.log('API Base URL:', process.env.REACT_APP_API_BASE_URL);

// 2. Test API directly
fetch('/api/comments')
  .then(response => response.json())
  .then(data => console.log('API Response:', data))
  .catch(error => console.error('API Error:', error));

// 3. Check network tab in browser dev tools
// Look for failed requests or CORS errors
```

**Solutions:**
```javascript
// Add error handling to API calls
const { data: comments, isLoading, error } = useQuery({
  queryKey: ['comments'],
  queryFn: async () => {
    try {
      const response = await fetch('/api/comments');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
  retry: 3,
  retryDelay: 1000
});

// Display error state
if (error) {
  return (
    <div className="text-center py-8">
      <p className="text-red-600">Error loading comments: {error.message}</p>
      <button onClick={() => window.location.reload()}>
        Retry
      </button>
    </div>
  );
}
```

### Issue: AI Analysis Not Working
**Error:** AI features not functioning or showing errors

**Debug Steps:**
```javascript
// 1. Check AI service configuration
console.log('AI Service URL:', process.env.REACT_APP_AI_SERVICE_URL);
console.log('AI API Key:', process.env.REACT_APP_AI_API_KEY ? 'Set' : 'Not Set');

// 2. Test AI endpoint
fetch('/api/generate-response', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    commentId: 'test',
    templateId: 'auto'
  })
})
.then(response => response.json())
.then(data => console.log('AI Response:', data))
.catch(error => console.error('AI Error:', error));
```

**Solutions:**
```javascript
// Add proper error handling for AI features
const generateResponseMutation = useMutation({
  mutationFn: async ({ commentId, templateId, customPrompt }) => {
    try {
      const response = await fetch('/api/generate-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ commentId, templateId, customPrompt }),
      });
      
      if (!response.ok) {
        throw new Error(`AI service error: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('AI Generation Error:', error);
      throw error;
    }
  },
  onError: (error) => {
    toast.error(`AI Error: ${error.message}`);
  }
});
```

### Issue: State Management Problems
**Error:** Component state not updating correctly

**Debug Steps:**
```javascript
// 1. Add state logging
useEffect(() => {
  console.log('Selected Comment:', selectedComment);
  console.log('Filter Sentiment:', filterSentiment);
  console.log('Search Term:', searchTerm);
}, [selectedComment, filterSentiment, searchTerm]);

// 2. Check for state conflicts
const handleCommentSelect = useCallback((comment) => {
  console.log('Selecting comment:', comment);
  setSelectedComment(comment);
}, []);
```

**Solutions:**
```javascript
// Use proper state management
const [state, setState] = useState({
  selectedComment: null,
  filterSentiment: 'all',
  filterPlatform: 'all',
  searchTerm: '',
  aiAnalysisMode: 'advanced'
});

const updateState = useCallback((updates) => {
  setState(prev => ({ ...prev, ...updates }));
}, []);
```

## 🌐 API Integration Problems

### Issue: CORS Errors
**Error:** `Access to fetch at 'http://localhost:3001/api/comments' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solutions:**
```javascript
// Backend CORS configuration (Node.js/Express)
const cors = require('cors');

app.use(cors({
  origin: ['http://localhost:3000', 'https://yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Or for development, use proxy in package.json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "proxy": "http://localhost:3001",
  "dependencies": {
    // ...
  }
}
```

### Issue: Authentication Errors
**Error:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**
```javascript
// Add proper authentication headers
const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem('authToken');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };
  
  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  });
  
  if (response.status === 401) {
    // Handle token expiration
    localStorage.removeItem('authToken');
    window.location.href = '/login';
    return;
  }
  
  return response;
};
```

### Issue: Rate Limiting
**Error:** `429 Too Many Requests`

**Solutions:**
```javascript
// Implement request throttling
const useThrottledApi = (delay = 1000) => {
  const [isThrottled, setIsThrottled] = useState(false);
  
  const throttledCall = useCallback(async (apiCall) => {
    if (isThrottled) return;
    
    setIsThrottled(true);
    try {
      const result = await apiCall();
      return result;
    } finally {
      setTimeout(() => setIsThrottled(false), delay);
    }
  }, [isThrottled, delay]);
  
  return throttledCall;
};

// Use with API calls
const throttledApi = useThrottledApi(1000);
const result = await throttledApi(() => fetch('/api/comments'));
```

## ⚡ Performance Issues

### Issue: Slow Loading
**Problem:** Component takes too long to load

**Solutions:**
```javascript
// 1. Implement lazy loading
const Comments = lazy(() => import('./pages/Comments'));

// 2. Add loading states
const { data: comments, isLoading } = useQuery({
  queryKey: ['comments'],
  queryFn: fetchComments,
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
});

// 3. Optimize re-renders
const MemoizedCommentItem = React.memo(({ comment, onSelect }) => {
  return (
    <div onClick={() => onSelect(comment)}>
      {/* Comment content */}
    </div>
  );
});

// 4. Use virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

const VirtualizedComments = ({ comments }) => (
  <List
    height={600}
    itemCount={comments.length}
    itemSize={120}
    itemData={comments}
  >
    {({ index, style, data }) => (
      <div style={style}>
        <CommentItem comment={data[index]} />
      </div>
    )}
  </List>
);
```

### Issue: Memory Leaks
**Problem:** Memory usage increases over time

**Solutions:**
```javascript
// 1. Clean up subscriptions
useEffect(() => {
  const subscription = subscribeToComments();
  
  return () => {
    subscription.unsubscribe();
  };
}, []);

// 2. Clear intervals and timeouts
useEffect(() => {
  const interval = setInterval(() => {
    // Poll for updates
  }, 30000);
  
  return () => clearInterval(interval);
}, []);

// 3. Use proper dependency arrays
const memoizedCallback = useCallback(() => {
  // Expensive operation
}, [dependency1, dependency2]);

const memoizedValue = useMemo(() => {
  // Expensive calculation
  return expensiveCalculation(data);
}, [data]);
```

## 🎨 UI/UX Problems

### Issue: Responsive Design Issues
**Problem:** Layout breaks on mobile devices

**Solutions:**
```css
/* Add responsive breakpoints */
.comments-container {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-6;
}

.comment-item {
  @apply p-4 border rounded-lg;
}

@media (max-width: 768px) {
  .comment-item {
    @apply p-3 text-sm;
  }
}

/* Use Tailwind responsive classes */
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>
```

### Issue: Dark Mode Not Working
**Problem:** Dark mode styles not applying

**Solutions:**
```javascript
// 1. Check Tailwind dark mode configuration
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media'
  // ...
}

// 2. Add dark mode toggle
const [isDarkMode, setIsDarkMode] = useState(false);

useEffect(() => {
  if (isDarkMode) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}, [isDarkMode]);

// 3. Use dark mode classes
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  {/* Content */}
</div>
```

### Issue: Accessibility Problems
**Problem:** Component not accessible to screen readers

**Solutions:**
```javascript
// 1. Add proper ARIA labels
<button
  aria-label="Generate AI response for comment"
  aria-describedby="response-description"
  onClick={generateResponse}
>
  Generate Response
</button>

// 2. Add keyboard navigation
const handleKeyDown = (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleClick();
  }
};

// 3. Add focus management
const focusElement = useRef(null);

useEffect(() => {
  if (focusElement.current) {
    focusElement.current.focus();
  }
}, [selectedComment]);

// 4. Add screen reader announcements
const announceToScreenReader = (message) => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};
```

## 🌍 Browser Compatibility

### Issue: Internet Explorer Not Working
**Problem:** Component doesn't work in IE11

**Solutions:**
```javascript
// 1. Add polyfills
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// 2. Use Babel configuration
// .babelrc
{
  "presets": [
    ["@babel/preset-env", {
      "targets": {
        "browsers": ["last 2 versions", "ie >= 11"]
      }
    }],
    "@babel/preset-react"
  ]
}

// 3. Avoid modern JavaScript features
// Instead of:
const { data, error } = await fetch('/api/comments');

// Use:
fetch('/api/comments')
  .then(response => response.json())
  .then(data => setComments(data))
  .catch(error => setError(error));
```

### Issue: Safari Specific Issues
**Problem:** Features not working in Safari

**Solutions:**
```javascript
// 1. Add Safari-specific CSS
.safari-fix {
  -webkit-appearance: none;
  -webkit-border-radius: 0;
}

// 2. Handle Safari date parsing
const parseDate = (dateString) => {
  // Safari doesn't support ISO date strings without timezone
  const date = new Date(dateString.replace(' ', 'T'));
  return isNaN(date.getTime()) ? new Date() : date;
};

// 3. Fix Safari flexbox issues
.flex-container {
  display: -webkit-flex;
  display: flex;
  -webkit-flex-direction: column;
  flex-direction: column;
}
```

## 🔍 Debugging Tools

### Browser DevTools
```javascript
// 1. Add debug logging
const DEBUG = process.env.NODE_ENV === 'development';

const debugLog = (message, data) => {
  if (DEBUG) {
    console.log(`[Comments Debug] ${message}`, data);
  }
};

// 2. Add performance monitoring
const measurePerformance = (name, fn) => {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  console.log(`${name} took ${end - start} milliseconds`);
  return result;
};

// 3. Add error tracking
const trackError = (error, context) => {
  console.error('Comments Error:', error, context);
  
  // Send to error tracking service
  if (window.gtag) {
    window.gtag('event', 'exception', {
      description: error.message,
      fatal: false
    });
  }
};
```

### React DevTools
```javascript
// 1. Add display name for debugging
const Comments = () => {
  // Component logic
};

Comments.displayName = 'Comments';

// 2. Add prop types for development
import PropTypes from 'prop-types';

Comments.propTypes = {
  // Define prop types
};

// 3. Use React.memo for performance debugging
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  // Custom comparison logic
  return prevProps.id === nextProps.id;
});
```

### Network Debugging
```javascript
// 1. Add request/response logging
const apiCall = async (url, options) => {
  console.log('API Request:', { url, options });
  
  const response = await fetch(url, options);
  const data = await response.json();
  
  console.log('API Response:', { status: response.status, data });
  
  return data;
};

// 2. Add retry logic with logging
const retryApiCall = async (url, options, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      console.log(`API Attempt ${i + 1}/${maxRetries}`);
      return await apiCall(url, options);
    } catch (error) {
      console.error(`API Attempt ${i + 1} failed:`, error);
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

## ❓ Frequently Asked Questions

### Q: How do I customize the AI analysis settings?
**A:** You can modify the AI settings through the component's internal state or by passing props:

```javascript
// Method 1: Modify internal state
const [aiSettings, setAiSettings] = useState({
  analysisMode: 'quantum',
  neuralDepth: 25,
  quantumProcessing: true
});

// Method 2: Create a wrapper component
const CustomComments = ({ aiConfig }) => {
  return <Comments aiConfig={aiConfig} />;
};
```

### Q: Can I use this component without the AI features?
**A:** Yes, you can disable AI features by setting the analysis mode to 'basic' or by modifying the component to hide AI-related UI elements.

### Q: How do I add custom response templates?
**A:** You can extend the component to include custom templates:

```javascript
const customTemplates = {
  customer_support: {
    name: 'Customer Support',
    prompt: 'Generate a helpful customer support response...'
  },
  marketing: {
    name: 'Marketing Response',
    prompt: 'Generate an engaging marketing response...'
  }
};
```

### Q: Is this component accessible?
**A:** The component includes basic accessibility features, but you should test with screen readers and add additional ARIA labels as needed for your specific use case.

### Q: How do I handle large numbers of comments?
**A:** For large datasets, consider implementing:
- Pagination
- Virtual scrolling
- Lazy loading
- Server-side filtering
- Caching strategies

### Q: Can I integrate with other social media platforms?
**A:** Yes, you can extend the platform support by:
- Adding new platform icons
- Updating the platform filter options
- Modifying the API endpoints
- Adding platform-specific styling

---

## 🆘 Getting Help

If you're still experiencing issues:

1. **Check the console** for error messages
2. **Review the network tab** for failed API calls
3. **Test in different browsers** to isolate browser-specific issues
4. **Check the component props** and state values
5. **Verify API endpoints** are working correctly
6. **Review the documentation** for proper usage examples

### Contact Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the README and API docs
- **Community**: Join our Discord for community support
- **Email**: Contact support@yourdomain.com for urgent issues

---

*Troubleshooting Guide v2.0.0 - Last updated: December 2024*









