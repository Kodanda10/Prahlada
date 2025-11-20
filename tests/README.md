# Test Suite Documentation - Project Dhruv

## Overview
This comprehensive test suite implements FANG-level testing for the Hindi-first "सोशल मीडिया एनालिटिक्स डैशबोर्ड" with 73+ test files across 14 categories.

## Test Categories

### 1. Visual Regression & Layout Stability
**Location**: `tests/visual-regression/`
- Hindi font rendering & clipping
- Text overflow stress tests
- Glassmorphism contrast audit
- Snapshot regression tests
- Z-index & overlay tests

**Run**: `npm run test -- visual-regression`

### 2. Hindi-First & Typography Integrity
**Location**: `tests/typography/`
- Hindi-only string audit
- Font fallback coverage
- Mixed-script input safety

**Run**: `npm run test -- typography`

### 3. Animation & Interaction Performance (60 FPS)
**Location**: `tests/animation/`
- Frame rate monitoring
- Layout thrashing checks
- Memory leak tests
- Input latency (< 50ms target)
- Reduced motion tests

**Run**: `npm run test -- animation`

### 4. D3 Mindmap & Mapbox Critical Features
**Location**: `tests/mindmap/`, `tests/mapbox/`
- Hierarchy correctness with FAISS metadata
- Edge-case hierarchies
- Node stress testing (500+ nodes)
- Interaction & animation
- Visit count consistency
- A11y fallback
- Marker rendering & tooltips
- Clustering & zoom behavior
- Performance & throttling
- Offline/error behavior

**Run**: `npm run test -- mindmap mapbox`

### 5. Other Data Visualization (Charts)
**Location**: `tests/charts/`
- CustomBarChart, CustomLineChart, CustomPieChart
- Chart responsiveness and theming
- Data validation and error handling
- Chart animation and interactivity

**Run**: `npm run test -- charts`

### 6. Frontend-Backend Integration & Resilience
**Location**: `tests/integration/`
- API service integration
- Data synchronization and caching
- Error recovery and retry logic
- Real-time updates (WebSocket/SSE)
- Authentication and session management
- Performance monitoring

**Run**: `npm run test -- integration`

### 7. Search & Semantic Logic
**Location**: `tests/search/`
- Basic and advanced search functionality
- Semantic understanding and synonyms
- Search performance and optimization
- Search UI and user experience
- Search analytics and insights

**Run**: `npm run test -- search`

### 8. Security & Authentication (Client)
**Location**: `tests/security/`
- Input validation and sanitization
- Authentication flow security
- API security headers and requests
- Data protection and privacy
- Secure error handling

**Run**: `npm run test -- security`

### 9. Accessibility & Screen Reader Flow
**Location**: `tests/accessibility/`
- Screen reader navigation
- ARIA labels and descriptions
- Keyboard navigation
- Color contrast and visual accessibility
- Form accessibility

**Run**: `npm run test -- accessibility`

### 10. Offline, Caching & Field Conditions
**Location**: `tests/offline/`
- Service worker registration
- Cache management
- Offline detection
- Background sync
- Network failure handling

**Run**: `npm run test -- offline`

### 11. Telemetry & Error Boundaries
**Location**: `tests/telemetry/`
- Error boundary functionality
- Performance monitoring
- Core Web Vitals tracking
- User interaction tracking

**Run**: `npm run test -- telemetry`

### 12. Browser Compatibility
**Location**: `tests/browser/`
- Modern browser support (ES6+, async/await)
- Progressive enhancement
- Cross-browser event handling
- Polyfill loading

**Run**: `npm run test -- browser`

### 13. Build & Bundle Optimization
**Location**: `tests/build/`
- Code splitting
- Asset optimization
- Tree shaking
- Performance budgets

**Run**: `npm run test -- build`

### 14. CI/CD Coverage Gates
**Location**: `tests/cicd/`
- Test coverage requirements (Lines ≥ 90%, Branches ≥ 85%)
- Linting & code quality
- Security scanning
- Performance testing
- Build & deployment gates

**Run**: `npm run test -- cicd`

## E2E Tests (Playwright)
**Location**: `tests/e2e/`
- Real Mapbox + D3 + Backend integration
- Analytics geo-mapping end-to-end
- Cross-browser testing

**Run**: `npx playwright test`

## Running Tests

### All Tests
```bash
npm test
```

### Specific Category
```bash
npm run test -- <category-name>
```

### With Coverage
```bash
npm run test -- --coverage
```

### Watch Mode
```bash
npm run test -- --watch
```

### Specific Test File
```bash
npm run test -- <path-to-test-file>
```

## Coverage Targets
- **Lines**: ≥ 90%
- **Functions**: ≥ 85%
- **Branches**: ≥ 80%
- **Statements**: ≥ 90%

## Performance Benchmarks
- **Input Latency**: < 50ms
- **Frame Rate**: 55-60 FPS
- **Bundle Size**: < 500KB total
- **Lighthouse Scores**:
  - Performance: ≥ 90
  - Accessibility: ≥ 95
  - Best Practices: ≥ 95

## CI/CD Integration
Tests are automatically run in GitHub Actions with the following workflows:
- `test:unit` - Unit tests with coverage
- `test:e2e` - E2E tests with Playwright
- `test:lint` - ESLint and TypeScript checks
- `test:accessibility` - Accessibility audits
- `test:bundle` - Build optimization checks

## Prerequisites
1. Install dependencies: `npm install`
2. For E2E tests: `npx playwright install`
3. For real Mapbox tests: Set `MAPBOX_ACCESS_TOKEN` environment variable

## Test Data
The test suite uses seeded data matching the FAISS metadata structure:
- **Tweets**: 50+ seeded tweets with Chhattisgarh locations
- **Hierarchy**: Complete district → constituency → block → GP → village structure
- **Analytics**: Mock data matching real API responses

## Contributing
When adding new tests:
1. Follow the existing file structure
2. Include Hindi text and assertions
3. Add performance benchmarks where applicable
4. Update coverage thresholds if needed
5. Ensure tests work in CI/CD pipeline

## Troubleshooting
- **Timeout errors**: Increase `testTimeout` in `vitest.config.ts`
- **Memory issues**: Use `--pool=forks` for large test suites
- **Flaky E2E tests**: Add retry logic and proper waits
- **Coverage gaps**: Check `exclude` patterns in vitest config