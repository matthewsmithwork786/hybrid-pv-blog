# Style Guide: Beyond the Solar Curve

This guide provides comprehensive documentation for the visual design system and content patterns used in the "Beyond the Solar Curve" report.

## Color Palette

| Purpose | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| **Solar PV** | Yellow | `#FFD700` | Solar-related content, PV sections |
| **Wind** | Green | `#2E7D32` | Wind energy content |
| **Battery (Standalone)** | Purple | `#7B1FA2` | Standalone battery content |
| **Battery (Co-located)** | Dark Orange | `#FF6F00` | Hybrid/co-located battery content |
| **Accent/Links** | Teal | `#00ACC1` | Links, interactive elements |
| **Text** | Dark Blue-Grey | `#2C3E50` | Body text, headings |
| **Negative/Curtailment** | Red | `#D32F2F` | Negative pricing, curtailment |
| **Positive** | Dark Green | `#388E3C` | Positive outcomes, benefits |

## Typography

### Font Families
- **Headings & Body**: Lato (Google Fonts)
- **Code**: Consolas, Monaco, monospace

### Hierarchy
- **H1**: 2.5rem, 900 weight (page titles)
- **H2**: 2rem, 700 weight with teal bottom border (section headers)
- **H3**: 1.5rem, 700 weight (subsection headers)
- **H4**: 1.2rem, 700 weight (chart titles)
- **Body**: 1rem, 400 weight (16px)

## Design Components

### Analysis Boxes
Content containers styled by energy type:

```html
<div class="analysis-box pv-section">
  <!-- Solar PV content -->
</div>

<div class="analysis-box battery-section">
  <!-- Battery content -->
</div>

<div class="analysis-box hybrid-section">
  <!-- Hybrid/co-located content -->
</div>
```

### Key Finding Callouts
Highlight important insights:

```html
<div class="key-finding">
  <p>Important insight or finding that readers should note.</p>
</div>
```

### Data Source Notes
Attribute data sources:

```html
<div class="data-note">
  Data: AEMO via NEMOSIS, 2018-2025
</div>
```

### Chart Containers
Standard pattern for embedding charts:

```html
<div class="chart-container">
  <div class="chart-header">
    <h4 class="chart-title">Chart Title</h4>
    <span class="chart-status-badge complete">Complete</span>
  </div>
  <iframe src="../data/outputs/sectionX/chart.html" class="chart-iframe" style="height: 500px"></iframe>
  <div class="chart-footer">
    <span class="chart-source">Data: AEMO via NEMOSIS</span>
    <a href="../scripts/sectionX/script.py" class="chart-code-link">View Analysis Code →</a>
  </div>
</div>
```

#### Chart Status Badges
- `complete`: Chart is fully implemented and working
- `pending`: Chart placeholder for future implementation
- `error`: Chart has errors and needs fixing

### Section Summaries
Chapter introduction summaries:

```html
<div class="section-summary">
  <h4>Chapter Overview</h4>
  <p>Brief summary of what this section covers and key takeaways.</p>
</div>
```

### Key Takeaways Lists
Structured bullet points with checkmarks:

```html
<div class="takeaways-list">
  <h4>Key Takeaways</h4>
  <ul>
    <li>First key point</li>
    <li>Second key point</li>
    <li>Third key point</li>
  </ul>
</div>
```

### Chart Placeholders
For missing/incomplete charts:

```html
<div class="chart-placeholder"></div>
```

## Content Patterns

### Section Structure
1. **Section Summary**: Brief overview at start
2. **Analysis Content**: Main narrative with embedded charts
3. **Key Findings**: Highlight important insights
4. **Data Notes**: Attribute all data sources
5. **Takeaways**: Summary at end (optional)

### Chart Integration Pattern
1. **Introduce**: Context sentence before chart
2. **Embed**: Use chart container with proper status
3. **Explain**: Analysis sentence after chart
4. **Link**: Provide code link for transparency

### Writing Style
- **Voice**: Professional, analytical, accessible
- **Tense**: Present tense for findings, past for methodology
- **Perspective**: Third-person objective
- **Clarity**: Avoid jargon, explain technical terms
- **Precision**: Use specific numbers, avoid vague statements

## Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Mobile Optimizations
- Charts use responsive iframe containers
- Text remains readable at all sizes
- Navigation collapses to hamburger menu
- Tables scroll horizontally on small screens

## Accessibility

### Color Contrast
- All text meets WCAG AA standards (4.5:1)
- Charts use distinct colors with high contrast
- Links use underlined accent color

### Screen Reader Support
- Semantic HTML structure
- Alt text for all images/charts
- Proper heading hierarchy
- Descriptive link text

### Keyboard Navigation
- All interactive elements keyboard accessible
- Clear focus indicators
- Skip navigation links

## Print Styles

### Optimizations
- Page breaks avoid splitting charts
- Background colors preserved where important
- URLs shown in parentheses after links
- Status badges hidden in print version

## File Organization

### Asset Structure
```
assets/
├── styles/
│   └── custom.css          # Main stylesheet
├── partials/
│   └── chart-container.html # Reusable chart component
└── images/
    └── (chart exports, diagrams)
```

### Script Organization
```
scripts/
├── utils/
│   ├── style_config.py     # Plotly templates, colors
│   ├── data_paths.py       # Path configuration
│   └── nemosis_helpers.py  # Data loading utilities
├── section1/
├── section3/
├── section4/
└── section5/
```

## Chart Styling Guidelines

### Plotly Configuration
- Use `style_config.TEMPLATE` for consistent theming
- Apply color palette from `style_config.COLORS`
- Include hover tooltips with detailed information
- Export as HTML with CDN for interactivity

### Common Chart Elements
- **Titles**: Descriptive, indicate time period
- **Axes**: Clearly labeled with units
- **Legends**: Position to avoid data overlap
- **Annotations**: Highlight key insights
- **Sources**: Include data attribution in footer

## Quality Checklist

### Before Publishing
- [ ] All charts render correctly
- [ ] Chart status badges are accurate
- [ ] Data sources are properly attributed
- [ ] Links to code are functional
- [ ] Color contrast meets accessibility standards
- [ ] Mobile responsiveness tested
- [ ] Print layout verified
- [ ] Spelling and grammar checked
- [ ] Consistent terminology used
- [ ] Cross-references work correctly

---

*Style Guide v1.0 - Created 2026-01-05*