# UI High-Fidelity Mockups for Atlas (ASC-024)

This document describes the high-fidelity mockups for the UI redesign of the Atlas application as part of ASC-024. These mockups build upon the wireframes, adding visual detail, color, typography, and interactive elements to refine the user experience for usability and accessibility.

## Table of Contents
- [Overview](#overview)
- [Design Tool and Process](#design-tool-and-process)
- [Main Navigation Mockup](#main-navigation-mockup)
- [Central Workspace Mockup](#central-workspace-mockup)
- [Task Creation Flow Mockup](#task-creation-flow-mockup)
- [Context-Aware Panels Mockup](#context-aware-panels-mockup)
- [Accessibility Features Mockup](#accessibility-features-mockup)
- [Next Steps](#next-steps)

## Overview

High-fidelity mockups provide a near-final representation of the Atlas UI, incorporating the feedback mechanisms, customizable themes, and layouts outlined in the UI Enhancement Strategy. These are textual descriptions simulating the output of a design tool like Figma or Sketch, which would be used in a real implementation for visual design.

## Design Tool and Process

- **Tool**: In a real scenario, these mockups would be created in Figma, allowing for collaborative feedback and interactive prototypes.
- **Process**:
  1. **Base on Wireframes**: Use the wireframes as a structural guide.
  2. **Apply Design System**: Incorporate Atlas's design system (colors, typography, icons).
  3. **Detail Interactions**: Define hover states, transitions, and micro-interactions.
  4. **User Feedback**: Simulate gathering feedback by outlining key review points.

## Main Navigation Mockup

**Mockup 1: Header and Sidebar**
- **Header Bar**:
  - Background: Gradient from deep blue (#1E3A8A) to light blue (#3B82F6).
  - Logo: Atlas logo in white, left-aligned, 40px height.
  - Navigation Tabs: White text, 16px Roboto, with active tab underlined in yellow (#F59E0B). Tabs include Home, Tasks, Chat, Plugins, Settings.
  - Search Bar: Right-aligned, white outline, placeholder text 'Search Atlas...' in italic.
- **Sidebar**:
  - Background: Dark navy (#1E293B), collapsible with a toggle icon (white chevron).
  - Sub-Navigation Items: Light gray text (#CBD5E1), 14px Roboto, hover state brightens to white. Active item highlighted with a yellow sidebar stripe.
  - Breadcrumb Trail: Below header, 12px Roboto, gray text (#718096) with '>' separators, clickable segments.

**Visual Elements**: Smooth gradient transitions in header, subtle shadow under header for depth, rounded corners on sidebar (8px radius).

**Purpose**: Provides a visually appealing, clear navigation structure with distinct active states for user orientation.

## Central Workspace Mockup

**Mockup 2: Main Content Area**
- **Content Area**:
  - Background: Light gray (#F7FAFC) for light theme, dark slate (#1A202C) for dark theme.
  - Layout: Responsive grid, 80% width in desktop view, adjusts to 100% on smaller screens.
  - Cards/Items: White (#FFFFFF) or dark gray (#2D3748) cards with 4px border radius, subtle drop shadow (0 2px 4px rgba(0,0,0,0.1)).
- **Contextual Toolbar**:
  - Position: Sticky at top of content area.
  - Buttons: Primary action in blue (#3B82F6), secondary in gray (#A0AEC0), 14px Roboto, hover state lightens by 10%.
  - Icons: Material Design icons, 20px, aligned left of button text.

**Visual Elements**: Smooth scrolling with momentum, fade-in animation for new content, hover tooltips on toolbar buttons (appear after 0.5s delay).

**Purpose**: Creates a focused workspace with visually distinct actionable elements.

## Task Creation Flow Mockup

**Mockup 3: Task Modal**
- **Modal Window**:
  - Background: White (#FFFFFF) or dark gray (#2D3748), 600px width, centered with overlay dimming background (rgba(0,0,0,0.5)).
  - Border: 1px light gray (#E2E8F0) or dark border (#4A5568), 8px radius.
  - Fields: Input fields with 1px border, 4px radius, focus state blue outline (#3B82F6).
  - Labels: 14px Roboto, dark gray (#4A5568) or light gray (#CBD5E1), left-aligned above fields.
- **Advanced Toggle**: Chevron icon, text 'Advanced Options', animates rotation on click.
- **AI Suggestions**: Small italic text below fields, green (#38A169), fades in when suggestion available.
- **Buttons**: 'Save' in blue (#3B82F6), 'Save & New' in outline blue, 'Cancel' in gray (#A0AEC0), all 14px Roboto.

**Visual Elements**: Smooth modal open/close animation (scale from 0.9 to 1.0), field validation errors in red (#E53E3E) with shake animation.

**Purpose**: Streamlines task creation with a clean, distraction-free interface and helpful AI prompts.

## Context-Aware Panels Mockup

**Mockup 4: Dynamic Side Panel**
- **Panel**:
  - Position: Right side, 300px width, collapsible with drag handle on left edge.
  - Background: Slightly lighter/darker than main content (e.g., #EDF2F7 or #1E293B).
  - Sections: Collapsible headers with chevron icons, 16px Roboto, bold.
  - Actions: Buttons or links in blue (#3B82F6), hover underline or lighten effect.
- **Drag-and-Drop**: Visual feedback with semi-transparent clone of dragged item, drop zones highlighted in dashed blue.

**Visual Elements**: Smooth slide-in/out animation for panel, subtle shadow on left edge for depth.

**Purpose**: Provides quick access to related actions without cluttering the main workspace.

## Accessibility Features Mockup

**Mockup 5: Accessibility Settings and Modes**
- **Settings Panel (Accessibility Tab)**:
  - Layout: Clean list with toggle switches and sliders.
  - High-Contrast Toggle: Switch with 'On' state in green (#38A169), preview thumbnail updates.
  - Text Size Slider: Range 12px-24px, live preview text below updates size.
- **High-Contrast Mode**:
  - Background: Black (#000000), text white (#FFFFFF), buttons bright yellow (#FFFF00).
  - Focus Indicators: 2px solid yellow border around focused elements, animated pulse effect.
- **Screen Reader Annotations**: Not visual, but mockup notes specify ARIA labels (e.g., 'Button: New Task, aria-label="Create a new task"').

**Visual Elements**: Immediate theme switch animation (0.3s fade), clear visual feedback on toggle states.

**Purpose**: Ensures users with disabilities can interact with Atlas effectively through customizable accessibility options.

## Next Steps

- **User Feedback**: Present these mockups to a sample user group for feedback on usability and aesthetics.
- **Iteration**: Refine designs based on feedback, focusing on areas of confusion or dissatisfaction.
- **Design System Integration**: Finalize the design system in code (CSS/QSS for PySide6) to match mockups.
- **Development Handoff**: Prepare detailed specs and assets for developers to implement the UI.

---

These high-fidelity mockup descriptions simulate the visual design phase of ASC-024. In a real project, these would be graphical designs created in a tool like Figma. If you have specific feedback or adjustments to these designs, please let me know before I proceed to simulate the feedback collection and iteration process.
