# 05 - UI Design System

> **Project:** AI Resume Analyzer & Job Match Platform
> **Version:** 1.0

---

# Purpose

This document defines the complete visual language for the application. Every page, component, and interaction must follow this design system to maintain a consistent, premium user experience.

---

# Design Philosophy

The UI should feel like a modern SaaS product built by a professional engineering team.

Inspired by:

- Linear
- Vercel
- Raycast
- Framer
- Apple
- Notion

Avoid:

- Bootstrap-style layouts
- Generic admin dashboards
- Bright colors
- Inconsistent spacing
- Heavy borders

---

# Design Style

- Premium SaaS
- Minimal
- Elegant
- Glassmorphism
- Responsive
- Clean
- Modern

---

# Color Palette

Use grayscale only.

```
Background        #050505
Surface           #111111
Glass             rgba(255,255,255,0.05)

Primary Text      #FFFFFF
Secondary Text    rgba(255,255,255,0.75)
Muted Text        rgba(255,255,255,0.55)

Success           #22c55e
Warning           #f59e0b
Error             #ef4444
```

No gradients for buttons unless explicitly defined.

---

# Typography

Primary Font

- Poppins

Accent Font

- Source Serif 4

Rules

- Large headings
- Medium font weight
- Comfortable line height
- Consistent typography scale

Example

```
Hero
56px

Section
36px

Card Title
22px

Body
16px

Caption
14px
```

---

# Spacing System

Use an 8px grid.

```
4
8
16
24
32
40
48
64
80
96
```

Never use random spacing values.

---

# Border Radius

```
Small      10px
Medium     16px
Large      24px
Hero        32px
Pill      999px
```

---

# Glassmorphism

All major cards use glass surfaces.

Properties

- Backdrop Blur
- Low Opacity
- Soft Shadow
- Transparent Background
- Rounded Corners

No visible borders unless required.

---

# Layout

Desktop

```
Sidebar

Content Area

Right Panel (optional)
```

Mobile

```
Top Navigation

Scrollable Content

Bottom Navigation
```

---

# Components

Every component must have:

- Hover State
- Active State
- Disabled State
- Loading State
- Error State
- Empty State

---

# Buttons

Variants

- Primary
- Secondary
- Glass
- Outline
- Ghost
- Danger

Rules

- Rounded corners
- Smooth hover animation
- Loading spinner support

---

# Cards

Cards must include

- Glass background
- Padding
- Rounded corners
- Hover elevation
- Soft shadow

---

# Forms

Use

- Floating labels (optional)
- Clear validation
- Helpful error messages
- Loading state
- Accessible inputs

---

# Icons

Library

```
lucide-react
```

Rules

- Consistent size
- Stroke width 2
- Minimal usage

---

# Animations

Use subtle motion only.

Allowed

- Fade
- Scale
- Slide
- Hover Lift
- Skeleton Loading
- Progress Animation

Avoid

- Bouncing
- Flashing
- Excessive movement

---

# Dashboard

Include

- Statistics Cards
- Charts
- Tables
- Activity Timeline
- Recent Reports

Dashboard must feel clean and spacious.

---

# Responsive Design

Breakpoints

```
Mobile

Tablet

Laptop

Desktop

Large Desktop
```

Every page must be mobile-first.

---

# Accessibility

Support

- Keyboard Navigation
- Screen Readers
- Focus Indicators
- High Contrast
- Proper Labels

---

# Dark Mode

Dark mode is the default theme.

Requirements

- Theme persistence
- Smooth transition
- Readable contrast
- Consistent colors

---

# Performance

- Lazy load images
- Lazy load routes
- Code splitting
- Optimized assets
- Skeleton loaders

---

# UI Quality Checklist

Before a page is complete:

- Responsive
- Accessible
- Consistent spacing
- Consistent typography
- Proper loading state
- Proper error state
- Proper empty state
- Smooth animations
- No overflow issues

---

# Agent Instructions

The AI coding agent must:

- Follow this design system for every page.
- Never create inconsistent layouts.
- Build reusable UI components.
- Use Tailwind CSS only.
- Use Lucide React icons.
- Follow the 8px spacing system.
- Maintain consistent typography.
- Ensure responsive behavior on all screen sizes.
- Keep animations subtle and performant.
- Prioritize clarity, accessibility, and a premium SaaS experience.