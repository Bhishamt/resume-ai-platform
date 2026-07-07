# 06 - Component Guidelines

> **Project:** AI Resume Analyzer & Job Match Platform
> **Version:** 1.0

---

# Purpose

This document defines the standards for building reusable UI components. Every component should be modular, maintainable, responsive, accessible, and consistent with the design system.

---

# Component Principles

Every component must be:

- Reusable
- Responsive
- Accessible
- Configurable
- Well-documented
- Easy to maintain
- Production-ready

Avoid duplicate components.

---

# Folder Structure

```
components/

ui/
layout/
forms/
dashboard/
resume/
analysis/
jobs/
ai/
admin/
common/
```

---

# Component Naming

Use PascalCase.

Examples:

```
Navbar.jsx
Sidebar.jsx
Button.jsx
ResumeCard.jsx
UploadZone.jsx
AnalysisCard.jsx
ScoreChart.jsx
JobMatchCard.jsx
LoadingSpinner.jsx
```

---

# Component Structure

Each component should contain:

- UI
- Props
- Events
- Validation
- Loading State
- Error State
- Accessibility Support

---

# Required Components

## Layout

- Navbar
- Sidebar
- Footer
- PageContainer
- Section
- Hero
- DashboardLayout

---

## UI

- Button
- Card
- Badge
- Avatar
- Modal
- Drawer
- Tooltip
- Toast
- Skeleton
- Spinner
- Divider

---

## Forms

- Input
- Textarea
- Select
- Checkbox
- Radio
- Switch
- FileUpload
- SearchBox

---

## Resume

- ResumeCard
- ResumePreview
- UploadZone
- ResumeDetails
- ResumeHistory

---

## Analysis

- ATSScoreCard
- SkillsCard
- ExperienceCard
- KeywordAnalysis
- SuggestionsCard
- GrammarCard

---

## Dashboard

- StatsCard
- ActivityTimeline
- ScoreChart
- RecentUploads
- RecentReports

---

## Job Matching

- JobInput
- MatchCard
- MissingSkills
- MatchingSkills
- RecommendationCard

---

## AI

- AIChat
- PromptCard
- AIResponse
- CoverLetterPreview
- InterviewQuestionCard

---

## Admin

- UserTable
- AnalyticsChart
- LogViewer
- FileManager
- SystemStatus

---

# Component Standards

Every component should:

- Accept props
- Avoid hardcoded values
- Support dark mode
- Be responsive
- Support loading state
- Handle empty state
- Handle errors gracefully

---

# Props Guidelines

- Keep props minimal
- Use default values
- Validate required props
- Avoid unnecessary nesting

---

# State Management

Use:

- React Context
- Custom Hooks

Avoid unnecessary global state.

---

# Styling Rules

- Tailwind CSS only
- No inline styles
- No duplicate utility classes
- Shared styles through reusable components

---

# Icons

Use only:

```
lucide-react
```

Maintain consistent size and spacing.

---

# Accessibility

Each component must support:

- Keyboard navigation
- Focus states
- ARIA labels
- Semantic HTML
- Screen readers

---

# Performance

- Lazy load heavy components
- Memoize when appropriate
- Avoid unnecessary re-renders
- Optimize images
- Keep components lightweight

---

# Testing

Every major component should have:

- Render test
- Interaction test
- Accessibility test
- Responsive check

---

# Acceptance Criteria

A component is complete when:

- Reusable
- Responsive
- Accessible
- Documented
- Error-free
- Matches design system
- Tested successfully

---

# Agent Instructions

The AI coding agent must:

- Build reusable components only.
- Never duplicate component logic.
- Keep components small and focused.
- Follow the project's design system.
- Use composition over large monolithic components.
- Ensure every component supports loading, error, and empty states.
- Maintain consistent naming and folder structure.